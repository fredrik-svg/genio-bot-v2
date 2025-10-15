import os
import sys
import json
import time
import queue
import signal
import logging
import threading

import numpy as np
from vosk import Model, KaldiRecognizer
import pvporcupine
from piper import PiperVoice

import config
from mqtt_client import MqttClient
from audio_utils import AudioIO

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
                    format="%(asctime)s %(levelname)s %(message)s")

class VoiceAssistant:
    def __init__(self):
        self.audio = AudioIO(sample_rate=config.SAMPLE_RATE,
                             input_device_index=config.INPUT_DEVICE_INDEX,
                             output_device_index=config.OUTPUT_DEVICE_INDEX)

        # Wakeword (Porcupine)
        if not config.PORCUPINE_ACCESS_KEY:
            logging.error("PORCUPINE_ACCESS_KEY saknas i config.py (kör setup_wizard.py).")
            sys.exit(1)
        if not os.path.exists(config.WAKEWORD_PATH):
            logging.error(f"Wakeword-fil saknas: {config.WAKEWORD_PATH}")
            sys.exit(1)
        self.porcupine = pvporcupine.create(access_key=config.PORCUPINE_ACCESS_KEY,
                                            keyword_paths=[config.WAKEWORD_PATH],
                                            sensitivities=[0.6])

        # STT (Vosk)
        if not os.path.isdir(config.VOSK_MODEL_PATH):
            logging.error(f"Vosk-modellen hittas inte: {config.VOSK_MODEL_PATH}")
            sys.exit(1)
        self.vosk_model = Model(config.VOSK_MODEL_PATH)

        # TTS (Piper)
        if not os.path.isdir(config.PIPER_MODEL_PATH):
            logging.error(f"Piper-modellen hittas inte: {config.PIPER_MODEL_PATH}")
            sys.exit(1)
        self.piper = PiperVoice.load(config.PIPER_MODEL_PATH)

        # MQTT
        self.mqtt = MqttClient(config.MQTT_HOST, config.MQTT_PORT, config.MQTT_USERNAME, config.MQTT_PASSWORD,
                               tls=config.MQTT_TLS, client_id=config.CLIENT_ID, on_message=self.on_mqtt_message)
        if not self.mqtt.connect():
            logging.error("Kunde inte ansluta till MQTT-broker.")
            sys.exit(1)
        self.mqtt.loop_start()
        self.mqtt.subscribe(config.MQTT_TOPIC_RESPONSES)

        self.running = True

    def on_mqtt_message(self, topic, data):
        if topic == config.MQTT_TOPIC_RESPONSES:
            tts_text = data.get("tts_text") if isinstance(data, dict) else None
            if tts_text:
                logging.info(f"TTS-svar mottaget ({len(tts_text)} tecken). Läser upp...")
                pcm = self.piper.synthesize(tts_text, rate=1.0, volume=1.0, length_scale=1.0, speaker=config.PIPER_SPEAKER)
                self.audio.play_pcm(np.frombuffer(pcm, dtype=np.int16))

    def listen_for_wake(self):
        """
        Enkel loop: lyssna efter wakeword i realtid i block, spela upp 'start_listen', spela in ett fönster,
        transkribera och skicka till n8n, spela upp 'end_listen'.
        """
        import pyaudio
        pa = self.audio.pa
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=config.SAMPLE_RATE, input=True, frames_per_buffer=512)

        try:
            while self.running:
                data = stream.read(512, exception_on_overflow=False)
                pcm = np.frombuffer(data, dtype=np.int16)
                result = self.porcupine.process(pcm)
                if result >= 0:
                    logging.info("Wakeword detekterat.")
                    # Ljudsignal: start
                    self.audio.play_wav("audio_feedback/start_listen.wav")

                    # Spela in tal i fast fönster
                    audio = self.audio.record(config.RECORD_SECONDS_AFTER_WAKE)

                    # STT
                    rec = KaldiRecognizer(self.vosk_model, config.SAMPLE_RATE)
                    rec.AcceptWaveform(audio.tobytes())
                    stt_json = json.loads(rec.Result())
                    text = stt_json.get("text", "").strip()
                    logging.info(f"Transkriberat: {text!r}")

                    if text:
                        self.mqtt.publish_json(config.MQTT_TOPIC_COMMANDS, {"text": text})
                    else:
                        logging.info("Ingen text att skicka.")

                    # Ljudsignal: slut
                    self.audio.play_wav("audio_feedback/end_listen.wav")
        finally:
            stream.stop_stream()
            stream.close()

    def stop(self):
        self.running = False
        try:
            self.mqtt.loop_stop()
        except Exception:
            pass

def main():
    va = VoiceAssistant()

    def handle_sigint(sig, frame):
        logging.info("Avslutar...")
        va.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)
    logging.info("Klart. Lyssnar efter wakeword... (Ctrl+C för att avsluta)")
    va.listen_for_wake()

if __name__ == "__main__":
    main()
