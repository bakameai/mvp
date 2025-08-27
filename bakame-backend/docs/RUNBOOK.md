# BAKAME IVR Operations Runbook

## Local Development Setup

### Prerequisites
- Python 3.12+
- Poetry
- Redis server
- PostgreSQL database

### Installation
```bash
cd bakame-backend
poetry install
cp .env.template .env
# Edit .env with your API keys
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Running Latency Tests
```bash
cd bakame-backend
poetry run python scripts/sim_call.py
```

## Twilio Media Streams Configuration

### Enable Media Streams
1. In Twilio Console, go to Voice → TwiML Apps
2. Create new TwiML App with webhook URL: `https://your-domain.com/webhook/call`
3. Enable Media Streams in your TwiML response
4. Set WebSocket URL: `wss://your-domain.com/webhook/media-stream`

### Testing Barge-in
1. Make a call to your Twilio number
2. Wait for AI response to start playing
3. Speak during the response
4. Verify that playback stops and system listens

## Monitoring & Metrics

### Health Check
```bash
curl https://your-domain.com/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "service": "BAKAME MVP",
  "checks": {
    "redis": {"status": "healthy"},
    "database": {"status": "healthy"},
    "llama_api": {"status": "healthy"},
    "openai_api": {"status": "healthy"},
    "deepgram_api": {"status": "healthy"}
  }
}
```

### Metrics Collection
- **CSV Location**: `user_sessions.csv` in backend root
- **Database**: PostgreSQL `user_sessions` table
- **Rotation**: CSV rotated daily (implement as needed)

### Key Metrics to Monitor
- `asr_ms` - Speech recognition latency
- `llm_ms` - AI response generation time
- `tts_ms` - Text-to-speech conversion time
- `total_ms` - End-to-end response time
- `error` - Error messages and types

## Common Failure Modes & Fixes

### 1. High Latency (>5000ms total)
**Symptoms**: Slow responses, user complaints
**Investigation**:
```bash
# Check recent metrics
tail -n 100 user_sessions.csv | grep "turn_metrics"

# Check health status
curl https://your-domain.com/healthz
```
**Fixes**:
- Restart services if unhealthy
- Check network connectivity to APIs
- Verify API key validity

### 2. Circuit Breaker Open
**Symptoms**: All requests falling back to OpenAI
**Investigation**:
```bash
# Check logs for circuit breaker messages
grep "Circuit breaker OPENED" app.log
```
**Fixes**:
- Wait 2 minutes for auto-recovery
- Check Llama API status
- Verify API credentials

### 3. Barge-in Not Working
**Symptoms**: Users can't interrupt AI responses
**Investigation**:
- Verify Media Streams WebSocket connection
- Check Redis for barge-in flags
- Test VAD sensitivity
**Fixes**:
- Restart WebSocket service
- Adjust VAD threshold in `media_stream.py`
- Verify Twilio Media Streams configuration

### 4. PII Leakage in Logs
**Symptoms**: Phone numbers/emails visible in logs
**Investigation**:
```bash
# Check for unredacted PII
grep -E "\+\d{10,}" user_sessions.csv
grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" user_sessions.csv
```
**Fixes**:
- Verify redaction utility is working
- Update PII patterns if needed
- Manually clean sensitive logs

## Configuration Management

### Environment Variables
```bash
# Required for production
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890
OPENAI_API_KEY=sk-xxxxx
LLAMA_API_KEY=xxxxx
DEEPGRAM_API_KEY=xxxxx
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:pass@localhost/bakame_db

# Optional provider configuration
ASR_PROVIDER=whisper  # or whisper_local
TTS_PROVIDER=deepgram  # or coqui_local
```

### Provider Switching
```bash
# Switch to local providers for offline mode
export ASR_PROVIDER=whisper_local
export TTS_PROVIDER=coqui_local

# Restart service
poetry run uvicorn app.main:app --reload
```

## TTS Configuration

### Voice Selection
The system uses Deepgram Aura-2 male voices for warm, kid-friendly speech synthesis.

