# HiveMQ Cloud Guide

## Översikt

HiveMQ Cloud är en fullt hanterad MQTT broker som körs i molnet. Den eliminerar behovet av att installera och underhålla en egen MQTT broker, vilket gör det enkelt att sätta upp en säker och skalbar IoT-lösning.

## Varför HiveMQ Cloud?

### ✅ Fördelar

**Ingen Installation eller Underhåll**
- Ingen MQTT broker att installera på Raspberry Pi eller server
- Inga uppdateringar eller säkerhetspatchar att hantera
- Ingen konfiguration av TLS-certifikat

**Säkerhet Inbyggt**
- TLS/SSL-kryptering alltid aktiverad
- Användarautentisering krävs för alla anslutningar
- Inget exponerat på ditt lokala nätverk

**Skalbarhet**
- Automatisk skalning vid ökad belastning
- Hög tillgänglighet med redundans
- Global närvaro för låg latens

**Enkel Hantering**
- Webbaserad administrationskonsol
- Realtidsövervakning av anslutningar och meddelanden
- Enkel användarhantering

**Kostnadsfritt**
- Gratis tier inkluderar:
  - 100 samtidiga anslutningar
  - 10 GB dataöverföring per månad
  - Perfekt för detta projekt!

### 🆚 Jämförelse med Lokal Mosquitto

| Aspekt | HiveMQ Cloud | Lokal Mosquitto |
|--------|--------------|-----------------|
| Installation | ❌ Ingen | ✅ Måste installeras |
| Underhåll | ❌ Inget | ⚠️ Regelbundna uppdateringar |
| TLS/SSL | ✅ Alltid aktiverad | ⚠️ Måste konfigureras |
| Åtkomst | 🌍 Från överallt | 🏠 Endast lokalt nätverk |
| Skalning | ✅ Automatisk | ⚠️ Manuell |
| Kostnad | 💰 Gratis tier | 💰 Gratis men el-kostnad |
| Backup | ✅ Automatisk | ⚠️ Måste konfigureras |
| Övervakning | ✅ Inbyggd konsol | ⚠️ Extra verktyg krävs |

## Snabbstart

### 1. Skapa Konto

1. Gå till https://console.hivemq.cloud/
2. Klicka på **"Sign Up"**
3. Fyll i dina uppgifter och verifiera email
4. Logga in på konsolen

### 2. Skapa Kluster

1. Klicka på **"Create Cluster"**
2. Välj plan:
   - **Free**: Perfekt för detta projekt
   - **Professional**: För produktionsmiljöer
3. Välj region:
   - Välj närmaste region för bästa prestanda
   - Europa: `eu-central-1` (Frankfurt) eller `eu-west-1` (Irland)
4. Ge klustret ett namn (t.ex. "voice-assistant")
5. Klicka på **"Create"**

⏱️ Klustret tar 2-3 minuter att skapa

### 3. Hämta Anslutningsinformation

När klustret är skapat, anteckna:

- **Cluster URL**: Visas på Overview (t.ex. `a1b2c3d4.hivemq.cloud`)
- **Port (MQTT/TLS)**: `8883`
- **Port (Websockets/TLS)**: `8884`

### 4. Skapa Användare

1. I kluster-dashboard, klicka på **"Access Management"**
2. Klicka på **"Add Credentials"**
3. Fyll i:
   - **Username**: `rpi-voice-assistant` (eller eget val)
   - **Password**: Generera starkt lösenord (spara säkert!)
4. Klicka på **"Add"**

💡 **Tips**: Skapa separata användare för olika enheter:
- `rpi-voice-assistant` för Raspberry Pi
- `n8n-workflow` för n8n
- `test-client` för testning

### 5. Konfigurera Röstassistenten

Kör setup wizard:

```bash
cd genio-bot-v2
source venv/bin/activate
python3 setup_wizard.py
```

Ange dina HiveMQ Cloud uppgifter när du tillfrågas.

### 6. Testa Anslutning

```bash
# Installera mosquitto-clients
sudo apt install mosquitto-clients

# Testa anslutning (ersätt med dina uppgifter)
mosquitto_pub -h a1b2c3d4.hivemq.cloud -p 8883 \
  --capath /etc/ssl/certs/ \
  -u rpi-voice-assistant -P ditt-lösenord \
  -t test -m "Hello from Raspberry Pi"
```

Om inga fel visas är anslutningen lyckad! ✅

## HiveMQ Cloud Konsol

### Dashboard Overview

I huvuddashboard kan du se:

- **Cluster Status**: Grön = aktiv, Röd = problem
- **Connected Clients**: Antal aktiva anslutningar
- **Messages/sec**: Antal meddelanden per sekund
- **Data Transfer**: Total dataöverföring

### Access Management

Hantera användare och behörigheter:

- **Add User**: Skapa ny användare
- **Edit User**: Ändra lösenord
- **Delete User**: Ta bort användare
- **View Permissions**: Se vad varje användare har åtkomst till

### Web Client

Inbyggd MQTT-klient för testning:

1. Klicka på **"Web Client"** i sidomenyn
2. Anslut med dina credentials
3. **Subscribe**: Lyssna på topics
4. **Publish**: Skicka meddelanden
5. **History**: Se tidigare meddelanden

Användbart för:
- Testa att meddelanden går fram
- Debugga topic-namn
- Verifiera JSON-format
- Övervaka realtidstrafik

### Metrics

Detaljerad statistik:

