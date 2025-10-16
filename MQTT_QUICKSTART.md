# MQTT Quick Start - Kom igång snabbt!

Detta är den snabbaste vägen till att ansluta röstassistenten till MQTT-miljön.

**🌐 VIKTIGT:** n8n och MQTT broker körs redan på **ai.genio-bot.com**. Du behöver **inte** installera något lokalt!

## 🚀 Snabbstart (2 minuter) - Anslut till ai.genio-bot.com

### Steg 1: Konfigurera röstassistenten

```bash
cd genio-bot-v2
source venv/bin/activate
python3 setup_wizard.py
```

Använd följande värden:
- **MQTT broker host**: `ai.genio-bot.com` (standard)
- **MQTT broker port**: `1883`
- Övriga värden: följ guiden

### Steg 2: Testa anslutning

```bash
# Installera mosquitto-clients om du inte har det
sudo apt install mosquitto-clients

# Testa anslutning
mosquitto_pub -h ai.genio-bot.com -t test -m "hello"
```

Det är allt! 🎉

Du är nu ansluten till:
- ✅ **Mosquitto MQTT broker** på `ai.genio-bot.com:1883`
- ✅ **n8n workflow automation** på `http://ai.genio-bot.com:5678`

## 📋 Nästa steg

### 1. Testa MQTT-anslutningen

```bash
./test-mqtt-connection.sh ai.genio-bot.com
```

### 2. Kontrollera n8n (valfritt)

n8n körs redan på servern och är tillgänglig på: http://ai.genio-bot.com:5678

Kontakta administratören för inloggningsuppgifter om du behöver ändra workflow.

### 3. Starta röstassistenten

```bash
source venv/bin/activate
python3 main.py
```

## 💡 Vanliga kommandon

```bash
# Testa MQTT-anslutning till servern
mosquitto_pub -h ai.genio-bot.com -t test -m hello

# Lyssna på meddelanden från servern
mosquitto_sub -h ai.genio-bot.com -t "rpi/#" -v

# Testa röstassistent topics
mosquitto_pub -h ai.genio-bot.com -t "rpi/commands/text" \
  -m '{"text":"hej", "timestamp":"2024-01-01T12:00:00"}'
```

## 🔍 Felsökning

### MQTT-anslutning fungerar inte

```bash
# Testa anslutning till servern
./test-mqtt-connection.sh ai.genio-bot.com

# Eller manuellt
mosquitto_pub -h ai.genio-bot.com -t test -m hello
```

### Kan inte nå servern

```bash
# Kontrollera nätverksanslutning
ping ai.genio-bot.com

# Kontrollera om port 1883 är öppen
nc -zv ai.genio-bot.com 1883
```

### n8n svarar inte

Kontakta administratören för servern ai.genio-bot.com om n8n inte fungerar.

## 📚 Mer information

- **Detaljerad MQTT-guide**: [MQTT_SETUP.md](MQTT_SETUP.md)
- **Installation av röstassistent**: [README.md](README.md)
- **Snabbguide för virtuell miljö**: [QUICKSTART.md](QUICKSTART.md)

## ❓ Vanliga frågor

### Var körs n8n och MQTT?

Båda körs på **ai.genio-bot.com**. Du behöver inte installera något lokalt.

### Kan jag testa lokalt?

Ja! Se [MQTT_SETUP.md](MQTT_SETUP.md) för instruktioner om lokal Docker Compose-installation för utveckling.

### Måste jag använda n8n?

Ja, n8n är nödvändigt för att bearbeta röstkommandon och generera svar. n8n körs redan på ai.genio-bot.com.

### Hur får jag tillgång till n8n?

n8n är tillgänglig på http://ai.genio-bot.com:5678. Kontakta administratören för inloggningsuppgifter.

### Behöver jag lösenord för MQTT?

Det beror på serverkonfigurationen. Om du får fel vid anslutning, kontakta administratören för användarnamn och lösenord.

---

## 🔧 Lokal utveckling (valfritt)

Om du vill testa lokalt istället för att använda ai.genio-bot.com:

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
- MQTT broker: `localhost:1883`
- n8n: `http://localhost:5678`

### Steg 3: Konfigurera för lokal användning

Kör `python3 setup_wizard.py` och använd `localhost` istället för `ai.genio-bot.com`.

---

**Behöver du mer hjälp?** Se [MQTT_SETUP.md](MQTT_SETUP.md) för komplett guide.