**Default Configuration:**
- Voice: `aura-2-aries-en` (warm, energetic, caring male voice)
- Rate: `0.95` (slightly slower for clarity)
- Pitch: `-1st` (deeper pitch for male voice warmth)
- Style: `conversational`

**Available Male Voices:**
- `aura-2-aries-en`: Warm, Energetic, Caring (recommended for kids)
- `aura-2-arcas-en`: Natural, Smooth, Clear
- `aura-2-apollo-en`: Confident, Comfortable

### Dynamic Temperature Control

**Temperature Settings by Conversation State:**
- Welcome Message: `0.4` (consistent, steady greeting)
- Normal Conversation: `0.9` (less variance, kid-friendly)
- Rwanda Fun Facts: `1.6` (creative, varied presentation)

### Sentiment Analysis

**Sentiment Detection:**
- Analyzes user speech for frustration indicators
- Adjusts TTS rate to 0.85 for frustrated users (slower, more patient)
- Provides encouraging responses for frustrated learners

**Frustration Indicators:**
- Negative words (no, can't, don't, won't)
- Difficulty expressions (hard, confusing, stuck)
- Low speech confidence scores
- Quick, short responses

### Accent Recovery

**Missing Word Fill:**
- Automatically corrects incomplete sentences
- Provides gentle feedback: "Good try! I filled in the missing word 'to'."
- Maintains original meaning while improving grammar

### Rwanda Facts Rotation

**Session End Facts:**
- Rotates through 20+ Rwanda facts
- Uses high temperature (1.6) for creative presentation
- Avoids repeating recently used facts
- Fallback to simple fact if AI generation fails

**Environment Variables:**
```bash
TTS_PROVIDER=deepgram
TTS_VOICE=aura-2-aries-en
TTS_RATE=0.95
TTS_PITCH=-1st
TTS_STYLE=conversational
```

### Voice Audition
To test different voices and select the best option:

```bash
cd bakame-backend
poetry run python scripts/tts_audit.py
```

This generates audio samples for comparison and creates a report in `docs/VOICE_CHOICES.md`.

### Audio Format Requirements
- **Telephony Standard**: 8kHz mono μ-law (PCM u-law)
- **Source Quality**: 22kHz linear16 from Deepgram
- **Transcoding**: Automatic conversion via FFmpeg

### Fallback Chain
1. **Primary**: Deepgram Aura TTS
2. **Secondary**: OpenAI TTS (if available)
3. **Last Resort**: Twilio `<Say>` verb

### Barge-in Configuration
- **Sentence Chunking**: Automatic splitting on sentence boundaries
- **Micro-pauses**: 200ms between sentences
- **Interruption**: Redis flags enable mid-sentence barge-in
- **Response Time**: ≤250ms interruption detection

### Testing TTS Pipeline
```bash
# Test Deepgram API with corrected parameters
poetry run python -c "
import asyncio
from app.services.deepgram_service import deepgram_service

async def test_tts():
    result = await deepgram_service.text_to_speech('Hello, this is a test!')
    print(f'TTS result: {result}')

asyncio.run(test_tts())
"

# Test complete TTS pipeline with fallback
poetry run python -c "
import asyncio
from app.services.twilio_service import twilio_service

async def test_pipeline():
    response = await twilio_service.create_voice_response('Welcome to BAKAME!')
    print('TwiML Response:')
    print(response)

asyncio.run(test_pipeline())
"

# Validate audio format
poetry run python -c "
from app.utils.audio_transcode import validate_telephony_audio
print(validate_telephony_audio('/tmp/test_telephony.wav'))
"
```

### Troubleshooting
- **Deepgram API Errors**: Check encoding parameter (must be 'linear16', not 'wav')
- **Audio Format Issues**: Verify FFmpeg installation and μ-law codec support
- **Barge-in Problems**: Check Redis connectivity and session flag management
- **Fallback Failures**: Verify OpenAI API key and service availability

## Backup & Recovery

### Database Backup
```bash
pg_dump bakame_db > backup_$(date +%Y%m%d).sql
```

### CSV Backup
```bash
cp user_sessions.csv backup/user_sessions_$(date +%Y%m%d).csv
```

### Redis Backup
```bash
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb backup/redis_$(date +%Y%m%d).rdb
```
