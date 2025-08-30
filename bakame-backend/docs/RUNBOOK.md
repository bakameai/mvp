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
    "elevenlabs_api": {"status": "healthy"}
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
ELEVENLABS_API_KEY=sk-xxxxx
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:pass@localhost/bakame_db

# Optional provider configuration
ASR_PROVIDER=whisper  # or whisper_local
```

### Provider Switching
```bash
# Switch to local providers for offline mode
export ASR_PROVIDER=whisper_local
export TTS_PROVIDER=coqui_local

# Restart service
poetry run uvicorn app.main:app --reload
```

## Voice AI Configuration

### ElevenLabs Conversational AI
The system uses ElevenLabs Conversational AI with RAG-based knowledge integration for natural, educational conversations.

**Agent Configuration:**
- Agent ID: `bakame`
- Goal: Guide offline learners through English conversation, debate, grammar, reading comprehension, and mental math
- RAG Documents: Code of the Debater, Chinua, Mental Math curriculum
- Voice Settings: Stability 0.5, Similarity Boost 0.8

**Features:**
- Context-aware conversations with student progress tracking
- Adaptive responses based on learning stage and performance
- Natural interruption handling and conversational flow

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
ELEVENLABS_API_KEY=sk-xxxxx
MCP_SERVER_URL=http://localhost:8001
```

### Voice Audition
To test different voices and select the best option:

```bash
cd bakame-backend
poetry run python scripts/tts_audit.py
```

This generates audio samples for comparison and creates a report in `docs/VOICE_CHOICES.md`.

### Call Start Flow

**Intro-First Behavior:**
- Every call starts with warm intro (≤7 seconds)
- Uses temperature 0.4 for consistent greeting
- Never opens with "I can't hear you" message
- Immediately asks for learner's name after intro

**Name Capture Process:**
1. **Name Extraction**: Uses NER patterns ("My name is X", "I am X", etc.)
2. **Confirmation**: "I heard Kevin — is that right?"
3. **Spell Mode**: Fallback for unclear names using NATO alphabet
4. **Default**: Falls back to "Friend" if all attempts fail

**Conversation States:**
- `intro`: Initial greeting and name request
- `name_capture`: Retry name collection
- `name_confirm`: Confirm extracted name
- `name_spell`: Letter-by-letter spelling mode
- `normal`: Regular learning conversation

**Silence Handling:**
- **During Name Capture**: "Take your time — please tell me your name"
- **After 2nd Silence**: Default to "Friend" and continue
- **Normal Conversation**: Standard "I didn't catch that" escalation

**Session Personalization:**
- Name stored in Redis session with 1-hour TTL
- Used throughout conversation for personalized responses
- Logged in analytics with confirmation status

### Audio Format Requirements
- **ElevenLabs Output**: High-quality audio URLs for direct Twilio playback
- **Telephony Compatibility**: Automatic format optimization by ElevenLabs
- **No Transcoding**: Direct audio streaming from ElevenLabs to Twilio

### Fallback Chain
1. **Primary**: ElevenLabs Conversational AI with audio response
2. **Secondary**: ElevenLabs text response with Twilio `<Say>`
3. **Last Resort**: Basic Twilio `<Say>` verb

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

### Curriculum System

**Bloom's Taxonomy Integration:**
- 6 stages per module: Remember → Understand → Apply → Analyze → Evaluate → Create
- 24 total curriculum files in `/docs/curriculum/{module}_{stage}.md`
- Each stage includes learning goals, skills, prompts, and assessment criteria

**Assessment System:**
- Multi-factor scoring: keyword matching (40%) + sentence structure (30%) + LLM evaluation (30%)
- Pass threshold: 60% overall score
- Advancement: 3 passes out of last 5 attempts
- Demotion: 3 consecutive failures

**Student Progression Tracking:**
- Current stages stored in Redis: `curriculum_stages.{module}`
- Assessment history: `assessment_history.{module}[]`
- Session TTL: 1 hour for active sessions, 24 hours for assessment history

**Language Scaffolding:**
- Accent-tolerant input processing
- Gentle grammar correction with meaning preservation
- Focus on communication success over perfect grammar
- Cultural context integration for Rwandan learners

**OER Resource Integration:**
- Organized by module in `/docs/resources/{module}/`
- CC-licensed educational content
- Mapped to Bloom's taxonomy stages
- Rwandan context adaptations

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
