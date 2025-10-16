# Projekt: `rpi-n8n-voice-assistant`

## Översikt
Detta projekt tillhandahåller en robust och säker röstassistentapplikation designad för Raspberry Pi 5. Den kombinerar lokal Speech-to-Text (STT) och Text-to-Speech (TTS) för svenska med realtidskommunikation till ett n8n-flöde via MQTT. Huvudsyftet är att möjliggöra en handsfree-interaktion med röstkommandon, där Raspberry Pi hanterar ljudin- och utgång samt röstigenkänning/syntes, medan n8n fungerar som den centrala "hjärnan" för att bearbeta kommandon och generera smarta svar.

> 💡 **Ny användare?** Se [QUICKSTART.md](QUICKSTART.md) för snabb guide om installation med virtuell miljö och lösning på `externally-managed-environment` felet.
> 
> 📡 **Behöver du sätta upp MQTT?** 
> - **Snabbstart (5 min)**: [MQTT_QUICKSTART.md](MQTT_QUICKSTART.md) 🚀
> - **Detaljerad guide**: [MQTT_SETUP.md](MQTT_SETUP.md) 📖

Applikationen är byggd med fokus på:
- 🔒 **Säkerhet**: Miljövariabler för känslig data, input-validering, resurshantering
- ⚡ **Prestanda**: Optimerad ljudhantering och effektiv resursanvändning
- 👥 **Användarvänlighet**: Interaktiv setup wizard, tydliga felmeddelanden
- 📈 **Skalbarhet**: Modulär struktur och konfigurerbar arkitektur
- 🔌 **Offline-funktionalitet**: Lokal STT/TTS och wakeword-detektering

## Funktioner

### Kärnfunktionalitet
- 🎯 **Wakeword-detektering**: Aktiveras av ett anpassat wakeword (t.ex. "assistans") med Picovoice Porcupine
- 🗣️ **Lokal Speech-to-Text (STT)**: Vosk svensk modell för offline röstigenkänning
- 🔊 **Lokal Text-to-Speech (TTS)**: Piper svensk modell för offline talsyntes
- 📡 **MQTT-kommunikation**: Säker och effektiv överföring mellan Raspberry Pi och n8n
- 🔊 **Ljudfeedback**: Korta ljudsignaler för lyssnar/kvittens

### Säkerhet & Prestanda
- 🔒 **Säker konfiguration**: Miljövariabler via `.env` för känslig data (API-nycklar, lösenord)
- ✅ **Input-validering**: Skydd mot injektionsattacker och överbelastning
- 🔄 **Robust återanslutning**: Exponentiell backoff för MQTT med konfigurerbar timeout
- 🛡️ **Resurshantering**: Automatisk cleanup vid fel och graceful shutdown
- ⚡ **Optimerad prestanda**: Effektiv bufferthantering och strömning

### Användarvänlighet
- 🧙 **Interaktiv setup wizard**: Guidar användaren genom initial konfiguration med validering
- 📝 **Detaljerad loggning**: Tydliga felmeddelanden och statusinformation
- 📚 **Utförlig dokumentation**: Kommenterad kod med docstrings och typehints
- ⚙️ **Flexibel konfiguration**: Stödjer både `.env`-filer och miljövariabler

## Installation (Raspberry Pi OS, 64-bit rekommenderas)

### 1. Förbered systemet
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv portaudio19-dev git
```

### 2. Klona projektet
```bash
git clone <repository-url>
cd genio-bot-v2
```

### 3. Installera Python-paket

**⚠️ Viktigt:** På moderna Raspberry Pi OS-versioner (och andra Debian/Ubuntu-baserade system) kan du få felmeddelandet `error: externally-managed-environment` när du försöker använda `pip3 install`. Detta är en säkerhetsfunktion för att skydda systempaketen.

**Lösning:** Använd en virtuell miljö (virtual environment), vilket är den rekommenderade metoden:

#### Alternativ A: Automatisk installation (rekommenderas)
```bash
./install.sh
```

Detta skript kommer att:
- Skapa en virtuell Python-miljö
- Installera alla beroenden
- Skapa nödvändiga mappar

#### Alternativ B: Manuell installation
```bash
# Skapa virtuell miljö
python3 -m venv venv

# Aktivera virtuell miljö
source venv/bin/activate

