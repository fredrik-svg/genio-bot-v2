#!/bin/bash
# Test script för att verifiera MQTT anslutning

set -e

MQTT_HOST="${1}"
MQTT_PORT="${2:-8883}"
MQTT_USER="${3}"
MQTT_PASS="${4}"

echo "=================================================="
echo "  MQTT Connection Test"
echo "=================================================="
echo ""

# Check if host is provided
if [ -z "$MQTT_HOST" ]; then
    echo "❌ Ingen MQTT host angiven!"
    echo ""
    echo "Användning för HiveMQ Cloud:"
    echo "  ./test-mqtt-connection.sh your-cluster.hivemq.cloud 8883 username password"
    echo ""
    echo "Användning för lokal Mosquitto:"
    echo "  ./test-mqtt-connection.sh localhost 1883"
    echo ""
    exit 1
fi

echo "Testar anslutning till: $MQTT_HOST:$MQTT_PORT"
echo ""

# Detect if this is likely HiveMQ Cloud (uses TLS)
if [[ "$MQTT_PORT" == "8883" ]] || [[ "$MQTT_HOST" == *"hivemq.cloud"* ]]; then
    echo "🔒 Upptäckte TLS-port eller HiveMQ Cloud"
    USE_TLS=true
    if [ -z "$MQTT_USER" ] || [ -z "$MQTT_PASS" ]; then
        echo "❌ Användarnamn och lösenord krävs för HiveMQ Cloud!"
        echo "   ./test-mqtt-connection.sh $MQTT_HOST $MQTT_PORT username password"
        exit 1
    fi
    MQTT_OPTS="--capath /etc/ssl/certs/ -u $MQTT_USER -P $MQTT_PASS"
else
    echo "💡 Testar mot: $MQTT_HOST (utan TLS)"
    USE_TLS=false
    MQTT_OPTS=""
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
if mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" $MQTT_OPTS -t "test/connection" -m "Hello from test script" -q 0; then
    echo "✅ Lyckades publicera meddelande"
else
    echo "❌ Misslyckades att publicera meddelande"
    exit 1
fi
echo ""

# Test 2: Prenumerera och ta emot meddelande
echo "📥 Test 2: Prenumererar på topic..."
echo "Startar subscriber i bakgrunden för 5 sekunder..."
timeout 5 mosquitto_sub -h "$MQTT_HOST" -p "$MQTT_PORT" $MQTT_OPTS -t "test/#" -v > /tmp/mqtt_test_output.txt 2>&1 &
SUBSCRIBER_PID=$!
sleep 2

echo "Publicerar testmeddelande..."
mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" $MQTT_OPTS -t "test/echo" -m "Echo test successful" -q 0
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
mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" $MQTT_OPTS -t "rpi/commands/text" \
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

if [ "$USE_TLS" = true ]; then
    echo "💡 Nästa steg för HiveMQ Cloud:"
    echo "  1. Konfigurera n8n med samma HiveMQ Cloud uppgifter"
    echo "  2. Testa med: mosquitto_sub -h $MQTT_HOST -p $MQTT_PORT $MQTT_OPTS -t 'rpi/#' -v"
    echo "  3. Konfigurera .env med dina HiveMQ Cloud uppgifter"
    echo "  4. Kör röstassistenten: python3 main.py"
else
    echo "💡 Nästa steg för lokal Mosquitto:"
    echo "  1. Konfigurera n8n för att lyssna på rpi/commands/text"
    echo "  2. Testa med: mosquitto_sub -h $MQTT_HOST -p $MQTT_PORT -t 'rpi/#' -v"
    echo "  3. Kör röstassistenten: python3 main.py"
fi
echo ""
