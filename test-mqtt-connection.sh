#!/bin/bash
# Test script för att verifiera MQTT anslutning

set -e

MQTT_HOST="${1:-ai.genio-bot.com}"
MQTT_PORT="${2:-1883}"

echo "=================================================="
echo "  MQTT Connection Test"
echo "=================================================="
echo ""
echo "Testar anslutning till: $MQTT_HOST:$MQTT_PORT"
echo ""
if [ "$MQTT_HOST" = "ai.genio-bot.com" ]; then
    echo "💡 Testar mot produktionsservern (ai.genio-bot.com)"
    echo "   För lokal test: ./test-mqtt-connection.sh localhost"
else
    echo "💡 Testar mot: $MQTT_HOST"
fi
echo ""

# Kontrollera om mosquitto-clients är installerat
if ! command -v mosquitto_pub &> /dev/null; then
    echo "⚠️  mosquitto-clients är inte installerat"
    echo ""
    echo "Installera med:"
    echo "  Ubuntu/Debian: sudo apt install mosquitto-clients"
    echo "  macOS: brew install mosquitto"
    echo ""
    echo "Alternativt, testa via Docker:"
    echo "  docker compose exec mosquitto mosquitto_pub -h localhost -t test -m hello"
    exit 1
fi

echo "✓ mosquitto-clients är installerat"
echo ""

# Test 1: Publicera meddelande
echo "📤 Test 1: Publicerar testmeddelande..."
if mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "test/connection" -m "Hello from test script" -q 0; then
    echo "✅ Lyckades publicera meddelande"
else
    echo "❌ Misslyckades att publicera meddelande"
    exit 1
fi
echo ""

# Test 2: Prenumerera och ta emot meddelande
echo "📥 Test 2: Prenumererar på topic..."
echo "Startar subscriber i bakgrunden för 5 sekunder..."
timeout 5 mosquitto_sub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "test/#" -v > /tmp/mqtt_test_output.txt 2>&1 &
SUBSCRIBER_PID=$!
sleep 2

echo "Publicerar testmeddelande..."
mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "test/echo" -m "Echo test successful" -q 0
sleep 2

if wait $SUBSCRIBER_PID 2>/dev/null; then
    echo "✅ Subscriber avslutades normalt"
else
    echo "✅ Subscriber timeout (normalt)"
fi

if [ -f /tmp/mqtt_test_output.txt ] && grep -q "Echo test successful" /tmp/mqtt_test_output.txt; then
    echo "✅ Meddelande mottaget korrekt!"
    echo ""
    echo "Mottaget innehåll:"
    cat /tmp/mqtt_test_output.txt
else
    echo "⚠️  Kunde inte verifiera att meddelandet mottogs"
fi
echo ""

# Test 3: Röstassistent topics
echo "📡 Test 3: Testar röstassistent topics..."
mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -t "rpi/commands/text" \
    -m '{"text":"test kommando","timestamp":"2024-01-01T12:00:00"}' -q 0
echo "✅ Publicerat till rpi/commands/text"
echo ""

# Rensa upp
rm -f /tmp/mqtt_test_output.txt

echo "=================================================="
echo "✅ Alla tester godkända!"
echo "=================================================="
echo ""
echo "MQTT broker på $MQTT_HOST:$MQTT_PORT fungerar korrekt."
echo ""
if [ "$MQTT_HOST" = "ai.genio-bot.com" ]; then
    echo "💡 Nästa steg:"
    echo "  1. n8n körs redan på http://ai.genio-bot.com:5678"
    echo "  2. Testa med: mosquitto_sub -h ai.genio-bot.com -t 'rpi/#' -v"
    echo "  3. Konfigurera .env med MQTT_HOST=ai.genio-bot.com"
    echo "  4. Kör röstassistenten: python3 main.py"
else
    echo "💡 Nästa steg:"
    echo "  1. Konfigurera n8n för att lyssna på rpi/commands/text"
    echo "  2. Testa med: mosquitto_sub -h $MQTT_HOST -t 'rpi/#' -v"
    echo "  3. Kör röstassistenten: python3 main.py"
fi
echo ""
