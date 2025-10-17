# HiveMQ Cloud URL Guide - Vilken URL ska jag använda?

## Problemet

När du konfigurerar HiveMQ Cloud visar dashboard tre olika URLs:

1. **URL**: `abc123.hivemq.cloud`
2. **TLS MQTT URL**: `mqtts://abc123.hivemq.cloud:8883`
3. **TLS Websocket URL**: `wss://abc123.hivemq.cloud:8884/mqtt`

Detta kan skapa förvirring om vilken URL som ska användas.

## Lösningen

**För denna röstassistent måste du alltid använda den enkla cluster URL:en (fält #1 - "URL").**

### ✅ RÄTT Format

```
abc123.hivemq.cloud
```

Använd bara hostname UTAN:
- ❌ Protokollprefix (`mqtt://`, `mqtts://`, `wss://`)
- ❌ Port (`:8883`, `:8884`)
- ❌ Path (`/mqtt`)

### ❌ FEL Format

```
mqtts://abc123.hivemq.cloud:8883        # FEL - innehåller protokoll och port
wss://abc123.hivemq.cloud:8884/mqtt     # FEL - websocket URL
abc123.hivemq.cloud:8883                # FEL - innehåller port
```

## Varför?

MQTT-klienten (`paho-mqtt` i Python) hanterar själv:
- Protokollet (MQTT/MQTTS baserat på TLS-inställningen)
- Porten (specificeras separat som 8883)
- Anslutningslogiken

Om du inkluderar protokoll eller port i hostname kan det orsaka anslutningsfel.

## I Praktiken

### 1. I HiveMQ Cloud Dashboard

Titta på kluster-dashboard och kopiera värdet från fältet märkt **"URL"**:

```
┌─────────────────────────────────────────┐
│ Cluster: my-voice-assistant             │
├─────────────────────────────────────────┤
│ URL: abc123.hivemq.cloud          ← DENNA! │
│ TLS MQTT URL: mqtts://...         ← EJ DENNA │
│ TLS Websocket URL: wss://...      ← EJ DENNA │
└─────────────────────────────────────────┘
```

### 2. I Setup Wizard

När du kör `python3 setup_wizard.py`:

```bash
HiveMQ Cloud cluster URL (bara hostname, t.ex. abc123.hivemq.cloud): abc123.hivemq.cloud
```

Om du av misstag anger fel format kommer setup wizard automatiskt att korrigera det:

```bash
HiveMQ Cloud cluster URL: mqtts://abc123.hivemq.cloud:8883
ℹ️  URL korrigerad automatiskt: mqtts://abc123.hivemq.cloud:8883 → abc123.hivemq.cloud
```

### 3. I .env-filen

Din `.env`-fil ska se ut så här:

```env
MQTT_HOST=abc123.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=din-username
MQTT_PASSWORD=ditt-lösenord
MQTT_TLS=True
```

**INTE:**

```env
# ❌ FEL!
MQTT_HOST=mqtts://abc123.hivemq.cloud:8883
```

### 4. I n8n MQTT Credentials

När du konfigurerar MQTT-noder i n8n:

- **Host**: `abc123.hivemq.cloud` ✅
- **Port**: `8883`
- **Protocol**: `mqtt` (välj från dropdown)
- **SSL/TLS**: Aktivera ✅

**INTE:**

- **Host**: `mqtts://abc123.hivemq.cloud` ❌

## Vanliga Fel och Lösningar

### Fel: `ConnectionError: Kunde inte ansluta till MQTT-broker`

**Orsak:** URL-formatet är fel

**Lösning:** Kontrollera att `MQTT_HOST` i `.env` är bara hostname:

```bash
# Kontrollera din .env
cat .env | grep MQTT_HOST

# Ska visa:
# MQTT_HOST=abc123.hivemq.cloud

# INTE:
# MQTT_HOST=mqtts://abc123.hivemq.cloud:8883
```

**Åtgärd:** Kör `python3 setup_wizard.py` igen och ange rätt format, eller redigera `.env` manuellt.

### Fel: `getaddrinfo failed` eller `Name or service not known`

**Orsak:** Ofta orsakad av att protokollprefix inkluderats i hostname

**Lösning:** Ta bort alla protokoll och portar från `MQTT_HOST`

### Fel: n8n kan inte ansluta till HiveMQ Cloud

**Orsak:** Fel format i n8n MQTT credentials

**Lösning:**
1. Gå till n8n → Settings → Credentials
2. Redigera din MQTT credential
3. Se till att **Host** är bara `abc123.hivemq.cloud` (utan `mqtts://`)
4. Klicka på "Test" för att verifiera
5. Spara

## Sammanfattning

**Kom ihåg:**

| Fält | Värde | Förklaring |
|------|-------|------------|
| MQTT_HOST | `abc123.hivemq.cloud` | Bara hostname |
| MQTT_PORT | `8883` | TLS-port (separat fält) |
| MQTT_TLS | `True` | Aktiverar MQTTS automatiskt |

**Setup wizard hjälper dig** genom att automatiskt korrigera fel format!

## Behöver du mer hjälp?

- Se [MQTT_QUICKSTART.md](MQTT_QUICKSTART.md) för snabbguide
- Se [MQTT_SETUP.md](MQTT_SETUP.md) för detaljerad guide
- Se [HIVEMQ_CLOUD.md](HIVEMQ_CLOUD.md) för komplett HiveMQ Cloud guide
- Kontrollera felsökningssektionen i [MQTT_SETUP.md](MQTT_SETUP.md#felsökning)
