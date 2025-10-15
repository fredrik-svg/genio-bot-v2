"""
Grundkonfiguration för rpi-n8n-voice-assistant.
Fyll i värden via setup_wizard.py eller manuellt.
"""

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
MQTT_TLS = False

MQTT_TOPIC_COMMANDS = "rpi/commands/text"
MQTT_TOPIC_RESPONSES = "rpi/responses/text"
CLIENT_ID = "rpi-n8n-voice-assistant"

# Picovoice Porcupine (wakeword)
PORCUPINE_ACCESS_KEY = ""  # Fylls i via wizard
WAKEWORD_PATH = "models/wakewords/sv/assistans.ppn"  # Byt till din ppn

# Vosk (STT)
VOSK_MODEL_PATH = "models/vosk-model-sv"

# Piper (TTS)
PIPER_MODEL_PATH = "models/piper-sv"  # t.ex. 'sv-SE-xxx-low.onnx' och 'json' i denna mapp
PIPER_SPEAKER = None  # sätt till index/namn om modellen kräver

# Ljud
INPUT_DEVICE_INDEX = None  # None => default
OUTPUT_DEVICE_INDEX = None
SAMPLE_RATE = 16000
RECORD_SECONDS_AFTER_WAKE = 6  # enkel inspelningsfönster efter wakeword
LOG_LEVEL = "INFO"
