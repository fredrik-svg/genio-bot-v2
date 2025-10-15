import io
import time
import wave
import logging
from typing import Optional
import numpy as np
import pyaudio
import soundfile as sf
import os

class AudioIO:
    def __init__(self, sample_rate: int = 16000, input_device_index: Optional[int]=None, output_device_index: Optional[int]=None):
        self.sample_rate = sample_rate
        self.pa = pyaudio.PyAudio()
        self.input_device_index = input_device_index
        self.output_device_index = output_device_index

    def record(self, seconds: float) -> np.ndarray:
        channels = 1
        format = pyaudio.paInt16
        chunk = 1024
        stream = self.pa.open(format=format, channels=channels, rate=self.sample_rate,
                              input=True, frames_per_buffer=chunk, input_device_index=self.input_device_index)
        frames = []
        try:
            for _ in range(int(self.sample_rate / chunk * seconds)):
                data = stream.read(chunk, exception_on_overflow=False)
                frames.append(np.frombuffer(data, dtype=np.int16))
        finally:
            stream.stop_stream()
            stream.close()
        audio = np.concatenate(frames)
        return audio

    def play_wav(self, path: str):
        if not os.path.exists(path):
            logging.warning(f"WAV not found: {path}")
            return
        data, sr = sf.read(path, dtype='int16')
        if sr != self.sample_rate:
            logging.warning(f"WAV sample rate {sr} != expected {self.sample_rate}, playing anyway.")
        stream = self.pa.open(format=pyaudio.paInt16, channels=1, rate=sr, output=True, output_device_index=self.output_device_index)
        try:
            stream.write(data.tobytes())
        finally:
            stream.stop_stream()
            stream.close()

    def play_pcm(self, pcm: np.ndarray):
        stream = self.pa.open(format=pyaudio.paInt16, channels=1, rate=self.sample_rate, output=True, output_device_index=self.output_device_index)
        try:
            stream.write(pcm.astype(np.int16).tobytes())
        finally:
            stream.stop_stream()
            stream.close()
