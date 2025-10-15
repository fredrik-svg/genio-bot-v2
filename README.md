# Projekt: `rpi-n8n-voice-assistant`

## Översikt
Detta projekt tillhandahåller en robust röstassistentapplikation designad för Raspberry Pi 5. Den kombinerar lokal Speech-to-Text (STT) och Text-to-Speech (TTS) för svenska med realtidskommunikation till ett n8n-flöde via MQTT. Huvudsyftet är att möjliggöra en handsfree-interaktion med röstkommandon, där Raspberry Pi hanterar ljudin- och utgång samt röstigenkänning/syntes, medan n8n fungerar som den centrala "hjärnan" för att bearbeta kommandon och generera smarta svar.

Applikationen är byggd med fokus på robusthet, säkerhet och offline-funktionalitet (för STT/TTS och wakeword), vilket gör den idealisk för inbäddade system och IoT-scenarion.

## Funktioner
- **Enkel setup-wizard:** Guidar användaren genom initial konfiguration.
- **Wakeword-detektering:** Aktiveras av ett anpassat wakeword (t.ex. "assistans") med Picovoice Porcupine.
- **Lokal Speech-to-Text (STT):** Vosk svensk modell.
- **Lokal Text-to-Speech (TTS):** Piper svensk modell.
- **MQTT-kommunikation:** Säker och effektiv överföring mellan Raspberry Pi och n8n.
- **Robust nätverkshantering:** Återanslutningslogik för MQTT.
- **Ljudfeedback:** Korta ljudsignaler för lyssnar/kvittens.
- **Konfigurerbart:** Via `config.py`.
- **Loggning och enkel felhantering.**

## Installation (Raspberry Pi OS, 64-bit rekommenderas)
1) Systempaket:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip portaudio19-dev
```
2) Klona/packa upp projektet och installera Python-paket:
```bash
cd rpi-n8n-voice-assistant
pip3 install -r requirements.txt
```
3) Kör setup-wizardet först:
```bash
python3 setup_wizard.py
```
4) Starta applikationen:
```bash
python3 main.py
```

## n8n (Server)
- **MQTT Trigger Node**: lyssnar på `rpi/commands/text`.
- Bearbeta texten (Code/LLM/HTTP).
- **MQTT Publish Node**: publicera svaret som JSON med fältet `tts_text` på `rpi/responses/text`.

### Exempel på Code-nod i n8n (JS)
```js
const incomingText = $json.text.toLowerCase();
let responseText = "Jag förstår tyvärr inte vad du vill.";

if (incomingText.includes("vad är klockan")) {
  const now = new Date();
  responseText = `Klockan är nu ${now.getHours()} och ${now.getMinutes()} minuter.`;
} else if (incomingText.includes("hej") || incomingText.includes("hallå")) {
  responseText = "Hej, hur kan jag hjälpa dig?";
} else if (incomingText.includes("säg något roligt")) {
  responseText = "Varför korsade kycklingen vägen? För att komma till andra sidan!";
}

return [{ json: { tts_text: responseText } }];
```

## Katalogstruktur
```
rpi-n8n-voice-assistant/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── main.py
├── setup_wizard.py
├── config.py
├── mqtt_client.py
├── audio_utils.py
├── audio_feedback/
│   ├── start_listen.wav
│   └── end_listen.wav
└── models/
    ├── vosk-model-sv/        # Lägg svensk Vosk-modell här
    ├── piper-sv/             # Lägg svensk Piper-modell här
    └── wakewords/
        └── sv/               # Lägg Porcupine .ppn här
```

## Licens
MIT (se `LICENSE`).
