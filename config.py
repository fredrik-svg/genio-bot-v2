"""
Grundkonfiguration för rpi-n8n-voice-assistant.
Stödjer både .env-filer och miljövariabler för bättre säkerhet.
"""
import os
from dotenv import load_dotenv

# Ladda .env-fil om den finns
load_dotenv()

def get_env_bool(key: str, default: bool = False) -> bool:
    """Konvertera strängvärde från miljövariabel till boolean."""
    val = os.getenv(key, str(default))
    return val.lower() in ('true', '1', 'yes', 'on')

def get_env_int(key: str, default: int) -> int:
    """Hämta integer från miljövariabel med fallback till default."""
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return default

# MQTT Configuration
# Using HiveMQ Cloud - no local MQTT broker needed
# Get credentials from https://console.hivemq.cloud/
MQTT_HOST = os.getenv("MQTT_HOST", "")  # No default - must be configured
MQTT_PORT = get_env_int("MQTT_PORT", 8883)  # HiveMQ Cloud TLS port
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TLS = get_env_bool("MQTT_TLS", True)  # HiveMQ Cloud requires TLS

MQTT_TOPIC_COMMANDS = os.getenv("MQTT_TOPIC_COMMANDS", "rpi/commands/text")
MQTT_TOPIC_RESPONSES = os.getenv("MQTT_TOPIC_RESPONSES", "rpi/responses/text")
CLIENT_ID = os.getenv("CLIENT_ID", "rpi-n8n-voice-assistant")

# Picovoice Porcupine (wakeword)
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY", "")
WAKEWORD_PATH = os.getenv("WAKEWORD_PATH", "models/wakewords/sv/assistans.ppn")

# Vosk (STT)
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-sv")

# Piper (TTS)
PIPER_MODEL_PATH = os.getenv("PIPER_MODEL_PATH", "models/piper-sv")
_speaker = os.getenv("PIPER_SPEAKER", "")
PIPER_SPEAKER = None if _speaker == "" else _speaker

# Ljud
_input_dev = os.getenv("INPUT_DEVICE_INDEX", "")
_output_dev = os.getenv("OUTPUT_DEVICE_INDEX", "")
INPUT_DEVICE_INDEX = None if _input_dev == "" else int(_input_dev)
OUTPUT_DEVICE_INDEX = None if _output_dev == "" else int(_output_dev)

SAMPLE_RATE = get_env_int("SAMPLE_RATE", 16000)
RECORD_SECONDS_AFTER_WAKE = get_env_int("RECORD_SECONDS_AFTER_WAKE", 6)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Timeout och säkerhet
MQTT_CONNECT_TIMEOUT = get_env_int("MQTT_CONNECT_TIMEOUT", 10)
MQTT_MAX_RETRIES = get_env_int("MQTT_MAX_RETRIES", 5)
MAX_TEXT_LENGTH = get_env_int("MAX_TEXT_LENGTH", 1000)  # Begränsa input-längd
