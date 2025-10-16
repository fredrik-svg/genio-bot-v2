#!/bin/bash
# Quick start script för MQTT miljö (Mosquitto + n8n)

set -e

echo "=================================================="
echo "  MQTT Environment Quick Start"
echo "  Startar Mosquitto + n8n med Docker Compose"
echo "=================================================="
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
echo "✅ MQTT miljö är startad!"
echo "=================================================="
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
echo "📋 Nästa steg:"
echo "  1. Öppna n8n i din webbläsare: http://localhost:5678"
echo "  2. Konfigurera MQTT nodes enligt guiden i MQTT_SETUP.md"
echo "  3. Kör setup wizard för röstassistenten: python3 setup_wizard.py"
echo "  4. Starta röstassistenten: python3 main.py"
echo ""
echo "💡 Tips:"
echo "  • Se loggar: docker compose logs -f"
echo "  • Stoppa tjänster: docker compose down"
echo "  • Testa MQTT: mosquitto_pub -h localhost -t test -m hello"
echo ""
echo "📖 Mer information: se MQTT_SETUP.md"
echo "=================================================="
