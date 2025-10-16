# Mosquitto MQTT Broker Configuration

Denna mapp innehåller konfiguration för Mosquitto MQTT broker.

## Mappstruktur

```
mosquitto/
├── config/
│   └── mosquitto.conf    # Huvudkonfigurationsfil
├── data/                 # Persistence data (git-ignorerad)
└── log/                  # Loggfiler (git-ignorerad)
```

## Användning

### Med Docker Compose

Starta Mosquitto tillsammans med n8n:

```bash
docker compose up -d
```

### Kontrollera status

```bash
# Se loggar
docker compose logs mosquitto

# Testa anslutning
docker compose exec mosquitto mosquitto_pub -t "test" -m "hello"
```

## Konfiguration

Standard-konfigurationen (`config/mosquitto.conf`) är inställd för utveckling med:
- ✅ Anonym åtkomst tillåten
- ✅ Port 1883 (MQTT)
- ✅ Port 9001 (WebSocket)
- ✅ Persistence aktiverad
- ✅ Omfattande loggning

⚠️ **För produktion**, se [MQTT_SETUP.md](../MQTT_SETUP.md) för att aktivera autentisering.

## Säker konfiguration

För att aktivera lösenordsskydd:

1. Skapa lösenordsfil (i Docker):
```bash
docker compose exec mosquitto mosquitto_passwd -c /mosquitto/config/passwd mqttuser
```

2. Redigera `config/mosquitto.conf`:
```conf
allow_anonymous false
password_file /mosquitto/config/passwd
```

3. Starta om:
```bash
docker compose restart mosquitto
```

## Felsökning

### Kontrollera att Mosquitto körs

```bash
docker compose ps
```

### Se alla loggar

```bash
docker compose logs -f mosquitto
```

### Testa anslutning

```bash
# Inifrån container
docker compose exec mosquitto mosquitto_pub -h localhost -t "test" -m "hello"

# Från host (om mosquitto-clients installerat)
mosquitto_pub -h localhost -t "test" -m "hello"
```

### Lyssna på alla meddelanden

```bash
docker compose exec mosquitto mosquitto_sub -h localhost -t "#" -v
```

## Mer information

Se [MQTT_SETUP.md](../MQTT_SETUP.md) för komplett MQTT setup-guide.
