# MQTT Setup Guide - Sätta upp en fungerande MQTT miljö

Denna guide hjälper dig att sätta upp en komplett MQTT-miljö för röstassistenten, inklusive MQTT broker (Mosquitto) och integration med n8n.

## 📋 Innehållsförteckning

1. [Översikt](#översikt)
2. [Metod 1: Docker Compose (Rekommenderas)](#metod-1-docker-compose-rekommenderas)
3. [Metod 2: Manuell installation](#metod-2-manuell-installation)
4. [Konfigurera n8n för MQTT](#konfigurera-n8n-för-mqtt)
5. [Testa MQTT-anslutningen](#testa-mqtt-anslutningen)
6. [Felsökning](#felsökning)

## 🎯 Översikt

För att röstassistenten ska fungera behöver du:

1. **MQTT Broker** (Mosquitto) - fungerar som meddelandehanterare (på ai.genio-bot.com)
2. **n8n** - för att bearbeta röstkommandon och skapa svar (på ai.genio-bot.com)
3. **Röstassistenten** (denna applikation) - körs på Raspberry Pi

**⚠️ VIKTIGT:** n8n och MQTT broker körs på **ai.genio-bot.com**, inte lokalt på din Raspberry Pi!

```
┌─────────────────┐      MQTT Topics:           ┌────────────────────────┐
│  Raspberry Pi   │  ──► rpi/commands/text ──►  │   ai.genio-bot.com     │
│ (Röstassistent) │                              │  ┌──────────────┐      │
│                 │  ◄── rpi/responses/text ◄──  │  │     n8n      │      │
└─────────────────┘                              │  └──────────────┘      │
         │                                       │         │              │
         └──────────► MQTT Broker (Mosquitto) ◄─┴─────────┘              │
                      (ai.genio-bot.com:1883)   └────────────────────────┘
```

## 🐳 Metod 1: Docker Compose (För lokal testning)

**⚠️ OBS:** Detta är **ENDAST** för lokal utveckling och testning. I produktionsmiljön körs n8n och MQTT broker redan på **ai.genio-bot.com**.

Om du vill testa lokalt kan du sätta upp både Mosquitto och n8n med Docker Compose:

### Steg 1: Installera Docker och Docker Compose

**På Raspberry Pi:**
```bash
# Installera Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Lägg till din användare i docker-gruppen
sudo usermod -aG docker $USER

# Logga ut och in igen för att aktivera gruppmedlemskapet
# Eller kör: newgrp docker

# Installera Docker Compose (om inte redan installerat)
sudo apt-get install docker-compose-plugin
```

**På Ubuntu/Debian server:**
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

### Steg 2: Använd medföljande docker-compose.yml

Projektet innehåller en färdig `docker-compose.yml` som startar både Mosquitto och n8n.

**Snabbstart (rekommenderas):**
```bash
# Kör det medföljande skriptet som startar allt automatiskt
./start-mqtt-environment.sh
```

**Manuellt:**
```bash
# Starta alla tjänster
docker compose up -d

# Kontrollera att de körs
docker compose ps

# Se loggar
docker compose logs -f
```

### Steg 3: Verifiera installationen

```bash
# Testa att Mosquitto körs
docker compose exec mosquitto mosquitto_pub -t "test" -m "hello"

# n8n bör nu vara tillgängligt på http://localhost:5678
```

### Steg 4: Konfigurera röstassistenten

Kör setup wizard och använd följande MQTT-inställningar:

```bash
source venv/bin/activate
python3 setup_wizard.py
```

**För anslutning till produktionsservern (ai.genio-bot.com):**
- **MQTT broker host**: `ai.genio-bot.com`
- **MQTT broker port**: `1883`
- **MQTT användarnamn**: (lämna tom eller använd ditt användarnamn)
- **MQTT lösenord**: (lämna tom eller använd ditt lösenord)
- **Använd TLS**: `false` (eller `true` om konfigurerat)

**För lokal testning:**
- **MQTT broker host**: `localhost`
- **MQTT broker port**: `1883`
- **MQTT användarnamn**: (lämna tom)
- **MQTT lösenord**: (lämna tom)
- **Använd TLS**: `false`

## 🔧 Metod 2: Anslut till befintlig server (ai.genio-bot.com)

**⚠️ REKOMMENDERAT:** För normal användning, anslut direkt till **ai.genio-bot.com** där n8n och MQTT broker redan körs.

Du behöver **INTE** installera Mosquitto eller n8n lokalt. Hoppa direkt till [Konfigurera röstassistenten](#konfigurera-röstassistenten-för-produktionsservern).

### Konfigurera röstassistenten för produktionsservern

1. **Kör setup wizard:**
```bash
source venv/bin/activate
python3 setup_wizard.py
```

2. **Använd följande värden:**
   - **MQTT broker host**: `ai.genio-bot.com` (standard)
   - **MQTT broker port**: `1883`
   - **MQTT användarnamn**: (lämna tom eller be din administratör om uppgifter)
   - **MQTT lösenord**: (lämna tom eller be din administratör om uppgifter)
   - **Använd TLS**: `false` (eller `true` beroende på serverkonfiguration)

3. **Testa anslutningen:**
```bash
# Installera mosquitto-clients om du inte har det
sudo apt install mosquitto-clients

# Testa anslutning till servern
mosquitto_pub -h ai.genio-bot.com -t "test/connection" -m "Hello from Raspberry Pi"
```

4. **Starta röstassistenten:**
```bash
source venv/bin/activate
python3 main.py
```

**Klart!** Din röstassistent kommer nu att kommunicera med n8n på ai.genio-bot.com via MQTT.

## 🔧 Metod 3: Manuell installation (För lokal testning)

Om du föredrar att installera Mosquitto direkt på systemet för lokal utveckling.

### Steg 1: Installera Mosquitto

**På Raspberry Pi OS / Debian / Ubuntu:**
```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients -y
```

### Steg 2: Konfigurera Mosquitto

Skapa konfigurationsfil:

```bash
sudo nano /etc/mosquitto/conf.d/custom.conf
```

Lägg till följande innehåll:

```conf
# Lyssna på alla nätverksgränssnitt
listener 1883 0.0.0.0

# Tillåt anonym åtkomst (OBS: Inte för produktion!)
allow_anonymous true

# Loggning
log_dest file /var/log/mosquitto/mosquitto.log
log_dest stdout
log_type all

# Persistence
persistence true
persistence_location /var/lib/mosquitto/

# Ökad timeout för långsamma klienter
keepalive_interval 60
```

**⚠️ Säkerhetsvarning**: Ovanstående konfiguration tillåter anonym åtkomst. För produktion, se [Säker konfiguration](#säker-konfiguration-produktion) nedan.

### Steg 3: Starta och aktivera Mosquitto

```bash
# Starta Mosquitto
sudo systemctl start mosquitto

# Aktivera automatisk start vid uppstart
sudo systemctl enable mosquitto

# Kontrollera status
sudo systemctl status mosquitto
```

### Steg 4: Testa installation

```bash
# Terminal 1: Prenumerera på ett topic
mosquitto_sub -h localhost -t "test/#" -v

# Terminal 2: Publicera ett meddelande
mosquitto_pub -h localhost -t "test/hello" -m "Hello MQTT!"
```

Om du ser meddelandet i Terminal 1, fungerar Mosquitto korrekt! ✅

### 📦 Installera n8n (valfritt - om inte redan installerat)

**Alternativ A: Docker (rekommenderas)**
```bash
docker run -d --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  --restart unless-stopped \
  n8nio/n8n
```

**Alternativ B: npm**
```bash
npm install -g n8n
n8n start
```

n8n kommer nu vara tillgängligt på: http://localhost:5678

## 🔌 Konfigurera n8n för MQTT

**📍 n8n är tillgänglig på:** http://ai.genio-bot.com:5678 (kontakta administratören för inloggningsuppgifter)

### Steg 1: Skapa ett nytt workflow i n8n

1. Öppna n8n i din webbläsare: http://ai.genio-bot.com:5678
2. Logga in med dina uppgifter
3. Skapa ett nytt workflow
4. Lägg till noderna enligt schemat nedan

### Steg 2: Lägg till MQTT Trigger Node

1. Klicka på "+" för att lägga till en ny nod
2. Sök efter "MQTT Trigger"
3. Konfigurera:
   - **Broker**: `localhost` (n8n och MQTT broker körs på samma server)
   - **Port**: `1883`
   - **Protocol**: `mqtt`
   - **Topics**: `rpi/commands/text`
   - **Client ID**: `n8n-mqtt-trigger` (valfritt)

**⚠️ Observera:** Använd `localhost` i n8n eftersom n8n och Mosquitto körs på samma server (ai.genio-bot.com). Raspberry Pi:n ansluter dock till `ai.genio-bot.com`.

### Steg 3: Lägg till processlogik

Exempel med en Code node för att bearbeta kommandon:

```javascript
// Hämta inkommande text
const incomingText = $json.text.toLowerCase();
let responseText = "Jag förstår tyvärr inte vad du vill.";

// Enkel kommandohantering
if (incomingText.includes("vad är klockan")) {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();
  responseText = `Klockan är nu ${hours} och ${minutes} minuter.`;
} 
else if (incomingText.includes("hej") || incomingText.includes("hallå")) {
  responseText = "Hej! Hur kan jag hjälpa dig?";
} 
else if (incomingText.includes("väder")) {
  responseText = "Tyvärr kan jag inte hämta väderinformation än, men det ser fint ut!";
}
else if (incomingText.includes("tack")) {
  responseText = "Varsågod! Jag finns här om du behöver mer hjälp.";
}

// Returnera svar med rätt format
return [{ 
  json: { 
    tts_text: responseText 
  } 
}];
```

### Steg 4: Lägg till MQTT Publish Node

1. Lägg till en "MQTT" nod efter Code-noden
2. Konfigurera:
   - **Broker**: `localhost` (n8n och MQTT broker körs på samma server)
   - **Port**: `1883`
   - **Protocol**: `mqtt`
   - **Topic**: `rpi/responses/text`
   - **Message**: `={{ $json }}`
   - **QoS**: `0`

### Steg 5: Aktivera workflow

Klicka på "Active" i övre högra hörnet för att aktivera workflowet.

## 🧪 Testa MQTT-anslutningen

### Test 1: Automatisk test (rekommenderas)

Använd det medföljande testskriptet:

```bash
./test-mqtt-connection.sh
```

Detta skript testar:
- Anslutning till MQTT broker
- Publicera och prenumerera på meddelanden
- Röstassistent topics (rpi/commands/text)

### Test 2: Manuellt meddelande

Simulera ett kommando från röstassistenten:

**För anslutning till ai.genio-bot.com:**
```bash
mosquitto_pub -h ai.genio-bot.com -t "rpi/commands/text" \
  -m '{"text":"hej", "timestamp":"2024-01-01T12:00:00"}'
```

Du bör se svaret på response-topic:

```bash
mosquitto_sub -h ai.genio-bot.com -t "rpi/responses/text" -v
```

**För lokal testning:**
```bash
mosquitto_pub -h localhost -t "rpi/commands/text" \
  -m '{"text":"hej", "timestamp":"2024-01-01T12:00:00"}'

mosquitto_sub -h localhost -t "rpi/responses/text" -v
```

### Test 3: Med röstassistenten

1. Starta röstassistenten:
```bash
source venv/bin/activate
python3 main.py
```

2. Säg wakeword (t.ex. "assistans") följt av ett kommando
3. Kontrollera loggarna för både röstassistenten och n8n

### Test 4: MQTT Explorer (GUI-verktyg)

För enklare testning och debugging, installera MQTT Explorer:

**På Windows/Mac/Linux:**
- Ladda ner från: https://mqtt-explorer.com/
- Anslut till din broker: `ai.genio-bot.com:1883` (för produktionsservern) eller `localhost:1883` (för lokal testning)
- Prenumerera på `rpi/#` för att se all trafik

## 🔒 Säker konfiguration (Produktion)

För produktionsmiljöer bör du aktivera autentisering.

### Skapa användarnamn och lösenord

```bash
# Skapa lösenordsfil (första användaren)
sudo mosquitto_passwd -c /etc/mosquitto/passwd mqttuser

# Lägg till fler användare (utan -c flaggan)
sudo mosquitto_passwd /etc/mosquitto/passwd n8nuser
```

### Uppdatera Mosquitto-konfiguration

```bash
sudo nano /etc/mosquitto/conf.d/custom.conf
```

Ändra till:

```conf
# Lyssna på alla nätverksgränssnitt
listener 1883 0.0.0.0

# Kräv autentisering
allow_anonymous false
password_file /etc/mosquitto/passwd

# Loggning
log_dest file /var/log/mosquitto/mosquitto.log
log_type all

# Persistence
persistence true
persistence_location /var/lib/mosquitto/
```

Starta om Mosquitto:

```bash
sudo systemctl restart mosquitto
```

### Uppdatera klientkonfiguration

**I .env för röstassistenten:**
```env
MQTT_USERNAME=mqttuser
MQTT_PASSWORD=ditt_lösenord
```

**I n8n MQTT-noder:**
- Lägg till Credentials för MQTT med användarnamn och lösenord

## 🐛 Felsökning

### Problem: Kan inte ansluta till MQTT broker

**Kontrollera att Mosquitto körs:**
```bash
# Om Docker:
docker compose ps

# Om systemd:
sudo systemctl status mosquitto
```

**Kontrollera portar:**
```bash
sudo netstat -tulpn | grep 1883
# Eller
sudo ss -tulpn | grep 1883
```

**Testa lokal anslutning:**
```bash
mosquitto_pub -h localhost -t "test" -m "hello" -d
```

### Problem: n8n kan inte ansluta till Mosquitto

**På produktionsservern (ai.genio-bot.com):**
- n8n och Mosquitto körs på samma server, använd `localhost` i n8n
- Kontakta administratören om problem uppstår

**Om du använrar lokal Docker Compose:**
- Använd service-namnet `mosquitto` istället för `localhost` i n8n
- Kontrollera att båda containers är på samma nätverk

**Om olika maskiner:**
- Kontrollera brandvägg: `sudo ufw allow 1883/tcp`
- Använd rätt IP-adress eller domännamn (ai.genio-bot.com)
- Testa med: `mosquitto_pub -h ai.genio-bot.com -t "test" -m "hello"`

### Problem: Meddelanden går inte fram

**Kontrollera topics:**
```bash
# Prenumerera på alla topics för debugging
mosquitto_sub -h localhost -t "#" -v
```

**Kontrollera loggar:**
```bash
# Mosquitto Docker:
docker compose logs mosquitto

# Mosquitto systemd:
sudo tail -f /var/log/mosquitto/mosquitto.log

# n8n:
docker compose logs n8n

# Röstassistent:
# Sätt LOG_LEVEL=DEBUG i .env
```

### Problem: "Connection refused"

**Kontrollera Mosquitto-konfigurationen:**
```bash
# Testa konfiguration
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
```

**Kontrollera att Mosquitto lyssnar på rätt interface:**
```bash
sudo netstat -tulpn | grep mosquitto
```

Ska visa något som:
```
tcp        0      0 0.0.0.0:1883            0.0.0.0:*               LISTEN      1234/mosquitto
```

### Problem: Timeout vid anslutning

**Öka timeout i röstassistentens .env:**
```env
MQTT_CONNECT_TIMEOUT=30
MQTT_MAX_RETRIES=10
```

**Kontrollera nätverkslatens:**
```bash
ping <mqtt-broker-ip>
```

## 📚 Ytterligare resurser

- **Mosquitto dokumentation**: https://mosquitto.org/documentation/
- **n8n MQTT nodes**: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.mqtt/
- **MQTT protokoll**: https://mqtt.org/
- **MQTT Explorer**: https://mqtt-explorer.com/

## 🎉 Sammanfattning

Efter att ha följt denna guide har du:

✅ En fungerande MQTT broker (Mosquitto)  
✅ n8n konfigurerat för MQTT-kommunikation  
✅ Röstassistenten ansluten till MQTT  
✅ Ett testbart end-to-end system  

Nu kan du börja utveckla mer avancerade röstkommandon och integrationer i n8n!

---

**Behöver du mer hjälp?** Se [README.md](README.md) för mer information om själva röstassistenten.
