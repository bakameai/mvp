# BAKAME IVR Metrics Specification

## CSV Schema

### Enhanced User Sessions CSV
**File**: `user_sessions.csv`
**Rotation**: Daily (implement as needed)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| timestamp | ISO 8601 | Interaction timestamp | 2024-01-15T10:30:45.123Z |
| phone_number | String | User phone number (preserved for joining) | +250788123456 |
| session_id | String | Unique session identifier | session_001 |
| module_name | String | Learning module or "metrics" | english, math, metrics |
| interaction_type | String | Type of interaction | voice, sms, turn_metrics |
| user_input | String | User input (PII redacted) | Hello, I want to learn [PHONE_REDACTED] |
| ai_response | String | AI response (PII redacted) | Great! Let's start with basic vocabulary |
| session_duration | Float | Duration in seconds | 45.67 |
| emotional_data | String | Emotional analysis data | {"sentiment": "positive"} |
| gamification_data | String | Gamification data | {"points": 10, "level": 2} |
| call_id | String | Twilio call identifier | CAxxxxx |
| turn | Integer | Turn number in conversation | 1, 2, 3... |
| asr_ms | Float | ASR processing time (milliseconds) | 234.56 |
| llm_ms | Float | LLM processing time (milliseconds) | 1234.78 |
| tts_ms | Float | TTS processing time (milliseconds) | 456.89 |
| total_ms | Float | Total processing time (milliseconds) | 1926.23 |
| tokens_in | Integer | Input tokens to LLM | 25 |
| tokens_out | Integer | Output tokens from LLM | 45 |
| asr_confidence | Float | ASR confidence score (0-1) | 0.95 |
| error | String | Error message if any | Connection timeout |

## Database Schema

### UserSession Table
```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    module_name VARCHAR(50) NOT NULL,
    interaction_type VARCHAR(20) NOT NULL,
    user_input TEXT,
    ai_response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_duration FLOAT,
    INDEX idx_phone_timestamp (phone_number, timestamp),
    INDEX idx_session_id (session_id)
);
```

### ModuleUsage Table
```sql
CREATE TABLE module_usage (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    module_name VARCHAR(50) NOT NULL,
    usage_count INTEGER DEFAULT 1,
    total_duration FLOAT DEFAULT 0,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_module (phone_number, module_name)
);
```

## Sample Queries

### Average Response Times by Module
```sql
SELECT 
    module_name,
    AVG(asr_ms) as avg_asr_ms,
    AVG(llm_ms) as avg_llm_ms,
    AVG(tts_ms) as avg_tts_ms,
    AVG(total_ms) as avg_total_ms,
    COUNT(*) as total_interactions
FROM user_sessions 
WHERE interaction_type = 'turn_metrics'
    AND timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY module_name;
```

### Error Rate Analysis
```sql
SELECT 
    DATE(timestamp) as date,
    COUNT(CASE WHEN error IS NOT NULL AND error != '' THEN 1 END) as error_count,
    COUNT(*) as total_count,
    ROUND(100.0 * COUNT(CASE WHEN error IS NOT NULL AND error != '' THEN 1 END) / COUNT(*), 2) as error_rate_percent
FROM user_sessions 
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### User Engagement Metrics
```sql
SELECT 
    phone_number,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(*) as total_interactions,
    AVG(session_duration) as avg_session_duration,
    MAX(timestamp) as last_activity
FROM user_sessions 
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY phone_number
ORDER BY total_interactions DESC
LIMIT 10;
```

## Monitoring Thresholds

### Performance SLAs
- **ASR Latency**: < 500ms (95th percentile)
- **LLM Latency**: < 2000ms (95th percentile)  
- **TTS Latency**: < 800ms (95th percentile)
- **Total Latency**: < 3000ms (95th percentile)

### Error Rates
- **Overall Error Rate**: < 5%
- **ASR Error Rate**: < 2%
- **LLM Error Rate**: < 3%
- **TTS Error Rate**: < 1%

### Availability
- **Service Uptime**: > 99.5%
- **Health Check Success**: > 99%

### TTS Metrics
- `tts_provider`: Provider used (deepgram, openai, twilio_say)
- `tts_voice`: Voice model used (aura-asteria-en, aura-luna-en, etc.)
- `tts_rate`: Speech rate setting (0.95, 1.0, etc.)
- `tts_pitch`: Pitch adjustment (+1st, 0st, etc.)
- `tts_style`: Style setting (conversational, etc.)
- `audio_encoding`: Output audio format (linear16, mulaw, etc.)
- `tts_fallback_count`: Number of fallback attempts
- `audio_transcode_ms`: Time spent on audio format conversion
- `sentence_chunks`: Number of sentence chunks generated
- `chunk_pause_ms`: Micro-pause duration between chunks
- `barge_in_triggered`: Whether user interrupted TTS playback
