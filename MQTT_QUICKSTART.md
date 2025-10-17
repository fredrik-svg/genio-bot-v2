# MQTT Quick Start - Kom igång snabbt!

Detta är den snabbaste vägen till att ansluta röstassistenten till MQTT-miljön.

**☁️ VIKTIGT:** Vi använder **HiveMQ Cloud** som MQTT broker - ingen lokal installation behövs!

## 🚀 Snabbstart (5 minuter) - Anslut till HiveMQ Cloud

### Steg 1: Skapa HiveMQ Cloud konto (gratis)

1. Gå till https://console.hivemq.cloud/
2. Skapa ett gratis konto
3. Skapa ett nytt kluster (free tier)
4. Anteckna följande information:
   - **Cluster URL** (t.ex. `abc123.hivemq.cloud`)
   - **Port** (8883 för TLS)
   - **Användarnamn** (skapa under "Access Management")
   - **Lösenord**

**⚠️ VIKTIGT - Vilken URL ska du använda?**

HiveMQ Cloud visar tre olika URLs:
1. **URL**: `abc123.hivemq.cloud` ✅ **ANVÄND DENNA!**
2. **TLS MQTT URL**: `mqtts://abc123.hivemq.cloud:8883` ❌ Använd INTE
3. **TLS Websocket URL**: `wss://abc123.hivemq.cloud:8884/mqtt` ❌ Använd INTE

**Använd bara den enkla cluster URL:en UTAN protokollprefix eller port.**

### Steg 2: Konfigurera röstassistenten

```bash
cd genio-bot-v2
source venv/bin/activate
python3 setup_wizard.py
```

Ange dina HiveMQ Cloud uppgifter när du tillfrågas:
- **MQTT broker host**: Din HiveMQ Cloud cluster URL
- **MQTT broker port**: `8883`
- **Användarnamn**: Ditt HiveMQ Cloud användarnamn
- **Lösenord**: Ditt HiveMQ Cloud lösenord
- **Använd TLS**: `true`

### Steg 3: Testa anslutning

```bash
# Installera mosquitto-clients om du inte har det
sudo apt install mosquitto-clients

# Testa anslutning till HiveMQ Cloud (ersätt med dina uppgifter)
mosquitto_pub -h your-cluster.hivemq.cloud -p 8883 \
  --capath /etc/ssl/certs/ \
  -u your-username -P your-password \
  -t test -m "hello"
```

Det är allt! 🎉

Du är nu ansluten till:
- ✅ **HiveMQ Cloud MQTT broker** (säker, molnbaserad)
- ✅ Redo att konfigurera **n8n** för att ansluta till samma broker

## 📋 Nästa steg

### 1. Testa MQTT-anslutningen

```bash
# Testa med dina HiveMQ Cloud uppgifter
mosquitto_sub -h your-cluster.hivemq.cloud -p 8883 \
  --capath /etc/ssl/certs/ \
  -u your-username -P your-password \
  -t "test/#" -v
```

### 2. Konfigurera n8n

Installera n8n lokalt eller använd en molntjänst:

```bash
# Lokalt med Docker
docker run -d -p 5678:5678 --name n8n n8nio/n8n

# Eller med npm
npm install -g n8n
n8n start
```

I n8n, konfigurera MQTT-noder med samma HiveMQ Cloud uppgifter.

### 3. Starta röstassistenten

```bash
source venv/bin/activate
python3 main.py
```

## 💡 Vanliga kommandon (HiveMQ Cloud)

