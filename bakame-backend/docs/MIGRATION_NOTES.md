# IVR Stabilization Migration Notes

## Overview

This document outlines the changes made during the IVR stabilization and pilot readiness implementation.

## Files Changed

### Core Services
- `app/services/llama_service.py` - Added circuit breaker protection
- `app/services/twilio_service.py` - Added barge-in support with chunked TTS
- `app/services/logging_service.py` - Enhanced with PII redaction and turn metrics
- `app/routers/webhooks.py` - Added 3-step silence handling
- `app/main.py` - Enhanced startup validation and health checks

### New Components
- `app/routers/media_stream.py` - Twilio Media Streams WebSocket handler for VAD
- `app/utils/retry.py` - Retry logic with exponential backoff
- `app/utils/metrics.py` - Per-turn metrics collection
- `app/utils/redact.py` - PII redaction utilities
- `app/utils/circuit_breaker.py` - Circuit breaker for LLM failures
- `app/utils/provider_config.py` - Configurable provider switching
- `scripts/sim_call.py` - Latency measurement harness

### Enhanced Modules
- `app/modules/english_module.py` - Added curriculum scaffolding with level-aware prompts

## Key Changes

### 1. Dependency Resolution
- Fixed pydantic-settings import issue
- Added comprehensive startup environment validation

### 2. Latency Measurement
- Created `scripts/sim_call.py` for repeatable ASR→LLM→TTS timing
- Added sample audio files in `scripts/samples/`

### 3. Barge-in & VAD
- Implemented Twilio Media Streams WebSocket endpoint
- Added simple VAD using audio amplitude analysis
- Enhanced TwiML generation with chunked sentence playback
- Redis-based barge-in flag management

### 4. Fallbacks & Retries
- Added retry decorator with exponential backoff (200ms → 400ms)
- Implemented 3-step silence handling: reprompt → simplify → SMS tip
- Enhanced error classification (transient vs fatal)

### 5. Observability
- Extended CSV schema with per-turn metrics
- Added metrics collection decorator
- Tracking: call_id, turn, asr_ms, llm_ms, tts_ms, tokens, confidence

### 6. PII Redaction
- Created comprehensive PII redaction utility
- Redacts phone numbers and emails from logs
- Preserves minimal trace IDs for record joining

### 7. Curriculum System Restructuring (Pedagogical Integration)

**Module Structure Changes:**
- **Old**: Flat files (`english_remember.md`, `math_apply.md`)
- **New**: Nested folders (`grammar/remember.md`, `composition/apply.md`)

**English Module Split:**
- **Grammar Module**: Focus on sentence structure, verb tenses, grammar rules
  - Source: Speak English: 30 Days to Better English
  - Emphasis: Technical grammar instruction and error correction
- **Composition Module**: Focus on creative writing, storytelling, expression
  - Source: Things Fall Apart (Chinua Achebe)
  - Emphasis: Cultural storytelling and creative expression

**New Module List:**
- `grammar` (split from english)
- `composition` (split from english) 
- `math` (unchanged content, new structure)
- `debate` (unchanged content, new structure)
- `comprehension` (unchanged content, new structure)

**OER Source Integration:**
- Grammar: Speak English: 30 Days to Better English (Educational Use)
- Composition: Things Fall Apart (Public Domain)
- Math: Secrets of Mental Math (Educational Use)
- Debate: Code of the Debater (Open Access)
- Comprehension: Art of Public Speaking (Public Domain)

**RAG Preparation:**
- All curriculum files structured with clean markdown
- Content chunked to <300 tokens per section
- Clear headers and bullet points for embedding
- Consistent formatting across all modules

**Assessment Logic Preserved:**
- Multi-factor scoring: keyword (40%) + structure (30%) + LLM (30%)
- Pass threshold: 60% overall score
- Advancement: 3 passes out of 5 attempts
- Demotion: 3 consecutive failures

**Language/Knowledge Split:**
- Language scaffolding preserves meaning while gently correcting grammar
- Assessment focuses on communication success over perfect pronunciation
- Cultural context integration for Rwandan learners
- Accent-tolerant evaluation patterns

**Emotion-Aware Enhancements:**
- Dynamic temperature adjustment based on conversation state
- Sentiment-aware response generation
- Encouraging feedback for struggling learners
- Cultural motivational messages with Ubuntu philosophy

### 8. Curriculum Scaffolding
- Added level-aware prompts (A1 → A2 → B1 → B2)
- Implemented error tracking and adaptive learning
- Targeted correction based on recent mistakes

### 8. Health & Resilience
- Enhanced `/healthz` endpoint with service connectivity checks
- Added circuit breaker for LLM failures (3 errors → 2 min timeout)
- Automatic fallback to OpenAI when circuit breaker opens

### 9. Offline/Edge Fallback
- Configurable provider switching via environment variables
- Support for local ASR/TTS providers
- Degraded mode detection and logging

## How to Extend

### Adding New Metrics
1. Update CSV schema in `logging_service.py`
2. Use `MetricsCollector` in your service
3. Call `log_turn_metrics()` with new fields

### Adding New PII Patterns
1. Update patterns in `app/utils/redact.py`
2. Test with sample data
3. Verify redaction in logs

### Adding New Providers
1. Update `ProviderConfig` in `app/utils/provider_config.py`
2. Implement provider interface
3. Add environment variable configuration

## Breaking Changes

- CSV log format extended with new columns
- TwiML generation now requires call_sid for barge-in support
- Health check endpoint returns detailed status instead of simple OK

## Backward Compatibility

- All existing API contracts preserved
- Fallback behavior maintains original functionality
- New features are opt-in via configuration