# Installera beroenden
pip install -r requirements.txt
```

**Notera:** Du måste aktivera den virtuella miljön varje gång du vill köra applikationen:
```bash
source venv/bin/activate
# Din prompt kommer att ändras till att visa (venv) framför den
# Exempel: (venv) user@raspberrypi:~/genio-bot-v2$
```

För att avaktivera den virtuella miljön när du är klar:
```bash
deactivate
```

### 4. Kör setup-wizardet
Setup-wizardet skapar en `.env`-fil med din konfiguration:
```bash
# Se till att virtuell miljö är aktiverad först
source venv/bin/activate
python3 setup_wizard.py
```

**Viktigt**: Följ instruktionerna i wizarden och ladda ner nödvändiga modeller:
- **Vosk** (svenska STT): [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
- **Piper** (svenska TTS): [github.com/rhasspy/piper#voices](https://github.com/rhasspy/piper#voices)
- **Porcupine** wakeword: [picovoice.ai/platform/porcupine](https://picovoice.ai/platform/porcupine/)

### 5. Starta applikationen
```bash
# Se till att virtuell miljö är aktiverad först
source venv/bin/activate
python3 main.py
```

### 🔒 Säkerhetsnot
- `.env`-filen innehåller känslig information och ska **ALDRIG** committas till Git
- Filen är redan exkluderad i `.gitignore`
- Använd `.env.example` som mall för nya installationer

## MQTT & n8n Setup

> 📖 **Se [MQTT_SETUP.md](MQTT_SETUP.md)** för komplett guide om hur du sätter upp MQTT broker och n8n integration.

### Snabb översikt
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
├── README.md                  # Denna fil
├── LICENSE                    # MIT-licens
├── .gitignore                 # Exkluderar känsliga filer från Git
├── .env.example               # Mall för miljövariabler
├── .env                       # Din konfiguration (skapas av wizard, GIT-IGNORERAD!)
├── requirements.txt           # Python-beroenden
├── main.py                    # Huvudapplikation
├── setup_wizard.py            # Interaktiv konfigurationsguide
├── config.py                  # Konfigurationshantering
├── mqtt_client.py             # MQTT-klient med säkerhet & felhantering
├── audio_utils.py             # Ljudhantering med resurshantering
├── audio_feedback/            # Feedback-ljud
│   ├── start_listen.wav       # Ljud när inspelning startar
│   └── end_listen.wav         # Ljud när inspelning slutar
└── models/                    # Modeller (GIT-IGNORERADE, ladda ner manuellt)
    ├── vosk-model-sv/         # Svensk Vosk STT-modell
    ├── piper-sv/              # Svensk Piper TTS-modell
    └── wakewords/
        └── sv/                # Porcupine wakeword-filer (.ppn)
```

## Förbättringar & Best Practices

### Säkerhet 🔒
- **Miljövariabler**: Känslig data (API-nycklar, lösenord) lagras i `.env` istället för kod
- **Input-validering**: Begränsningar på text- och payload-storlek för att förhindra DoS
- **TLS-stöd**: Säker MQTT-kommunikation med TLS 1.2
- **Resurshantering**: Automatisk cleanup vid fel för att undvika resursläckage
- **Gitignore**: Känsliga filer exkluderas automatiskt från versionshantering

### Prestanda ⚡
- **Optimerad ljudhantering**: Effektiv bufferthantering och strömning
- **Exponentiell backoff**: Smart återanslutningslogik för MQTT
- **Graceful shutdown**: Säker avslutning av alla resurser
- **Minimal minnesanvändning**: Context managers och explicit cleanup

### Användarvänlighet 👥
- **Interaktiv wizard**: Enkel konfiguration med validering och hjälptext
- **Tydliga felmeddelanden**: Detaljerad information vid problem
- **Emoji-indikationer**: Visuell feedback i loggar och wizard
- **Omfattande loggning**: DEBUG, INFO, WARNING, ERROR nivåer

### Kodkvalitet 📚
- **Type hints**: Typannoteringar för bättre IDE-stöd och färre buggar
- **Docstrings**: Dokumentation för alla klasser och metoder
- **Custom exceptions**: Specifika exceptions för olika fel-typer
- **Modulär struktur**: Separata moduler för olika ansvarsområden
- **PEP 8**: Följer Python kodstandarder

### Skalbarhet 📈
- **Konfigurerbar**: Enkelt att anpassa för olika användningsfall
- **Modulär design**: Lätt att utöka med nya funktioner
- **MQTT-arkitektur**: Stödjer flera klienter och distribuerade system
- **Lokal processing**: Offline STT/TTS minskar beroenden

## Felsökning

### Problem: externally-managed-environment
Om du får felmeddelandet `error: externally-managed-environment` när du försöker köra `pip3 install -r requirements.txt`:

**Orsak:** Moderna Debian/Ubuntu-baserade system (inklusive Raspberry Pi OS) använder PEP 668 för att förhindra att systempaketen bryts av pip-installationer.

**Lösning:**
1. **Använd virtuell miljö (rekommenderas):**
   ```bash
   # Kör installationsskriptet
   ./install.sh
   
   # Eller manuellt:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Alternativ (ej rekommenderat):** Använd `pip install --break-system-packages`, men detta kan orsaka problem med systempaket.

### Problem med MQTT-anslutning

Se den kompletta guiden: **[MQTT_SETUP.md](MQTT_SETUP.md)** för detaljerad information om att sätta upp MQTT broker.

```bash
# Kontrollera att MQTT broker körs
mosquitto -v

# Testa anslutning
mosquitto_pub -h localhost -t test -m "hello"
```

### Problem med ljudenheter
```python
# Aktivera virtuell miljö först
source venv/bin/activate

# Lista tillgängliga ljudenheter
import pyaudio
pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    print(i, pa.get_device_info_by_index(i)['name'])
```

### Debug-läge
Sätt `LOG_LEVEL=DEBUG` i `.env` för detaljerad loggning.

## Licens
MIT (se `LICENSE`).