- **Connected Clients**: Över tid
- **Messages**: Inkommande/utgående
- **Bandwidth**: Dataöverföring
- **Errors**: Anslutningsfel och problem

### Settings

Kluster-inställningar:

- **General**: Namn, region, plan
- **Security**: TLS-inställningar
- **Limits**: Max anslutningar, meddelanden
- **Billing**: Fakturainformation (för betalplaner)

## Best Practices

### Säkerhet

**Starka Lösenord**
```bash
# Generera starkt lösenord
openssl rand -base64 32
```

**Rotera Lösenord Regelbundet**
- Byt lösenord var 3-6 månad
- Vid misstänkt säkerhetsintrång

**Separata Användare**
- En användare per enhet/tjänst
- Enklare att spåra aktivitet
- Lätt att återkalla åtkomst

### Övervakning

**Kontrollera Regelbundet**
- Connected Clients: Ovanliga anslutningar?
- Message Rate: Ovanligt hög aktivitet?
- Error Log: Nya fel?

**Sätt upp Alerting**
- HiveMQ Cloud kan skicka email-notiser
- Konfigurera i Settings → Alerts

### Topics

**Använd Hierarkiska Topics**
```
rpi/commands/text
rpi/responses/text
rpi/status/online
rpi/errors/critical
```

**Topic Best Practices**
- Använd `/` för hierarki
- Håll topic-namn korta och beskrivande
- Använd wildcards för prenumeration: `rpi/#`

### QoS (Quality of Service)

**QoS 0**: At most once
- Snabbast
- Inga garantier
- Bra för: status-uppdateringar

**QoS 1**: At least once
- Garanterad leverans
- Kan dupliceras
- Bra för: kommandon

**QoS 2**: Exactly once
- Långsammast
- Garanterad en gång
- Bra för: kritiska meddelanden

För detta projekt: **QoS 0** är tillräckligt

## Felsökning

### Kan inte skapa konto

- **Email finns redan**: Använd glömt lösenord
- **Email verifieras inte**: Kolla spam-mapp
- **Region inte tillgänglig**: Välj annan region

### Kluster startar inte

- Vänta 5 minuter och uppdatera sidan
- Kontrollera HiveMQ Cloud status-sida
- Kontakta HiveMQ support via konsolen

### Kan inte ansluta till kluster

**Kontrollera:**
1. Cluster URL är korrekt (utan `mqtt://` eller `https://`)
2. Port är `8883` (inte `1883`)
3. Username och password är korrekta
4. TLS är aktiverat i klienten

**Testa:**
```bash
# Ping kluster
ping a1b2c3d4.hivemq.cloud

# Testa TLS-anslutning
openssl s_client -connect a1b2c3d4.hivemq.cloud:8883
```

### Meddelanden går inte fram

**I HiveMQ Cloud Console:**
1. Gå till Metrics → Messages
2. Kontrollera att meddelanden tas emot
3. Öppna Web Client
4. Prenumerera på `#` (alla topics)
5. Skicka testmeddelande från röstassistenten
6. Kontrollera att det syns i Web Client

**Vanliga orsaker:**
- Fel topic-namn
- Client inte ansluten
- QoS-problem
- JSON-format fel

## Kostnader

### Free Tier (Forever Free)

**Ingår:**
- 100 samtidiga anslutningar
- 10 GB dataöverföring per månad
- Grundläggande funktioner
- Community support

**Räcker för:**
- Detta projekt med marginal
- Upp till 10 Raspberry Pi enheter
- Testning och utveckling

### Professional Plan

Om du växer ur Free tier:

**Från $49/månad:**
- 200+ anslutningar
- 50+ GB dataöverföring
- Prioriterad support
- SLA 99.9%
- Avancerad övervakning

## Alternativ till HiveMQ Cloud

Om HiveMQ Cloud inte passar:

### CloudMQTT
- https://www.cloudmqtt.com/
- Liknande tjänst
- Gratis tier: 10 anslutningar

### AWS IoT Core
- https://aws.amazon.com/iot-core/
- Mer avancerad
- Betala per användning

### Azure IoT Hub
- https://azure.microsoft.com/services/iot-hub/
- Microsoft-ekosystem
- Gratis tier begränsad

### Shiftr.io
- https://shiftr.io/
- Enkel att använda
- Gratis tier: 5 anslutningar

## Support och Resurser

### HiveMQ Cloud Support

**Community:**
- Forum: https://community.hivemq.com/
- GitHub: https://github.com/hivemq

**Documentation:**
- https://docs.hivemq.com/hivemq-cloud/

**Support Tickets:**
- Via HiveMQ Cloud Console
- Svarstid beroende på plan

### Röstassistenten Support

**Problem med röstassistenten:**
- Se [README.md](README.md)
- Se [MQTT_SETUP.md](MQTT_SETUP.md)
- Skapa issue på GitHub

## Sammanfattning

HiveMQ Cloud är det perfekta valet för detta projekt:

✅ Inga installationer behövs  
✅ Säkert ur lådan  
✅ Gratis för detta projekt  
✅ Enkel att använda  
✅ Professionell lösning  

**Nästa steg:**
1. Skapa HiveMQ Cloud konto
2. Konfigurera röstassistenten
3. Konfigurera n8n
4. Börja utveckla röstkommandon!

---

**Frågor?** Se [MQTT_QUICKSTART.md](MQTT_QUICKSTART.md) för snabb hjälp eller [MQTT_SETUP.md](MQTT_SETUP.md) för komplett guide.
