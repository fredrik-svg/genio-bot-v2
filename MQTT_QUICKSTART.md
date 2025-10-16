# MQTT Quick Start - Kom igång snabbt!

Detta är den snabbaste vägen till en fungerande MQTT-miljö för röstassistenten.

## 🚀 Snabbstart (5 minuter)

### Steg 1: Installera Docker

**På Raspberry Pi eller Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Logga ut och in igen för att aktivera docker-gruppen.

### Steg 2: Starta MQTT-miljön

```bash
cd genio-bot-v2
./start-mqtt-environment.sh
```

Det är allt! 🎉

Nu har du:
- ✅ **Mosquitto MQTT broker** på `localhost:1883`
- ✅ **n8n workflow automation** på `http://localhost:5678`

## 📋 Nästa steg

### 1. Testa MQTT-anslutningen

```bash
./test-mqtt-connection.sh
```

### 2. Konfigurera n8n

1. Öppna n8n i webbläsaren: http://localhost:5678
2. Logga in med:
   - Användarnamn: `admin`
   - Lösenord: `admin`
3. Skapa ett nytt workflow med:
   - **MQTT Trigger** nod (topic: `rpi/commands/text`)
   - **Code** nod (för att bearbeta kommandon)
   - **MQTT** nod (topic: `rpi/responses/text`)

Se [MQTT_SETUP.md](MQTT_SETUP.md) för detaljerad guide.

### 3. Konfigurera röstassistenten

```bash
source venv/bin/activate
python3 setup_wizard.py
```

Använd följande MQTT-inställningar:
- Host: `localhost`
- Port: `1883`
- Användarnamn: (lämna tom)
- Lösenord: (lämna tom)
- TLS: `false`

### 4. Starta röstassistenten

```bash
source venv/bin/activate
python3 main.py
```

## 💡 Vanliga kommandon

```bash
# Se loggar
docker compose logs -f

# Stoppa tjänster
docker compose down

# Starta om
docker compose restart

# Testa MQTT manuellt
docker compose exec mosquitto mosquitto_pub -h localhost -t test -m hello
```

## 🔍 Felsökning

### Tjänsterna startar inte

```bash
# Kontrollera status
docker compose ps

# Se felmeddelanden
docker compose logs
```

### MQTT-anslutning fungerar inte

```bash
# Testa anslutning
./test-mqtt-connection.sh

# Kontrollera att Mosquitto körs
docker compose exec mosquitto mosquitto_pub -h localhost -t test -m hello
```

### n8n är långsam eller svarar inte

```bash
# Starta om n8n
docker compose restart n8n

# Vänta 30 sekunder och försök igen
```

## 📚 Mer information

- **Detaljerad MQTT-guide**: [MQTT_SETUP.md](MQTT_SETUP.md)
- **Installation av röstassistent**: [README.md](README.md)
- **Snabbguide för virtuell miljö**: [QUICKSTART.md](QUICKSTART.md)

## ❓ Vanliga frågor

### Kan jag använda en annan MQTT broker?

Ja! Du kan installera Mosquitto direkt på systemet eller använda en befintlig broker. Se [MQTT_SETUP.md](MQTT_SETUP.md) för instruktioner.

### Måste jag använda n8n?

Ja, n8n är nödvändigt för att bearbeta röstkommandon och generera svar. Men du kan ersätta det med din egen backend om du vill.

### Är det säkert att köra utan lösenord?

För utveckling: Ja  
För produktion: **Nej!**

Se avsnittet "Säker konfiguration" i [MQTT_SETUP.md](MQTT_SETUP.md) för att aktivera autentisering.

### Kan jag nå MQTT från en annan dator?

Ja, men du måste:
1. Ersätta `localhost` med serverns IP-adress
2. Öppna port 1883 i brandväggen: `sudo ufw allow 1883/tcp`

---

**Behöver du mer hjälp?** Se [MQTT_SETUP.md](MQTT_SETUP.md) för komplett guide.
