# MQTT Setup Guide - Sätta upp en fungerande MQTT miljö

Denna guide hjälper dig att sätta upp en komplett MQTT-miljö för röstassistenten med HiveMQ Cloud och n8n.

## 📋 Innehållsförteckning

1. [Översikt](#översikt)
2. [Metod 1: HiveMQ Cloud (Rekommenderas för produktion)](#metod-1-hivemq-cloud-rekommenderas-för-produktion)
3. [Metod 2: Lokal Mosquitto (Endast för testning)](#metod-2-lokal-mosquitto-endast-för-testning)
4. [Konfigurera n8n för MQTT](#konfigurera-n8n-för-mqtt)
5. [Testa MQTT-anslutningen](#testa-mqtt-anslutningen)
6. [Felsökning](#felsökning)

## 🎯 Översikt

För att röstassistenten ska fungera behöver du:

1. **MQTT Broker** - HiveMQ Cloud (molnbaserad, säker, ingen installation behövs)
2. **n8n** - för att bearbeta röstkommandon och skapa svar (kan köras lokalt eller i molnet)
3. **Röstassistenten** (denna applikation) - körs på Raspberry Pi

**☁️ VIKTIGT:** Vi använder **HiveMQ Cloud** som MQTT broker - ingen lokal installation behövs!

```
┌─────────────────┐      MQTT Topics:           ┌────────────────────────┐
│  Raspberry Pi   │  ──► rpi/commands/text ──►  │   HiveMQ Cloud         │
│ (Röstassistent) │                              │   (TLS port 8883)      │
│                 │  ◄── rpi/responses/text ◄──  │                        │
└─────────────────┘                              └────────────────────────┘
         │                                                   ▲
         │                                                   │
         └───────────────────────────────────────────────────┘
                  Säker TLS-anslutning
                                               
                  ┌─────────────┐
                  │     n8n     │ ◄─── Ansluter till HiveMQ Cloud
                  │  (lokalt/   │      med samma uppgifter
                  │   moln)     │
                  └─────────────┘
```

## ☁️ Metod 1: HiveMQ Cloud (Rekommenderas för produktion)

**🚀 REKOMMENDERAT:** HiveMQ Cloud är en molnbaserad MQTT broker som inte kräver någon installation eller underhåll.

### Fördelar med HiveMQ Cloud
- ✅ Ingen installation eller konfiguration av MQTT broker
- ✅ Automatisk skalning och hög tillgänglighet
- ✅ Inbyggd TLS-säkerhet
- ✅ Gratis tier (100 anslutningar, 10 GB/månad)
- ✅ Webbaserad administrationskonsol
- ✅ Fungerar från vilken plats som helst (perfekt för IoT)

### Steg 1: Skapa HiveMQ Cloud konto

1. **Gå till HiveMQ Cloud:**
   - Besök: https://console.hivemq.cloud/
   - Skapa ett gratis konto

2. **Skapa ett nytt kluster:**
   - Klicka på "Create Cluster"
   - Välj "Free" plan (perfekt för detta projekt)
   - Välj en region nära dig (för bästa latens)
   - Ge ditt kluster ett namn
   - Klicka på "Create"

3. **Anteckna anslutningsinformation:**
   - **Cluster URL**: Hittas på kluster-dashboard (t.ex. `abc123.hivemq.cloud`)
   - **Port**: `8883` (TLS/SSL)
   - **WebSocket Port**: `8884` (om du behöver WebSocket)

**⚠️ VIKTIGT - Vilken URL ska du använda?**

HiveMQ Cloud visar tre olika URLs på dashboard:
1. **URL**: `abc123.hivemq.cloud` ✅ **ANVÄND DENNA FÖR RÖSTASSISTENTEN!**
2. **TLS MQTT URL**: `mqtts://abc123.hivemq.cloud:8883` ❌ Använd INTE (innehåller protokoll och port)
3. **TLS Websocket URL**: `wss://abc123.hivemq.cloud:8884/mqtt` ❌ Använd INTE (för websockets)

**För denna röstassistent måste du använda den enkla cluster URL:en UTAN protokollprefix (`mqtt://`, `mqtts://`, `wss://`) och UTAN port (`:8883`).**

Rätt exempel:
- ✅ `abc123.hivemq.cloud`
- ✅ `my-voice-cluster.hivemq.cloud`

Fel exempel:
- ❌ `mqtts://abc123.hivemq.cloud:8883`
- ❌ `abc123.hivemq.cloud:8883`
- ❌ `wss://abc123.hivemq.cloud:8884/mqtt`

### Steg 2: Skapa användare för MQTT-åtkomst

1. **Navigera till "Access Management"** i din kluster-dashboard
2. **Klicka på "Add Credentials"**
3. **Skapa användare för röstassistenten:**
   - **Username**: `rpi-voice-assistant` (eller valfritt namn)
   - **Password**: Generera ett starkt lösenord
   - **Permissions**: Lämna som standard (full åtkomst)
   - Klicka på "Add"
4. **Spara uppgifterna säkert** - du kommer behöva dem senare

**💡 Tips:** Du kan skapa olika användare för olika enheter (en för Raspberry Pi, en för n8n, etc.) för bättre säkerhet och spårbarhet.

### Steg 3: Konfigurera röstassistenten

Kör setup wizard och ange dina HiveMQ Cloud uppgifter:

```bash
cd genio-bot-v2
source venv/bin/activate
python3 setup_wizard.py
```

**Ange följande värden:**
- **HiveMQ Cloud cluster URL**: Din kluster-URL (t.ex. `abc123.hivemq.cloud`)
  - ⚠️ **OBS**: Använd ENDAST hostname, INTE "TLS MQTT URL" eller "TLS Websocket URL"
  - ✅ Rätt: `abc123.hivemq.cloud`
  - ❌ Fel: `mqtts://abc123.hivemq.cloud:8883`
- **MQTT broker port**: `8883`
- **HiveMQ Cloud användarnamn**: Det användarnamn du skapade
- **HiveMQ Cloud lösenord**: Det lösenord du skapade
- **Använd TLS**: `true`

Wizarden kommer att spara dessa uppgifter i `.env`-filen.

### Steg 4: Testa anslutningen

```bash
# Installera mosquitto-clients om du inte har det
sudo apt install mosquitto-clients

# Testa anslutning (ersätt med dina uppgifter)
mosquitto_pub -h abc123.hivemq.cloud -p 8883 \
  --capath /etc/ssl/certs/ \
  -u rpi-voice-assistant -P ditt-lösenord \
  -t test -m "Hello from Raspberry Pi"
```

Om du ser inga fel är anslutningen lyckad! ✅

### Steg 5: Övervaka anslutningar i HiveMQ Cloud

1. Gå tillbaka till HiveMQ Cloud konsolen
2. Navigera till "Overview" för ditt kluster
3. Kontrollera "Connected Clients" - du bör se din anslutning
4. Under "Metrics" kan du se meddelanden som skickas och tas emot

**🎉 Klart!** Din MQTT broker är nu uppsatt och redo att användas.

## 🐳 Metod 2: Lokal Mosquitto (Endast för testning)

**⚠️ OBS:** Detta är **ENDAST** för lokal utveckling och offline-testning. För produktion, använd HiveMQ Cloud (Metod 1).

Om du vill testa lokalt utan internetanslutning kan du sätta upp Mosquitto med Docker Compose:

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

**För lokal testning (utan TLS):**
- **MQTT broker host**: `localhost`
- **MQTT broker port**: `1883`
- **MQTT användarnamn**: (lämna tom)
- **MQTT lösenord**: (lämna tom)
- **Använd TLS**: `false`

**Viktigt:** Lokal Mosquitto kräver inte TLS och använder port 1883. Detta är ENDAST för testning!

### Steg 4: Starta röstassistenten

```bash
source venv/bin/activate
python3 main.py
```

**Klart!** Din röstassistent kommer nu att kommunicera via din lokala MQTT broker.

## 🔧 Metod 3: Manuell Mosquitto installation (För lokal testning)

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

n8n kan köras lokalt eller i molnet. Båda fallen ansluter till HiveMQ Cloud.

### Installera n8n (om du inte redan har det)

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

n8n blir tillgängligt på: http://localhost:5678

### Steg 1: Skapa MQTT Credentials i n8n

Innan du konfigurerar noder behöver du skapa credentials för HiveMQ Cloud:

1. I n8n, gå till **Settings** → **Credentials**
2. Klicka på **"New Credential"**
3. Sök efter och välj **"MQTT"**
4. Konfigurera credentials:
   - **Name**: `HiveMQ Cloud`
   - **Protocol**: `mqtt`
   - **Host**: Din HiveMQ Cloud URL (t.ex. `abc123.hivemq.cloud`)
     - ⚠️ **VIKTIGT**: Använd bara hostname UTAN protokollprefix
     - ✅ Rätt: `abc123.hivemq.cloud`
     - ❌ Fel: `mqtts://abc123.hivemq.cloud`
     - ❌ Fel: `mqtt://abc123.hivemq.cloud`
   - **Port**: `8883`
   - **Username**: Ditt HiveMQ Cloud användarnamn
   - **Password**: Ditt HiveMQ Cloud lösenord
   - **SSL/TLS**: ✅ Aktivera
   - **CA Certificate**: Lämna tom (använder systemets CA)
5. Klicka på **"Save"**

### Steg 2: Skapa ett nytt workflow i n8n

1. Öppna n8n i din webbläsare
2. Klicka på **"New Workflow"**
3. Ge workflowet ett namn (t.ex. "Voice Assistant")
4. Lägg till noderna enligt schemat nedan

### Steg 3: Lägg till MQTT Trigger Node

1. Klicka på "+" för att lägga till en ny nod
2. Sök efter **"MQTT Trigger"**
3. Konfigurera:
   - **Credentials**: Välj `HiveMQ Cloud` (som du skapade i Steg 1)
   - **Topics**: `rpi/commands/text`
   - **Client ID**: `n8n-mqtt-trigger` (valfritt)
   - **QoS**: `0` (eller högre om du behöver garanterad leverans)

**✅ Tips:** Om du använder samma HiveMQ Cloud kluster för flera n8n instanser, ge varje instans ett unikt Client ID.

### Steg 4: Lägg till processlogik

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

### Steg 5: Lägg till MQTT Publish Node

1. Lägg till en **"MQTT"** nod efter Code-noden
2. Konfigurera:
   - **Credentials**: Välj `HiveMQ Cloud` (samma som Trigger Node)
   - **Topic**: `rpi/responses/text`
   - **Message**: `={{ $json }}`
   - **QoS**: `0`
   - **Retain**: `false`

### Steg 6: Aktivera workflow

Klicka på "Active" i övre högra hörnet för att aktivera workflowet.

## 🧪 Testa MQTT-anslutningen

### Test 1: Automatisk test (rekommenderas)

Använd det medföljande testskriptet med dina HiveMQ Cloud uppgifter:

```bash
# Syntax: ./test-mqtt-connection.sh <host> <port> <username> <password>
./test-mqtt-connection.sh abc123.hivemq.cloud 8883 your-username your-password
```

Detta skript testar:
- Anslutning till MQTT broker med TLS
- Publicera och prenumerera på meddelanden
- Röstassistent topics (rpi/commands/text)

### Test 2: Manuellt meddelande

Simulera ett kommando från röstassistenten:

**För anslutning till HiveMQ Cloud:**
```bash
# Sätt dina uppgifter
MQTT_HOST="abc123.hivemq.cloud"
MQTT_USER="your-username"
MQTT_PASS="your-password"

# Publicera ett testkommando
mosquitto_pub -h $MQTT_HOST -p 8883 \
  --capath /etc/ssl/certs/ \
  -u $MQTT_USER -P $MQTT_PASS \
  -t "rpi/commands/text" \
  -m '{"text":"hej", "timestamp":"2024-01-01T12:00:00"}'
```

Lyssna på svar från n8n:

```bash
# I en separat terminal, prenumerera på svar
mosquitto_sub -h $MQTT_HOST -p 8883 \
  --capath /etc/ssl/certs/ \
  -u $MQTT_USER -P $MQTT_PASS \
  -t "rpi/responses/text" -v
```

**För lokal testning (utan TLS):**
```bash
# Publicera
mosquitto_pub -h localhost -t "rpi/commands/text" \
  -m '{"text":"hej", "timestamp":"2024-01-01T12:00:00"}'

# Prenumerera
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
- Konfigurera anslutning:
  - **Host**: Din HiveMQ Cloud URL (t.ex. `abc123.hivemq.cloud`)
  - **Port**: `8883`
  - **Protocol**: `mqtts://` (MQTT over TLS)
  - **Username**: Ditt HiveMQ Cloud användarnamn
  - **Password**: Ditt HiveMQ Cloud lösenord
  - **SSL/TLS**: ✅ Aktivera
- Prenumerera på `rpi/#` för att se all trafik

### Test 5: HiveMQ Cloud Console

Du kan också övervaka meddelanden direkt i HiveMQ Cloud konsolen:

1. Gå till din kluster-dashboard på https://console.hivemq.cloud/
2. Navigera till **"Web Client"** i sidomenyn
3. Anslut med dina credentials
4. Prenumerera på `rpi/#` eller specifika topics
5. Publicera testmeddelanden för att verifiera flödet

## 🔒 Säkerhet och Best Practices

### HiveMQ Cloud (Produktion)

HiveMQ Cloud hanterar säkerhet automatiskt:

- ✅ **TLS-kryptering**: Alltid aktiverad (port 8883)
- ✅ **Autentisering**: Användarnamn och lösenord krävs
- ✅ **Access Control**: Hantera användare via HiveMQ Cloud Console
- ✅ **Certifikat**: Hanteras automatiskt av HiveMQ

**Rekommenderade åtgärder:**
1. **Använd starka lösenord** för alla MQTT-användare
2. **Skapa separata användare** för olika enheter/tjänster
3. **Rotera lösenord** regelbundet
4. **Övervaka anslutningar** via HiveMQ Cloud Console
5. **Sätt upp alerting** för ovanlig aktivitet

### Lokal Mosquitto (Endast testning)

Om du kör lokal Mosquitto för testning och vill säkra den:

**Skapa användarnamn och lösenord:**

```bash
# Skapa lösenordsfil (första användaren)
sudo mosquitto_passwd -c /etc/mosquitto/passwd mqttuser

# Lägg till fler användare (utan -c flaggan)
sudo mosquitto_passwd /etc/mosquitto/passwd n8nuser
```

**Uppdatera Mosquitto-konfiguration:**

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

### Problem: Kan inte ansluta till HiveMQ Cloud

**Kontrollera credentials:**
```bash
# Testa anslutning med debug-flagga
mosquitto_pub -h your-cluster.hivemq.cloud -p 8883 \
  --capath /etc/ssl/certs/ \
  -u your-username -P your-password \
  -t "test" -m "hello" -d
```

**Vanliga fel:**
1. **Fel URL-format**: Kontrollera att du INTE använder protokollprefix
   - ✅ Rätt: `abc123.hivemq.cloud`
   - ❌ Fel: `mqtts://abc123.hivemq.cloud:8883`
   - ❌ Fel: `wss://abc123.hivemq.cloud:8884/mqtt`
2. **Fel användarnamn/lösenord**: Verifiera i HiveMQ Cloud Console → Access Management
3. **Fel cluster URL**: Kontrollera URL i HiveMQ Cloud Console → Overview (använd fältet märkt "URL")
4. **TLS-certifikatfel**: Se till att `ca-certificates` är installerat (`sudo apt install ca-certificates`)
5. **Port blockerad**: Kontrollera att port 8883 är öppen i din brandvägg

**Kontrollera nätverksanslutning:**
```bash
# Ping HiveMQ Cloud
ping your-cluster.hivemq.cloud

# Kontrollera TLS-anslutning
openssl s_client -connect your-cluster.hivemq.cloud:8883
```

**Kontrollera HiveMQ Cloud status:**
- Gå till HiveMQ Cloud Console
- Kontrollera att klustret är "Running" (grön status)
- Kontrollera "Connected Clients" för aktiva anslutningar

### Problem: n8n kan inte ansluta till HiveMQ Cloud

**Kontrollera n8n MQTT Credentials:**
1. I n8n, gå till **Settings** → **Credentials**
2. Hitta din HiveMQ Cloud credential
3. Klicka på "Test" för att verifiera anslutningen
4. Om testet misslyckas, kontrollera:
   - Host ska vara UTAN protokollprefix (`mqtt://`, `mqtts://`, `wss://`)
     - ✅ Rätt: `abc123.hivemq.cloud`
     - ❌ Fel: `mqtts://abc123.hivemq.cloud`
   - Port ska vara `8883`
   - SSL/TLS ska vara aktiverad
   - Username och Password ska matcha HiveMQ Cloud

**Kontrollera n8n loggar:**
```bash
# Om Docker:
docker logs n8n

# Om npm:
# Loggar visas i terminalen där n8n körs
```

### Problem: Röstassistenten kan inte ansluta

**Kontrollera .env-filen:**
```bash
cat .env | grep MQTT
```

Ska visa:
```
MQTT_HOST=your-cluster.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=your-username
MQTT_PASSWORD=your-password
MQTT_TLS=True
```

**Kör röstassistenten med debug:**
```bash
# Sätt LOG_LEVEL=DEBUG i .env
LOG_LEVEL=DEBUG python3 main.py
```

**Vanliga problem:**
1. **TLS=False**: HiveMQ Cloud kräver TLS, sätt `MQTT_TLS=True`
2. **Fel port**: Ska vara `8883`, inte `1883`
3. **Tomma credentials**: Användarnamn och lösenord får inte vara tomma

### Problem: Meddelanden går inte fram

**Kontrollera topics i HiveMQ Cloud:**
1. Gå till HiveMQ Cloud Console → Web Client
2. Anslut med dina credentials
3. Prenumerera på `#` (alla topics)
4. Publicera ett testmeddelande från röstassistenten
5. Kontrollera att meddelandet syns i Web Client

**Prenumerera via kommandorad:**
```bash
# Prenumerera på alla topics för debugging
mosquitto_sub -h your-cluster.hivemq.cloud -p 8883 \
  --capath /etc/ssl/certs/ \
  -u your-username -P your-password \
  -t "#" -v
```

**Kontrollera loggar:**
```bash
# Röstassistent:
# Sätt LOG_LEVEL=DEBUG i .env och kör
python3 main.py

# n8n:
docker logs n8n  # Om Docker
# Eller kontrollera terminal där n8n körs
```

**Vanliga orsaker:**
1. **Fel topic-namn**: Kontrollera att `rpi/commands/text` och `rpi/responses/text` används
2. **QoS-problem**: Prova att öka QoS till 1 eller 2
3. **n8n workflow inte aktivt**: Kontrollera att workflowet är aktiverat (grönt)
4. **Client ID-konflikt**: Om samma Client ID används av flera klienter, använd unika ID:n

### Problem: TLS/SSL-certifikatfel

**På Raspberry Pi/Linux:**
```bash
# Installera/uppdatera CA-certifikat
sudo apt update
sudo apt install ca-certificates -y
sudo update-ca-certificates
```

**På macOS:**
```bash
# Använd systemets certifikat
mosquitto_pub -h your-cluster.hivemq.cloud -p 8883 \
  --capath /etc/ssl/certs/ \
  -u your-username -P your-password \
  -t test -m hello
```

**Om problemet kvarstår:**
- Ladda ner HiveMQ Cloud's CA-certifikat manuellt från HiveMQ Cloud Console
- Använd `--cafile` istället för `--capath`

### Problem: Timeout vid anslutning

**Öka timeout i röstassistentens .env:**
```env
MQTT_CONNECT_TIMEOUT=30
MQTT_MAX_RETRIES=10
```

**Kontrollera nätverkslatens:**
```bash
# Testa latens till HiveMQ Cloud
ping your-cluster.hivemq.cloud

# Testa om port 8883 är öppen
nc -zv your-cluster.hivemq.cloud 8883
```

**Kontrollera brandvägg:**
- Se till att utgående trafik på port 8883 är tillåten
- Om du är bakom företagsbrandvägg, kontakta IT-avdelningen

### Problem: Lokal Mosquitto fungerar inte

**För lokal testning med Docker Compose:**
```bash
# Kontrollera status
docker compose ps

# Se loggar
docker compose logs mosquitto

# Testa anslutning
docker compose exec mosquitto mosquitto_pub -t test -m hello
```

**För systemd-installation:**
```bash
# Kontrollera status
sudo systemctl status mosquitto

# Se loggar
sudo journalctl -u mosquitto -f

# Testa konfiguration
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
```

## 📚 Ytterligare resurser

### HiveMQ Cloud
- **HiveMQ Cloud Console**: https://console.hivemq.cloud/
- **HiveMQ Cloud Documentation**: https://docs.hivemq.com/hivemq-cloud/
- **HiveMQ Cloud Pricing**: https://www.hivemq.com/cloud/ (Free tier tillgänglig)

### MQTT & n8n
- **n8n MQTT nodes**: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.mqtt/
- **MQTT protokoll**: https://mqtt.org/
- **MQTT Explorer**: https://mqtt-explorer.com/
- **Mosquitto dokumentation**: https://mosquitto.org/documentation/ (för lokal testning)

### Säkerhet
- **MQTT Security Best Practices**: https://www.hivemq.com/mqtt-security-fundamentals/
- **TLS/SSL Setup**: https://docs.hivemq.com/hivemq-cloud/security.html

## 🎉 Sammanfattning

Efter att ha följt denna guide har du:

### Med HiveMQ Cloud (Rekommenderat):
✅ Ett gratis HiveMQ Cloud konto med säker MQTT broker  
✅ TLS-krypterad kommunikation  
✅ Ingen lokal MQTT-installation att underhålla  
✅ n8n konfigurerat för MQTT-kommunikation  
✅ Röstassistenten ansluten till HiveMQ Cloud  
✅ Ett testbart end-to-end system  

### Med lokal Mosquitto (Testning):
✅ Lokal MQTT broker för offline-utveckling  
✅ n8n och Mosquitto i Docker Compose  
✅ Snabb utvecklingsmiljö  

Nu kan du börja utveckla mer avancerade röstkommandon och integrationer i n8n!

---

**🚀 Nästa steg:**
- Utforska n8n's integrationer (HTTP, webhooks, databaser, AI-tjänster)
- Skapa mer avancerade röstkommandon
- Integrera med smarta hem-system
- Lägg till användarautentisering
- Övervaka och analysera meddelanden i HiveMQ Cloud Console

**Behöver du mer hjälp?** Se [README.md](README.md) för mer information om själva röstassistenten.