```bash
# Sätt dina uppgifter som variabler för enklare användning
MQTT_HOST="your-cluster.hivemq.cloud"
MQTT_PORT="8883"
MQTT_USER="your-username"
MQTT_PASS="your-password"

# Testa MQTT-anslutning
mosquitto_pub -h $MQTT_HOST -p $MQTT_PORT \
  --capath /etc/ssl/certs/ -u $MQTT_USER -P $MQTT_PASS \
  -t test -m hello

# Lyssna på alla meddelanden
mosquitto_sub -h $MQTT_HOST -p $MQTT_PORT \
  --capath /etc/ssl/certs/ -u $MQTT_USER -P $MQTT_PASS \
  -t "rpi/#" -v

# Testa röstassistent topics
mosquitto_pub -h $MQTT_HOST -p $MQTT_PORT \
  --capath /etc/ssl/certs/ -u $MQTT_USER -P $MQTT_PASS \
  -t "rpi/commands/text" \
  -m '{"text":"hej", "timestamp":"2024-01-01T12:00:00"}'
```

## 🔍 Felsökning

### MQTT-anslutning fungerar inte

```bash
# Kontrollera att uppgifterna är korrekta
mosquitto_pub -h your-cluster.hivemq.cloud -p 8883 \
  --capath /etc/ssl/certs/ \
  -u your-username -P your-password \
  -t test -m hello -d

# Kontrollera TLS-anslutning
openssl s_client -connect your-cluster.hivemq.cloud:8883
```

### Kan inte nå HiveMQ Cloud

```bash
# Kontrollera nätverksanslutning
ping your-cluster.hivemq.cloud

# Kontrollera om port 8883 är öppen
nc -zv your-cluster.hivemq.cloud 8883
```

### Autentiseringsfel

- Kontrollera att användarnamn och lösenord är korrekta i HiveMQ Cloud konsolen
- Se till att användaren har rätt behörigheter (Access Management)
- Prova att skapa en ny användare om problemet kvarstår

## 📚 Mer information

- **Detaljerad MQTT-guide**: [MQTT_SETUP.md](MQTT_SETUP.md)
- **Installation av röstassistent**: [README.md](README.md)
- **Snabbguide för virtuell miljö**: [QUICKSTART.md](QUICKSTART.md)

## ❓ Vanliga frågor

### Var körs MQTT broker?

MQTT broker körs i **HiveMQ Cloud** - en molnbaserad tjänst. Ingen lokal installation behövs!

### Kostar HiveMQ Cloud pengar?

HiveMQ Cloud har en gratis tier som är mer än tillräcklig för detta projekt (100 anslutningar, 10 GB data/månad).

### Kan jag testa lokalt?

Ja! Du kan fortfarande köra en lokal Mosquitto broker för utveckling. Se [MQTT_SETUP.md](MQTT_SETUP.md) för instruktioner.

### Måste jag använda n8n?

Ja, n8n är nödvändigt för att bearbeta röstkommandon och generera svar. Du kan installera n8n lokalt eller använda en molntjänst.

### Hur konfigurerar jag n8n?

Installera n8n (lokalt eller moln) och konfigurera MQTT-noderna med samma HiveMQ Cloud uppgifter som röstassistenten använder.

### Är anslutningen säker?

Ja! HiveMQ Cloud använder TLS-kryptering (port 8883) och kräver autentisering för alla anslutningar.

---

## 🔧 Lokal utveckling (valfritt)

Om du vill testa med en lokal Mosquitto broker istället för HiveMQ Cloud:

### Steg 1: Installera Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Logga ut och in igen.

### Steg 2: Starta lokal MQTT-miljö

```bash
./start-mqtt-environment.sh
```

Nu har du en lokal miljö på:
- MQTT broker: `localhost:1883` (utan TLS)
- n8n: `http://localhost:5678`

### Steg 3: Konfigurera för lokal användning

Kör `python3 setup_wizard.py` och använd:
- **MQTT host**: `localhost`
- **Port**: `1883`
- **TLS**: `false`
- **Användarnamn/lösenord**: lämna tomma

**OBS:** Lokal installation är endast för testning! För produktion, använd HiveMQ Cloud.

---

**Behöver du mer hjälp?** Se [MQTT_SETUP.md](MQTT_SETUP.md) för komplett guide.
