import os
import json
import pathlib

CONFIG_FILE = "config.py"

TEMPLATE = """\"\"\"
Auto-genererad av setup_wizard.py
\"\"\"

MQTT_HOST = "{MQTT_HOST}"
MQTT_PORT = {MQTT_PORT}
MQTT_USERNAME = "{MQTT_USERNAME}"
MQTT_PASSWORD = "{MQTT_PASSWORD}"
MQTT_TLS = {MQTT_TLS}

MQTT_TOPIC_COMMANDS = "{MQTT_TOPIC_COMMANDS}"
MQTT_TOPIC_RESPONSES = "{MQTT_TOPIC_RESPONSES}"
CLIENT_ID = "{CLIENT_ID}"

PORCUPINE_ACCESS_KEY = "{PORCUPINE_ACCESS_KEY}"
WAKEWORD_PATH = "{WAKEWORD_PATH}"

VOSK_MODEL_PATH = "{VOSK_MODEL_PATH}"
PIPER_MODEL_PATH = "{PIPER_MODEL_PATH}"
PIPER_SPEAKER = {PIPER_SPEAKER}

INPUT_DEVICE_INDEX = {INPUT_DEVICE_INDEX}
OUTPUT_DEVICE_INDEX = {OUTPUT_DEVICE_INDEX}
SAMPLE_RATE = {SAMPLE_RATE}
RECORD_SECONDS_AFTER_WAKE = {RECORD_SECONDS_AFTER_WAKE}
LOG_LEVEL = "{LOG_LEVEL}"
"""

def ask(prompt, default=None, cast=str):
    raw = input(f"{prompt} [{default}]: ") if default is not None else input(f"{prompt}: ")
    if not raw and default is not None:
        return default
    return cast(raw)

def main():
    print("=== rpi-n8n-voice-assistant Setup Wizard ===")

    # Ensure folders
    pathlib.Path("models/wakewords/sv").mkdir(parents=True, exist_ok=True)
    pathlib.Path("models/vosk-model-sv").mkdir(parents=True, exist_ok=True)
    pathlib.Path("models/piper-sv").mkdir(parents=True, exist_ok=True)
    pathlib.Path("audio_feedback").mkdir(parents=True, exist_ok=True)

    print("\nLägg dina modeller här efter nedladdning:")
    print(" - Vosk (svenska): models/vosk-model-sv/")
    print(" - Piper (svenska): models/piper-sv/ (onnx + .json)")
    print(" - Porcupine wakeword .ppn: models/wakewords/sv/assistans.ppn (eller annat filnamn)")

    # Config questions
    cfg = {}
    cfg["MQTT_HOST"] = ask("MQTT host", "localhost")
    cfg["MQTT_PORT"] = ask("MQTT port", 1883, int)
    cfg["MQTT_USERNAME"] = ask("MQTT username", "")
    cfg["MQTT_PASSWORD"] = ask("MQTT password", "")
    cfg["MQTT_TLS"] = ask("Use TLS? true/false", "false").lower() == "true"

    cfg["MQTT_TOPIC_COMMANDS"] = ask("Commands topic", "rpi/commands/text")
    cfg["MQTT_TOPIC_RESPONSES"] = ask("Responses topic", "rpi/responses/text")
    cfg["CLIENT_ID"] = ask("MQTT client id", "rpi-n8n-voice-assistant")

    cfg["PORCUPINE_ACCESS_KEY"] = ask("Picovoice Access Key", "")
    cfg["WAKEWORD_PATH"] = ask("Wakeword path", "models/wakewords/sv/assistans.ppn")

    cfg["VOSK_MODEL_PATH"] = ask("Vosk model path", "models/vosk-model-sv")
    cfg["PIPER_MODEL_PATH"] = ask("Piper model path", "models/piper-sv")
    speaker = ask("Piper speaker (tom = None)", "")
    cfg["PIPER_SPEAKER"] = "None" if speaker.strip() == "" else repr(speaker.strip())

    inp = ask("Input device index (tom = None)", "")
    outp = ask("Output device index (tom = None)", "")
    cfg["INPUT_DEVICE_INDEX"] = "None" if inp.strip() == "" else int(inp)
    cfg["OUTPUT_DEVICE_INDEX"] = "None" if outp.strip() == "" else int(outp)
    cfg["SAMPLE_RATE"] = ask("Sample rate", 16000, int)
    cfg["RECORD_SECONDS_AFTER_WAKE"] = ask("Record seconds after wake", 6, int)
    cfg["LOG_LEVEL"] = ask("Log level", "INFO")

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(**cfg))

    print(f"\nSkrev {CONFIG_FILE}.")
    print("\n== Modellnedladdning (manuellt) ==")
    print("Vosk svenskt språk: https://alphacephei.com/vosk/models (svenska). Packa upp i models/vosk-model-sv/.")
    print("Piper svenska röster: https://github.com/rhasspy/piper#voices. Lägg .onnx + .json i models/piper-sv/.")
    print("Porcupine: https://picovoice.ai/platform/porcupine/ (få access key & .ppn).")
    print("\nKlar. Kör sedan: python3 main.py")

if __name__ == "__main__":
    main()
