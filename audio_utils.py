"""
Ljudhantering med förbättrad resurshantering och felhantering.
"""
import io
import time
import wave
import logging
from typing import Optional
import numpy as np
import pyaudio
import soundfile as sf
import os

class AudioError(Exception):
    """Bas exception för ljud-relaterade fel."""
    pass

class AudioIO:
    """
    Hanterar ljudinspelning och uppspelning med PyAudio.
    
    Inkluderar automatisk resurshantering och robust felhantering.
    """
    
    def __init__(self, sample_rate: int = 16000, 
                 input_device_index: Optional[int] = None, 
                 output_device_index: Optional[int] = None,
                 max_record_seconds: int = 30,
                 stream_stabilize_delay: float = 0.1):
        """
        Initialisera ljudhantering.
        
        Args:
            sample_rate: Samplingsfrekvens i Hz
            input_device_index: Index för ingångsenhet (None = default)
            output_device_index: Index för utgångsenhet (None = default)
            max_record_seconds: Max inspelningstid (säkerhet)
            stream_stabilize_delay: Fördröjning efter att stream öppnats (sekunder)
        """
        if sample_rate <= 0:
            raise ValueError(f"Ogiltig sample rate: {sample_rate}")
        if max_record_seconds <= 0:
            raise ValueError(f"Ogiltig max_record_seconds: {max_record_seconds}")
            
        self.sample_rate = sample_rate
        self.input_device_index = input_device_index
        self.output_device_index = output_device_index
        self.max_record_seconds = max_record_seconds
        self.stream_stabilize_delay = stream_stabilize_delay
        
        try:
            self.pa = pyaudio.PyAudio()
            logging.info(f"PyAudio initialiserad (sample rate: {sample_rate} Hz)")
        except Exception as e:
            raise AudioError(f"Kunde inte initialisera PyAudio: {e}")

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup vid context manager exit."""
        self.cleanup()

    def cleanup(self) -> None:
        """Frigör PyAudio-resurser."""
        try:
            if hasattr(self, 'pa'):
                self.pa.terminate()
                logging.debug("PyAudio resurs frigjord")
        except Exception as e:
            logging.error(f"Fel vid cleanup av PyAudio: {e}")

    def record(self, seconds: float) -> np.ndarray:
        """
        Spela in ljud under angiven tid.
        
        Args:
            seconds: Inspelningstid i sekunder
            
        Returns:
            NumPy array med PCM audio data
            
        Raises:
            AudioError: Om inspelning misslyckas
            ValueError: Om seconds är ogiltig
        """
        if seconds <= 0:
            raise ValueError(f"Inspelningstid måste vara positiv: {seconds}")
        if seconds > self.max_record_seconds:
            raise ValueError(f"Inspelningstid ({seconds}s) överstiger max ({self.max_record_seconds}s)")
            
        channels = 1
        format = pyaudio.paInt16
        chunk = 1024
        stream = None
        
        try:
            stream = self.pa.open(
                format=format,
                channels=channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=chunk,
                input_device_index=self.input_device_index
            )
            
            # Kort paus för att låta ljudströmmen stabiliseras
            # Detta förhindrar att första chunks innehåller brus eller ofullständig data
            time.sleep(self.stream_stabilize_delay)
            
            frames = []
            num_chunks = int(self.sample_rate / chunk * seconds)
            
            for _ in range(num_chunks):
                try:
                    data = stream.read(chunk, exception_on_overflow=False)
                    frames.append(np.frombuffer(data, dtype=np.int16))
                except Exception as e:
                    logging.warning(f"Fel vid läsning av ljudchunk: {e}")
                    continue
                    
            if not frames:
                raise AudioError("Ingen ljuddata inspelad")
                
            audio = np.concatenate(frames)
            logging.debug(f"Inspelning klar: {len(audio)} samples")
            return audio
            
        except Exception as e:
            raise AudioError(f"Inspelning misslyckades: {e}")
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logging.error(f"Fel vid stängning av inspelningsström: {e}")

    def play_wav(self, path: str) -> bool:
        """
        Spela upp WAV-fil.
        
        Args:
            path: Sökväg till WAV-fil
            
        Returns:
            True om uppspelning lyckades
        """
        if not os.path.exists(path):
            logging.warning(f"WAV-fil hittas inte: {path}")
            return False
            
        if not os.path.isfile(path):
            logging.warning(f"Sökvägen är inte en fil: {path}")
            return False
            
        stream = None
        try:
            data, sr = sf.read(path, dtype='int16')
            
            if sr != self.sample_rate:
                logging.debug(f"WAV sample rate {sr} != expected {self.sample_rate}, spelar ändå")
            
            # Hantera stereo till mono
            if len(data.shape) > 1:
                data = np.mean(data, axis=1).astype(np.int16)
                
            stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sr,
                output=True,
                output_device_index=self.output_device_index
            )
            
            stream.write(data.tobytes())
            logging.debug(f"WAV uppspelning klar: {path}")
            return True
            
        except Exception as e:
            logging.error(f"Fel vid uppspelning av WAV {path}: {e}")
            return False
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logging.error(f"Fel vid stängning av uppspelningsström: {e}")

    def play_pcm(self, pcm: np.ndarray) -> bool:
        """
        Spela upp PCM audio data.
        
        Args:
            pcm: NumPy array med PCM data
            
        Returns:
            True om uppspelning lyckades
        """
        if not isinstance(pcm, np.ndarray):
            logging.error("PCM data måste vara NumPy array")
            return False
            
        if len(pcm) == 0:
            logging.warning("Tom PCM data, hoppar över uppspelning")
            return False
            
        stream = None
        try:
            stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True,
                output_device_index=self.output_device_index
            )
            
            stream.write(pcm.astype(np.int16).tobytes())
            logging.debug(f"PCM uppspelning klar: {len(pcm)} samples")
            return True
            
        except Exception as e:
            logging.error(f"Fel vid uppspelning av PCM: {e}")
            return False
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logging.error(f"Fel vid stängning av PCM-ström: {e}")
    
    def list_devices(self) -> None:
        """Visa tillgängliga ljudenheter (för debugging)."""
        try:
            info = self.pa.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            logging.info("Tillgängliga ljudenheter:")
            for i in range(num_devices):
                device_info = self.pa.get_device_info_by_host_api_device_index(0, i)
                logging.info(f"  [{i}] {device_info.get('name')}: "
                           f"in={device_info.get('maxInputChannels')}, "
                           f"out={device_info.get('maxOutputChannels')}")
        except Exception as e:
            logging.error(f"Kunde inte lista ljudenheter: {e}")
