# Fix för MQTT Connection Timeout

## Problemet

Användare fick följande fel vid anslutning till MQTT broker:

```
[INFO] Ansluter till MQTT broker 7dab69000883410aba47967fb078d6d9.s1.eu.hivemq.cloud:8883 (försök 5/5)
[WARNING] MQTT anslutning timeout
```

Efter 5 försök kunde inte applikationen ansluta till HiveMQ Cloud MQTT broker, trots att konfigurationen var korrekt.

## Grundorsaken

Problemet fanns i `mqtt_client.py` i metoden `connect()`. 

**Tidigare beteende:**
1. `connect()` anropade `self._client.connect()` för att initiera anslutning
2. Metoden väntade sedan på att `self._connected` skulle bli `True`
3. Men `self._connected` sattes av `_on_connect` callback
4. **PROBLEMET**: Callback kunde aldrig köras eftersom nätverkslooppen inte var startad!
5. Resultat: Timeout efter 10 sekunder

**Varför hände detta?**
- MQTT-biblioteket (paho-mqtt) kräver att `loop_start()` körs för att processa nätverkshändelser
- Utan en körande loop kan callbacks (som `_on_connect`) aldrig anropas
- Applikationen anropade `loop_start()` i `main.py` EFTER att `connect()` hade returnerats
- Men `connect()` väntade på callback som aldrig kunde köras = deadlock-liknande situation

## Lösningen

### Ändringar i `mqtt_client.py`

#### 1. Lagt till `_loop_started` flagga
```python
def __init__(self, ...):
    # ...
    self._connected = False
    self._loop_started = False  # NY: Håller reda på om loopen är startad
```

#### 2. Gjort `loop_start()` idempotent
```python
def loop_start(self) -> None:
    """Starta MQTT nätverksloop i separat tråd."""
    if not self._loop_started:  # NY: Kontrollera innan start
        self._client.loop_start()
        self._loop_started = True
```

Nu kan `loop_start()` anropas flera gånger utan problem - den startar bara en gång.

#### 3. Gjort `loop_stop()` säker
```python
def loop_stop(self) -> None:
    """Stoppa MQTT nätverksloop."""
    try:
        if self._loop_started:  # NY: Kontrollera innan stopp
            self._client.loop_stop()
            self._loop_started = False
    except Exception as e:
        logging.error(f"Fel vid stopp av MQTT loop: {e}")
```

#### 4. Startat loop i `connect()` metoden
```python
def connect(self, retries: int = 5, backoff: float = 2.0, timeout: int = 10) -> bool:
    """Anslut till MQTT broker med exponentiell backoff."""
    # NY: Starta nätverksloop om den inte redan är startad
    self.loop_start()
    
    for attempt in range(1, retries + 1):
        try:
            logging.info(f"Ansluter till MQTT broker {self.host}:{self.port} (försök {attempt}/{retries})")
            self._client.connect(self.host, self.port, keepalive=60)
            
            # Vänta på anslutning (callback kan nu köras!)
            start_time = time.time()
            while not self._connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self._connected:
                logging.info("MQTT anslutning etablerad")
                return True
            # ...
```

### Ändringar i `main.py`

Tagit bort onödig `loop_start()` anrop:
```python
# FÖRE:
if not self.mqtt.connect(retries=config.MQTT_MAX_RETRIES, timeout=config.MQTT_CONNECT_TIMEOUT):
    raise ConnectionError("Kunde inte ansluta till MQTT-broker")
    
self.mqtt.loop_start()  # <-- Denna rad togs bort
self.mqtt.subscribe(config.MQTT_TOPIC_RESPONSES)

# EFTER:
if not self.mqtt.connect(retries=config.MQTT_MAX_RETRIES, timeout=config.MQTT_CONNECT_TIMEOUT):
    raise ConnectionError("Kunde inte ansluta till MQTT-broker")
    
self.mqtt.subscribe(config.MQTT_TOPIC_RESPONSES)  # loop redan startad!
```

## Fördelar med Lösningen

### 1. **Löser timeout-problemet**
Nätverkslooppen startas INNAN `connect()` väntar på callback, så callbacks kan processas direkt.

### 2. **Enklare API**
Användare av `MqttClient` behöver inte tänka på när `loop_start()` ska anropas - det hanteras automatiskt.

### 3. **Säker och robust**
- `loop_start()` kan anropas flera gånger utan problem
- `loop_stop()` kontrollerar att loopen är startad innan stopp
- Ingen risk för race conditions

### 4. **Bakåtkompatibel**
Om någon annan del av koden fortfarande anropar `loop_start()` fungerar det ändå - metoden är nu idempotent.

## Testresultat

### Enhetstester
```
✓ Network loop starts during connect() call
✓ Multiple loop_start() calls are safe (idempotent)
✓ loop_stop() properly stops and resets flag
```

### Integrationstester
```
✓ Connection successful: True
✓ Client connected: True
✓ Network loop started: True
✓ loop_start() was called: True
```

## Flödesdiagram

### FÖRE (Timeout)
```
1. main.py: mqtt.connect()
2. mqtt_client.py: connect()
   └─> _client.connect()
   └─> wait for _connected flag...
       └─> [TIMEOUT] callback aldrig anropad
3. main.py: mqtt.loop_start()  <-- För sent!
```

### EFTER (Fungerande)
```
1. main.py: mqtt.connect()
2. mqtt_client.py: connect()
   └─> loop_start()  <-- NYTT: Startar loopen först
       └─> _client.loop_start()
   └─> _client.connect()
   └─> wait for _connected flag...
       └─> [SUCCESS] callback anropas av loopen!
3. main.py: mqtt.subscribe(...)  <-- Fortsätter direkt
```

## Verifiering

### Före fix:
```bash
$ python3 main.py
[INFO] Ansluter till MQTT broker xxx.hivemq.cloud:8883 (försök 1/5)
[WARNING] MQTT anslutning timeout
[INFO] Väntar 2.0s innan nästa försök...
[INFO] Ansluter till MQTT broker xxx.hivemq.cloud:8883 (försök 2/5)
[WARNING] MQTT anslutning timeout
...
RuntimeError: Kunde inte initialisera MQTT: Kunde inte ansluta till MQTT-broker
```

### Efter fix:
```bash
$ python3 main.py
[INFO] Ansluter till MQTT broker xxx.hivemq.cloud:8883 (försök 1/5)
[INFO] MQTT anslutning etablerad
✓ MQTT-kommunikation initialiserad
Lyssnar efter wakeword... (Tryck Ctrl+C för att avsluta)
```

## Sammanfattning

**Problem:** MQTT timeout på grund av att nätverkslooppen inte startades innan `connect()` väntade på callbacks.

**Lösning:** 
- Starta nätverkslooppen automatiskt i `connect()` metoden
- Gör `loop_start()` och `loop_stop()` säkra att anropa flera gånger
- Ta bort onödig `loop_start()` från applikationskod

**Resultat:** MQTT-anslutning fungerar nu korrekt och användaren kan ansluta till HiveMQ Cloud utan timeout!

---

**Ändringar:** 2 filer ändrade, 10 rader tillagda, 3 rader borttagna  
**Teststatus:** ✅ Alla tester godkända  
**Bakåtkompatibilitet:** ✅ Fullt bakåtkompatibel
