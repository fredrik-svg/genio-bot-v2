"""
Huvudapplikation för rpi-n8n-voice-assistant.

En röstassistent för Raspberry Pi med wakeword-detektering,
lokal STT/TTS och MQTT-kommunikation till n8n.
"""
import os
import sys
import json
import glob
import time
import signal
import logging
import threading
from typing import Optional

import numpy as np
from vosk import Model, KaldiRecognizer
import pvporcupine
from piper import PiperVoice
import pyaudio

import config
from mqtt_client import MqttClient
from audio_utils import AudioIO

# Konfigurera logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class VoiceAssistant:
    """
    Huvudklass för röstassistenten.
    
    Hanterar wakeword-detektering, STT, TTS och MQTT-kommunikation.
    """
    
    def __init__(self):
        """Initialisera röstassistenten med alla nödvändiga komponenter."""
        self.running = False
        self.audio: Optional[AudioIO] = None
        self.porcupine: Optional[pvporcupine.Porcupine] = None
        self.vosk_model: Optional[Model] = None
        self.piper: Optional[PiperVoice] = None
        self.mqtt: Optional[MqttClient] = None
        
        try:
            self._initialize()
        except Exception as e:
            logging.error(f"Initialisering misslyckades: {e}")
            self.cleanup()
            raise

    def _initialize(self) -> None:
        """Initialisera alla komponenter."""
        logging.info("Startar initialisering av röstassistent...")
        
        # Validera konfiguration
        self._validate_config()
        
        # Ljud
        try:
            self.audio = AudioIO(
                sample_rate=config.SAMPLE_RATE,
                input_device_index=config.INPUT_DEVICE_INDEX,
                output_device_index=config.OUTPUT_DEVICE_INDEX
            )
            logging.info("✓ Ljudhantering initialiserad")
        except Exception as e:
            raise RuntimeError(f"Kunde inte initialisera ljudhantering: {e}")

        # Wakeword (Porcupine)
        try:
            if not config.PORCUPINE_ACCESS_KEY:
                raise ValueError("PORCUPINE_ACCESS_KEY saknas (kör setup_wizard.py eller sätt .env)")
            if not os.path.exists(config.WAKEWORD_PATH):
                raise FileNotFoundError(f"Wakeword-fil saknas: {config.WAKEWORD_PATH}")
                
            self.porcupine = pvporcupine.create(
                access_key=config.PORCUPINE_ACCESS_KEY,
                keyword_paths=[config.WAKEWORD_PATH],
                sensitivities=[0.6]
            )
            logging.info(f"✓ Wakeword-detektering initialiserad: {config.WAKEWORD_PATH}")
        except Exception as e:
            raise RuntimeError(f"Kunde inte initialisera Porcupine: {e}")

        # STT (Vosk)
        try:
            if not os.path.isdir(config.VOSK_MODEL_PATH):
                raise FileNotFoundError(f"Vosk-modellen hittas inte: {config.VOSK_MODEL_PATH}")
                
            logging.info("Laddar Vosk-modell (kan ta några sekunder)...")
            self.vosk_model = Model(config.VOSK_MODEL_PATH)
            logging.info("✓ Speech-to-Text (Vosk) initialiserad")
        except Exception as e:
            raise RuntimeError(f"Kunde inte initialisera Vosk: {e}")

        # TTS (Piper)
        try:
            # Support both directory and file paths for PIPER_MODEL_PATH
            piper_model_file = None
            
            if os.path.isfile(config.PIPER_MODEL_PATH):
                # Direct path to .onnx file
                piper_model_file = config.PIPER_MODEL_PATH
            elif os.path.isdir(config.PIPER_MODEL_PATH):
                # Directory path - find the .onnx file
                onnx_files = sorted(glob.glob(os.path.join(config.PIPER_MODEL_PATH, "*.onnx")))
                if onnx_files:
                    piper_model_file = onnx_files[0]
                    logging.info(f"Hittade Piper-modell: {os.path.basename(piper_model_file)}")
                else:
                    raise FileNotFoundError(
                        f"Ingen .onnx-fil hittades i katalogen: {config.PIPER_MODEL_PATH}\n"
                        f"Ladda ner en Piper-modell från https://github.com/rhasspy/piper#voices"
                    )
            else:
                raise FileNotFoundError(
                    f"Piper-modellen hittas inte: {config.PIPER_MODEL_PATH}\n"
                    f"Ange antingen en sökväg till en .onnx-fil eller en katalog som innehåller en."
                )
                
            logging.info("Laddar Piper-modell (kan ta några sekunder)...")
            self.piper = PiperVoice.load(piper_model_file)
            logging.info("✓ Text-to-Speech (Piper) initialiserad")
        except Exception as e:
            raise RuntimeError(f"Kunde inte initialisera Piper: {e}")

        # MQTT
        try:
            self.mqtt = MqttClient(
                config.MQTT_HOST,
                config.MQTT_PORT,
                config.MQTT_USERNAME,
                config.MQTT_PASSWORD,
                tls=config.MQTT_TLS,
                client_id=config.CLIENT_ID,
                on_message=self.on_mqtt_message
            )
            
            if not self.mqtt.connect(
                retries=config.MQTT_MAX_RETRIES,
                timeout=config.MQTT_CONNECT_TIMEOUT
            ):
                raise ConnectionError("Kunde inte ansluta till MQTT-broker")
                
            self.mqtt.loop_start()
            self.mqtt.subscribe(config.MQTT_TOPIC_RESPONSES)
            logging.info("✓ MQTT-kommunikation initialiserad")
        except Exception as e:
            raise RuntimeError(f"Kunde inte initialisera MQTT: {e}")

        self.running = True
        logging.info("✓ Initialisering klar!")

    def _validate_config(self) -> None:
        """Validera kritiska konfigurationsinställningar."""
        if not config.MQTT_HOST:
            raise ValueError("MQTT_HOST måste anges")
        if not 1 <= config.MQTT_PORT <= 65535:
            raise ValueError(f"Ogiltig MQTT_PORT: {config.MQTT_PORT}")
        if config.SAMPLE_RATE <= 0:
            raise ValueError(f"Ogiltig SAMPLE_RATE: {config.SAMPLE_RATE}")
        if config.RECORD_SECONDS_AFTER_WAKE <= 0:
            raise ValueError(f"Ogiltig RECORD_SECONDS_AFTER_WAKE: {config.RECORD_SECONDS_AFTER_WAKE}")

    def on_mqtt_message(self, topic: str, data: dict) -> None:
        """
        Hantera inkommande MQTT-meddelanden från n8n.
        
        Args:
            topic: MQTT topic
            data: JSON data som dict
        """
        try:
            if topic == config.MQTT_TOPIC_RESPONSES:
                tts_text = data.get("tts_text") if isinstance(data, dict) else None
                
                if not tts_text:
                    logging.warning("TTS-svar utan 'tts_text' fält")
                    return
                    
                # Säkerhet: Validera textstorlek
                if len(tts_text) > config.MAX_TEXT_LENGTH:
                    logging.warning(f"TTS-text för lång ({len(tts_text)} tecken), klipper av")
                    tts_text = tts_text[:config.MAX_TEXT_LENGTH]
                
                logging.info(f"TTS-svar mottaget ({len(tts_text)} tecken). Läser upp...")
                
                try:
                    pcm = self.piper.synthesize(
                        tts_text,
                        rate=1.0,
                        volume=1.0,
                        length_scale=1.0,
                        speaker=config.PIPER_SPEAKER
                    )
                    self.audio.play_pcm(np.frombuffer(pcm, dtype=np.int16))
                except Exception as e:
                    logging.error(f"TTS-syntes misslyckades: {e}")
        except Exception as e:
            logging.exception(f"Fel vid hantering av MQTT-meddelande: {e}")

    def listen_for_wake(self) -> None:
        """
        Huvudloop: Lyssna efter wakeword och hantera röstkommandon.
        
        När wakeword detekteras:
        1. Spela feedback-ljud
        2. Spela in användarens kommando
        3. Transkribera med Vosk
        4. Skicka till n8n via MQTT
        5. Spela feedback-ljud
        """
        stream = None
        
        try:
            pa = self.audio.pa
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=config.SAMPLE_RATE,
                input=True,
                frames_per_buffer=512
            )
            
            logging.info("Lyssnar efter wakeword... (Tryck Ctrl+C för att avsluta)")

            while self.running:
                try:
                    data = stream.read(512, exception_on_overflow=False)
                    pcm = np.frombuffer(data, dtype=np.int16)
                    result = self.porcupine.process(pcm)
                    
                    if result >= 0:
                        logging.info("🎤 Wakeword detekterat!")
                        self._handle_voice_command()
                        
                except Exception as e:
                    logging.error(f"Fel i wakeword-loop: {e}")
                    time.sleep(0.1)  # Undvik tight loop vid fel
                    
        except KeyboardInterrupt:
            logging.info("Avbruten av användare")
        except Exception as e:
            logging.exception(f"Kritiskt fel i listen_for_wake: {e}")
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logging.error(f"Fel vid stängning av wakeword-ström: {e}")

    def _handle_voice_command(self) -> None:
        """Hantera detekterat röstkommando."""
        try:
            # Ljudsignal: start
            self.audio.play_wav("audio_feedback/start_listen.wav")

            # Spela in tal
            logging.info("Spelar in...")
            audio = self.audio.record(config.RECORD_SECONDS_AFTER_WAKE)

            # STT med Vosk
            logging.info("Transkriberar...")
            rec = KaldiRecognizer(self.vosk_model, config.SAMPLE_RATE)
            rec.AcceptWaveform(audio.tobytes())
            stt_json = json.loads(rec.Result())
            text = stt_json.get("text", "").strip()
            
            logging.info(f"📝 Transkriberat: '{text}'")

            # Skicka till n8n via MQTT
            if text:
                # Säkerhet: Validera textstorlek
                if len(text) > config.MAX_TEXT_LENGTH:
                    logging.warning(f"Text för lång ({len(text)} tecken), klipper av")
                    text = text[:config.MAX_TEXT_LENGTH]
                    
                success = self.mqtt.publish_json(
                    config.MQTT_TOPIC_COMMANDS,
                    {"text": text, "timestamp": time.time()}
                )
                
                if success:
                    logging.info("✓ Kommando skickat till n8n")
                else:
                    logging.error("✗ Kunde inte skicka kommando till n8n")
            else:
                logging.info("Ingen text detekterad")

            # Ljudsignal: slut
            self.audio.play_wav("audio_feedback/end_listen.wav")
            
        except Exception as e:
            logging.exception(f"Fel vid hantering av röstkommando: {e}")

    def cleanup(self) -> None:
        """Frigör alla resurser på ett säkert sätt."""
        logging.info("Rensar upp resurser...")
        
        self.running = False
        
        # Stäng MQTT
        if self.mqtt:
            try:
                self.mqtt.loop_stop()
                self.mqtt.disconnect()
            except Exception as e:
                logging.error(f"Fel vid stängning av MQTT: {e}")
        
        # Stäng Porcupine
        if self.porcupine:
            try:
                self.porcupine.delete()
            except Exception as e:
                logging.error(f"Fel vid stängning av Porcupine: {e}")
        
        # Stäng audio
        if self.audio:
            try:
                self.audio.cleanup()
            except Exception as e:
                logging.error(f"Fel vid stängning av audio: {e}")
        
        logging.info("Cleanup klar")

    def stop(self) -> None:
        """Stoppa röstassistenten."""
        self.running = False

def main():
    """Huvudfunktion för att starta röstassistenten."""
    va: Optional[VoiceAssistant] = None
    
    def handle_signal(sig, frame):
        """Hantera signal för graceful shutdown."""
        logging.info("\n🛑 Avslutar...")
        if va:
            va.stop()
            va.cleanup()
        sys.exit(0)

    # Registrera signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        # Starta röstassistent
        logging.info("=" * 60)
        logging.info("  RPI-N8N Voice Assistant v2")
        logging.info("=" * 60)
        
        va = VoiceAssistant()
        va.listen_for_wake()
        
    except KeyboardInterrupt:
        logging.info("\nAvbruten av användare")
    except Exception as e:
        logging.exception(f"Kritiskt fel: {e}")
        sys.exit(1)
    finally:
        if va:
            va.cleanup()

if __name__ == "__main__":
    main()
