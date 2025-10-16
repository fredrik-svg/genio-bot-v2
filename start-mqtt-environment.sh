#!/bin/bash
# Quick start script för MQTT miljö (Mosquitto + n8n)
# Detta är för LOKAL utveckling och testning

set -e

echo "=================================================="
echo "  MQTT Environment Quick Start (LOKAL TESTNING)"
echo "  Startar Mosquitto + n8n med Docker Compose"
echo "=================================================="
echo ""
echo "⚠️  VIKTIGT: Detta är för LOKAL utveckling!"
echo "    I produktionsmiljön körs allt på ai.genio-bot.com"
echo "    Anslut direkt dit för normal användning."
echo ""
read -p "Vill du fortsätta med lokal installation? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Avbrutet. Se MQTT_QUICKSTART.md för anslutning till ai.genio-bot.com"
    exit 0
fi
echo ""

# Kontrollera att Docker är installerat
if ! command -v docker &> /dev/null; then
    echo "❌ Docker är inte installerat!"
    echo "Installera Docker först: https://docs.docker.com/get-docker/"
    exit 1
fi

# Kontrollera att Docker Compose är installerat
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose är inte installerat!"
    echo "Installera Docker Compose först."
    exit 1
fi

echo "✓ Docker och Docker Compose är installerade"
echo ""

# Skapa nödvändiga mappar
echo "📁 Skapar mappar för persistence..."
mkdir -p mosquitto/data mosquitto/log n8n-data

# Sätt rätt ägare för n8n-data (UID 1000 = n8n container user)
# Detta krävs för att n8n ska kunna skriva till mappen
if [ -d "n8n-data" ]; then
    if [ "$(uname)" = "Linux" ]; then
        # På Linux, försök sätta rätt ägare
        if command -v sudo &> /dev/null; then
            sudo chown -R 1000:1000 n8n-data 2>/dev/null || true
        fi
    fi
fi

echo "✓ Mappar skapade"
echo ""

# Starta tjänsterna
echo "🚀 Startar Mosquitto och n8n..."
docker compose up -d

echo ""
echo "⏳ Väntar på att tjänsterna ska starta..."
sleep 5

# Kontrollera status
echo ""
echo "📊 Status:"
docker compose ps

echo ""
echo "=================================================="
echo "✅ Lokal MQTT miljö är startad!"
echo "=================================================="
echo ""
echo "⚠️  Du kör nu en LOKAL testmiljö"
echo ""
echo "Tjänster:"
echo "  • Mosquitto MQTT Broker:"
echo "    - MQTT: localhost:1883"
echo "    - WebSocket: localhost:9001"
echo "  • n8n Workflow Automation:"
echo "    - URL: http://localhost:5678"
echo "    - Användarnamn: admin"
echo "    - Lösenord: admin"
echo ""
echo "📋 Nästa steg för lokal testning:"
echo "  1. Öppna n8n i din webbläsare: http://localhost:5678"
echo "  2. Konfigurera MQTT nodes enligt guiden i MQTT_SETUP.md"
echo "  3. Kör setup wizard: python3 setup_wizard.py"
echo "     VIKTIGT: Använd 'localhost' som MQTT host (inte ai.genio-bot.com)"
echo "  4. Starta röstassistenten: python3 main.py"
echo ""
echo "💡 Tips:"
echo "  • Se loggar: docker compose logs -f"
echo "  • Stoppa tjänster: docker compose down"
echo "  • Testa MQTT: mosquitto_pub -h localhost -t test -m hello"
echo ""
echo "📖 Mer information: se MQTT_SETUP.md"
echo ""
echo "⚠️  För produktionsanvändning: Anslut till ai.genio-bot.com istället!"
echo "=================================================="
