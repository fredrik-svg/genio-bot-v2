"""
Setup wizard för rpi-n8n-voice-assistant.

Guidar användaren genom initial konfiguration och skapar .env-fil.
"""
import os
import sys
import pathlib
from typing import Optional, Callable

ENV_FILE = ".env"

def ask(prompt: str, default: Optional[str] = None, 
        validator: Optional[Callable[[str], bool]] = None,
        error_msg: str = "Ogiltigt värde, försök igen") -> str:
    """
    Ställ fråga till användaren med valfri validering.
    
    Args:
        prompt: Fråga att visa
        default: Standardvärde (None = obligatoriskt)
        validator: Valideringsfunktion
        error_msg: Felmeddelande vid ogiltig input
        
    Returns:
        Användarsvar eller default
    """
    while True:
        if default is not None:
            display_default = default if default != "" else "(tom)"
            user_input = input(f"{prompt} [{display_default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
            if not user_input:
                print("⚠️  Detta fält är obligatoriskt")
                continue
        
        # Validera om validator finns
        if validator and not validator(user_input):
            print(f"⚠️  {error_msg}")
            continue
            
        return user_input

def validate_port(value: str) -> bool:
    """Validera att port är giltigt nummer."""
    try:
        port = int(value)
        return 1 <= port <= 65535
    except ValueError:
        return False

def validate_sample_rate(value: str) -> bool:
    """Validera sample rate."""
    try:
        rate = int(value)
        return rate > 0
    except ValueError:
        return False

def validate_seconds(value: str) -> bool:
    """Validera sekunder."""
    try:
        seconds = int(value)
        return 0 < seconds <= 60
    except ValueError:
        return False

def strip_mqtt_protocol(url: str) -> str:
    """
    Ta bort MQTT-protokollprefix från URL om det finns.
    
    Args:
        url: URL som kan innehålla mqtt://, mqtts://, ws://, eller wss://
        
    Returns:
        URL utan protokollprefix och utan port
    """
    url = url.strip()
    
    # Ta bort vanliga MQTT-protokoll
    protocols = ['mqtts://', 'mqtt://', 'wss://', 'ws://', 'https://', 'http://']
    for protocol in protocols:
        if url.lower().startswith(protocol):
            url = url[len(protocol):]
            break
    
    # Ta bort port om den finns i slutet (t.ex. :8883 eller :8884)
    if ':' in url:
        url = url.split(':')[0]
    
    # Ta bort trailing path om det finns (t.ex. /mqtt)
    if '/' in url:
        url = url.split('/')[0]
    
    return url

def main():
    """Huvudfunktion för setup wizard."""
    print("=" * 70)
    print("  🤖 RPI-N8N Voice Assistant - Setup Wizard")
    print("=" * 70)
    print("\nDenna guide hjälper dig att konfigurera din röstassistent.")
    print("Tryck Enter för att acceptera standardvärden [inom hakparenteser].\n")

    # Skapa nödvändiga mappar
    print("📁 Skapar mappar...")
    try:
        pathlib.Path("models/wakewords/sv").mkdir(parents=True, exist_ok=True)
        pathlib.Path("models/vosk-model-sv").mkdir(parents=True, exist_ok=True)
        pathlib.Path("models/piper-sv").mkdir(parents=True, exist_ok=True)
        pathlib.Path("audio_feedback").mkdir(parents=True, exist_ok=True)
        print("✓ Mappar skapade")
    except Exception as e:
        print(f"⚠️  Varning: Kunde inte skapa mappar: {e}")

    print("\n" + "─" * 70)
    print("📥 VIKTIGT: Ladda ner modeller manuellt")
    print("─" * 70)
    print("Lägg dina modeller här efter nedladdning:")
    print("  • Vosk (svenska STT): models/vosk-model-sv/")
    print("    → https://alphacephei.com/vosk/models")
    print("  • Piper (svenska TTS): models/piper-sv/")
    print("    Ladda ner både .onnx och .onnx.json filer")
    print("    Exempel: sv_SE-lisa-medium.onnx + sv_SE-lisa-medium.onnx.json")
    print("    → https://github.com/rhasspy/piper#voices")
    print("  • Porcupine wakeword (.ppn): models/wakewords/sv/")
    print("    → https://picovoice.ai/platform/porcupine/")

    print("\n" + "─" * 70)
    print("⚙️  MQTT Konfiguration (HiveMQ Cloud)")
    print("─" * 70)
    print("💡 Använder HiveMQ Cloud - ingen lokal MQTT-installation krävs")
    print("📖 Skapa ett gratis konto på: https://console.hivemq.cloud/")
    print()
    print("⚠️  VIKTIGT: Använd bara CLUSTER URL från HiveMQ Cloud")
    print("   ✅ RÄTT format: abc123.hivemq.cloud")
    print("   ❌ FEL format: mqtts://abc123.hivemq.cloud:8883")
    print("   ❌ FEL format: wss://abc123.hivemq.cloud:8884/mqtt")
    print()
    print("   I HiveMQ Cloud dashboard, använd fältet märkt 'URL'")
    print("   (INTE 'TLS MQTT URL' eller 'TLS Websocket URL')")
    
    mqtt_host_raw = ask("HiveMQ Cloud cluster URL (bara hostname, t.ex. abc123.hivemq.cloud)")
    if not mqtt_host_raw:
        print("❌ MQTT broker host krävs!")
        sys.exit(1)
    
    # Rensa URL från eventuella protokoll och portar
    mqtt_host = strip_mqtt_protocol(mqtt_host_raw)
    if mqtt_host != mqtt_host_raw:
        print(f"ℹ️  URL korrigerad automatiskt: {mqtt_host_raw} → {mqtt_host}")
    
    mqtt_port = ask(
        "MQTT broker port (8883 för TLS)", 
        "8883",
        validator=validate_port,
        error_msg="Port måste vara mellan 1 och 65535"
    )
    mqtt_username = ask("HiveMQ Cloud användarnamn")
    if not mqtt_username:
        print("❌ Användarnamn krävs för HiveMQ Cloud!")
        sys.exit(1)
    
    mqtt_password = ask("HiveMQ Cloud lösenord")
    if not mqtt_password:
        print("❌ Lösenord krävs för HiveMQ Cloud!")
        sys.exit(1)
    
    mqtt_tls = ask("Använd TLS? (true/false)", "true").lower()
    mqtt_tls = "True" if mqtt_tls in ("true", "yes", "1") else "False"

    print("\n" + "─" * 70)
    print("📡 MQTT Topics")
    print("─" * 70)
    
    topic_commands = ask("Commands topic", "rpi/commands/text")
    topic_responses = ask("Responses topic", "rpi/responses/text")
    client_id = ask("MQTT client ID", "rpi-n8n-voice-assistant")

    print("\n" + "─" * 70)
    print("🎤 Röstdetektering (Porcupine)")
    print("─" * 70)
    print("⚠️  Notera: PORCUPINE_ACCESS_KEY är känslig och ska ej delas!")
    
    porcupine_key = ask("Picovoice Access Key (obligatorisk)")
    if not porcupine_key:
        print("❌ Access key krävs för att använda Porcupine!")
        sys.exit(1)
    
    wakeword_path = ask("Wakeword fil (.ppn)", "models/wakewords/sv/assistans.ppn")

    print("\n" + "─" * 70)
    print("🗣️  Speech-to-Text och Text-to-Speech")
    print("─" * 70)
    
    vosk_path = ask("Vosk model sökväg", "models/vosk-model-sv")
    piper_path = ask("Piper model sökväg", "models/piper-sv")
    piper_speaker = ask("Piper speaker ID (tom = auto)", "")

    print("\n" + "─" * 70)
    print("🔊 Ljudinställningar")
    print("─" * 70)
    print("Tip: Lämna tom för standardenheter")
    
    input_dev = ask("Input device index (tom = standard)", "")
    output_dev = ask("Output device index (tom = standard)", "")
    
    sample_rate = ask(
        "Sample rate (Hz)",
        "16000",
        validator=validate_sample_rate,
        error_msg="Sample rate måste vara positiv"
    )
    
    record_seconds = ask(
        "Inspelningstid efter wakeword (sekunder)",
        "6",
        validator=validate_seconds,
        error_msg="Måste vara mellan 1 och 60 sekunder"
    )

    print("\n" + "─" * 70)
    print("📝 Loggning")
    print("─" * 70)
    
    log_level = ask("Log level (DEBUG/INFO/WARNING/ERROR)", "INFO")

    # Skriv .env fil
    print("\n" + "─" * 70)
    print("💾 Sparar konfiguration...")
    print("─" * 70)
    
    try:
        # SÄKERHETSNOTERING: .env-filen innehåller känslig information i klartext.
        # Detta är standard för miljövariabel-filer och anses säkert så länge:
        # 1. Filen är exkluderad från versionshantering (.gitignore)
        # 2. Filbehörigheter är korrekta (chmod 600 rekommenderas)
        # 3. Systemet är säkert (användarautentisering, ingen obehörig åtkomst)
        # För produktionsmiljöer bör secrets managers (Vault, AWS Secrets Manager) övervägas.
        
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write("# MQTT Configuration\n")
            f.write(f"MQTT_HOST={mqtt_host}\n")
            f.write(f"MQTT_PORT={mqtt_port}\n")
            f.write(f"MQTT_USERNAME={mqtt_username}\n")
            f.write(f"MQTT_PASSWORD={mqtt_password}\n")  # nosec - intentional for .env file
            f.write(f"MQTT_TLS={mqtt_tls}\n\n")
            
            f.write("# MQTT Topics\n")
            f.write(f"MQTT_TOPIC_COMMANDS={topic_commands}\n")
            f.write(f"MQTT_TOPIC_RESPONSES={topic_responses}\n")
            f.write(f"CLIENT_ID={client_id}\n\n")
            
            f.write("# Picovoice Porcupine (KÄNSLIG - håll privat!)\n")
            f.write(f"PORCUPINE_ACCESS_KEY={porcupine_key}\n\n")
            
            f.write("# Model Paths\n")
            f.write(f"WAKEWORD_PATH={wakeword_path}\n")
            f.write(f"VOSK_MODEL_PATH={vosk_path}\n")
            f.write(f"PIPER_MODEL_PATH={piper_path}\n")
            if piper_speaker:
                f.write(f"PIPER_SPEAKER={piper_speaker}\n")
            f.write("\n")
            
            f.write("# Audio Settings\n")
            if input_dev:
                f.write(f"INPUT_DEVICE_INDEX={input_dev}\n")
            if output_dev:
                f.write(f"OUTPUT_DEVICE_INDEX={output_dev}\n")
            f.write(f"SAMPLE_RATE={sample_rate}\n")
            f.write(f"RECORD_SECONDS_AFTER_WAKE={record_seconds}\n\n")
            
            f.write("# Logging\n")
            f.write(f"LOG_LEVEL={log_level}\n")

        print(f"✓ Konfiguration sparad i {ENV_FILE}")
        
        # Säkra filbehörigheter (endast ägaren kan läsa/skriva)
        try:
            os.chmod(ENV_FILE, 0o600)
            print(f"✓ Filbehörigheter satta till 600 (endast ägare kan läsa)")
        except Exception as e:
            print(f"⚠️  Varning: Kunde inte sätta filbehörigheter: {e}")
        
        # Säkerhetsvarning
        print("\n" + "─" * 70)
        print("🔒 SÄKERHETSVARNING")
        print("─" * 70)
        print(f"⚠️  {ENV_FILE} innehåller känslig information (API-nycklar, lösenord)")
        print(f"⚠️  Dela ALDRIG denna fil eller committa den till Git!")
        print(f"⚠️  Filen är redan exkluderad i .gitignore")
        print(f"⚠️  Filbehörigheter: 600 (rekommenderas för produktion)")
        
        print("\n" + "─" * 70)
        print("✅ Setup klar!")
        print("─" * 70)
        print("\n📋 Nästa steg:")
        print("  1. Ladda ner och installera modellerna (se länkar ovan)")
        print("  2. Starta applikationen: python3 main.py")
        print("  3. Sätt upp ditt n8n-flöde (se README.md)")
        print("\n🎉 Lycka till!")
        
    except Exception as e:
        print(f"\n❌ Fel vid sparande av konfiguration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup avbruten av användare")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Oväntat fel: {e}")
        sys.exit(1)
