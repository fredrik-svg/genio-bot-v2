# Förbättring av Speech-to-Text Precision efter Wakeword-Detektering

## Problem
Efter att wakeword detekterades hade appen svårt att uppfatta vad som sades. Ofta tolkades bara enstaka ord korrekt, vilket gjorde röstassistenten opålitlig.

## Analys
Problemet berodde på flera faktorer:

1. **Feedback-ljudets interferens**: När wakeword detekterades spelades ett feedback-ljud (`start_listen.wav`) upp, men inspelningen startade omedelbart efter utan att vänta på att ljudet skulle spelas klart. Detta innebar att:
   - Feedback-ljudet kunde höras av mikrofonen under inspelning
   - Användaren började prata samtidigt som feedback-ljudet spelades
   - Vosk STT-modellen fick blandad input (feedback + tal)

2. **Audio stream instabilitet**: Efter att en ljudström öppnades kunde de första millisekunder innehålla:
   - Ofullständig data
   - Brus från systemet
   - "Click"-ljud från mikrofonen som aktiveras

3. **STT-precision**: Vosk STT användes utan word-level detaljer, vilket minskade precisionen.

## Lösning

### 1. Delay efter feedback-ljud (AUDIO_FEEDBACK_DELAY)
**Fil**: `main.py`, metod `_handle_voice_command()`

```python
# Spela feedback-ljud
self.audio.play_wav("audio_feedback/start_listen.wav")

# Vänta på att ljudet ska spelas klart
time.sleep(config.AUDIO_FEEDBACK_DELAY)  # Default: 0.3 sekunder

# Nu är det säkert att börja spela in
audio = self.audio.record(config.RECORD_SECONDS_AFTER_WAKE)
```

Detta förhindrar att feedback-ljudet stör inspelningen och ger användaren tid att börja prata efter ljudsignalen.

### 2. Stream stabilisering (AUDIO_STREAM_STABILIZE_DELAY)
**Fil**: `audio_utils.py`, metod `record()`

```python
# Öppna ljudström
stream = self.pa.open(...)

# Vänta på att strömmen stabiliseras
time.sleep(self.stream_stabilize_delay)  # Default: 0.1 sekunder

# Nu är strömmen redo att spela in ren ljuddata
frames = []
for _ in range(num_chunks):
    data = stream.read(chunk)
    ...
```

Detta säkerställer att de första chunks som spelas in innehåller ren användarröst utan brus.

### 3. Förbättrad STT-precision
**Fil**: `main.py`, metod `_handle_voice_command()`

```python
rec = KaldiRecognizer(self.vosk_model, config.SAMPLE_RATE)
rec.SetWords(True)  # Aktivera ordnivå-detaljer för bättre precision
```

Genom att aktivera word-level detaljer i Vosk får vi:
- Bättre ordgränser
- Mer exakt timing
- Förbättrad övergripande precision

## Konfiguration

Nya miljövariabler i `.env`:

```bash
# Fördröjning efter feedback-ljud innan inspelning (sekunder)
AUDIO_FEEDBACK_DELAY=0.3

# Fördröjning efter att ljudström öppnats (sekunder)
AUDIO_STREAM_STABILIZE_DELAY=0.1
```

Dessa värden kan justeras beroende på:
- **Hårdvara**: Snabbare system kan använda kortare delays
- **Feedback-ljud**: Längre feedback-ljud kräver längre AUDIO_FEEDBACK_DELAY
- **Mikrofon**: Vissa mikrofoner behöver mer tid att stabiliseras

## Testning

För att verifiera förbättringen:

1. **Starta applikationen**:
   ```bash
   source venv/bin/activate
   python3 main.py
   ```

2. **Testa wakeword-detektering**:
   - Säg wakeword (t.ex. "assistans")
   - Vänta på feedback-ljudet
   - Säg ett kommando (t.ex. "Vad är klockan?")

3. **Observera loggarna**:
   ```
   🎤 Wakeword detekterat!
   Spelar in...
   Transkriberar...
   📝 Transkriberat: 'vad är klockan'  <-- Ska nu vara mer komplett
   ✓ Kommando skickat till n8n
   ```

## Förväntade resultat

- **Före fix**: "vad klockan", "klockan", "vad" (ofullständiga transkriptioner)
- **Efter fix**: "vad är klockan" (fullständig, korrekt transkription)

## Finjustering

Om problem kvarstår, prova att justera delays:

```bash
# För långsammare system eller längre feedback-ljud
AUDIO_FEEDBACK_DELAY=0.5

# För mikrofoner med mer brus vid start
AUDIO_STREAM_STABILIZE_DELAY=0.2
```

## Tekniska detaljer

### Timing-diagram (före fix)
```
Wakeword detekterat
│
├─ play_wav() börjar spela feedback
│  └─ Tar ~300ms att spela klart
│
├─ record() börjar OMEDELBART (problem!)
│  └─ Spelar in feedback-ljud + användarens röst (blandad)
│
└─ STT får förvirrad input → dålig precision
```

### Timing-diagram (efter fix)
```
Wakeword detekterat
│
├─ play_wav() börjar spela feedback
│  └─ Tar ~300ms att spela klart
│
├─ time.sleep(0.3) väntar på feedback
│
├─ record() öppnar stream
│  └─ time.sleep(0.1) väntar på stabilisering
│
├─ record() börjar spela in REN användarröst
│
└─ STT får tydlig input → hög precision
```

## Modifierade filer

1. **config.py**: Lade till AUDIO_FEEDBACK_DELAY och AUDIO_STREAM_STABILIZE_DELAY
2. **main.py**: Lade till delay efter feedback-ljud och SetWords(True) för STT
3. **audio_utils.py**: Lade till stream_stabilize_delay parameter och implementation
4. **.env.example**: Dokumenterade nya konfigurationsalternativ

## Säkerhet & Prestanda

- **Minimal overhead**: Totalt ~400ms extra delay per röstkommando
- **Konfigurerbar**: Kan justeras per installation
- **Ingen ändring i arkitektur**: Inga breaking changes
- **Bakåtkompatibel**: Default-värden fungerar utan .env-uppdatering
