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
