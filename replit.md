# BAKAME AI - Voice-Based Learning Platform

## Overview

BAKAME (Building African Knowledge through Accessible Mobile Education) is an AI-powered educational platform that delivers personalized learning through voice calls and SMS to feature phones. The system requires no internet access or smartphones, making quality education accessible to underserved communities.

The platform provides 5 core learning modules (English, Math, Reading Comprehension, Debate, and General Q&A) through natural conversational AI, using voice calls as the primary interface. Students can learn by simply dialing a phone number and speaking with an AI tutor.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Multi-Application Architecture

The system consists of three separate applications:

1. **Backend API (FastAPI/Python)** - Core voice processing and AI engine
   - Deployed on Fly.io at `app-pyzfduqr.fly.dev`
   - Handles Twilio webhooks for voice/SMS
   - Processes audio streams in real-time
   - Manages AI conversation flow

2. **Admin Dashboard (React/TypeScript)** - Administrative interface
   - Built with Vite, React, and TypeScript
   - Uses shadcn/ui component library
   - Provides analytics and session monitoring
   - Independent deployment from backend

3. **Frontend Website (React/TypeScript)** - Public-facing web application
   - Marketing and information pages
   - User enrollment interface
   - Separate from admin dashboard

### Voice Processing Pipeline

The system now supports both Twilio (legacy) and Telnyx (new) for voice communications:

**Telnyx Audio Flow (New)**: Caller → Telnyx Call Control → FastAPI JSON API → AI Processing → Telnyx Commands → Caller
**Legacy Twilio Flow**: Caller → Twilio → FastAPI WebSocket Bridge → Google TTS/ElevenLabs ConvAI → AI Processing → Response Audio → Twilio → Caller

Key architectural decisions:
- **Real-time audio streaming** via WebSocket connections for low latency
- **Audio format conversions**: μ-law 8kHz (Twilio) ↔ PCM 16kHz (AI services)
- **Silence detection** to determine when user has finished speaking
- **Buffer management** to handle streaming audio chunks efficiently

The backend maintains two concurrent WebSocket connections:
1. Twilio WebSocket for caller audio I/O
2. Google TTS/ElevenLabs WebSocket for AI voice generation

### AI Service Architecture

**Primary AI Stack**:
- **Voice Generation**: Google Cloud Text-to-Speech (primary), ElevenLabs ConvAI (alternative)
- **Conversation AI**: OpenAI GPT-4o-mini for response generation
- **Speech-to-Text**: OpenAI Whisper for audio transcription

**Fallback Options**:
- Llama LLM as alternative to GPT
- Deepgram as alternative to Whisper
- Built-in retry logic and error handling

Architectural rationale: Multiple AI providers ensure system resilience. Google TTS provides cost-effective voice synthesis, while ElevenLabs offers more natural conversational AI as a premium option.

### Learning Module System

Five independent learning modules, each implementing a consistent interface:

```python
async def process(user_input: str, session_context: dict) -> str
```

Modules are selected based on user intent or conversation context:
- **English Module**: Grammar correction, pronunciation practice
- **Math Module**: Mental arithmetic with adaptive difficulty  
- **Comprehension Module**: Story generation and Q&A
- **Debate Module**: Critical thinking through argumentation
- **General Module**: Open-ended educational conversations

Design principle: Modular architecture allows independent module updates without affecting the core system.

### Session Management

**Redis-based session storage** for conversation context:
- Stores user conversation history
- Maintains module state across interactions
- Session timeout: 7 days (604800 seconds) - supports unlimited learning sessions
- Key format: `session:{phone_number}:{session_id}`
- TTL automatically refreshes with each interaction

**PostgreSQL for persistent data**:
- User session logs
- Module usage statistics
- Analytics data
- Schema designed for both transactional and analytical queries

**Call Duration Policy**:
- **AI never hangs up on students** - Only students can end calls
- Gather timeout set to 3600 seconds (1 hour) to allow unlimited thinking/pause time
- No time limits on learning sessions
- Students end calls by saying goodbye, bye, hang up, or end call
- Conversation flows naturally without "continue?" interruptions

Rationale: Redis provides fast in-memory access for active conversations, while PostgreSQL ensures data persistence for analytics and compliance. The unlimited session duration ensures students can learn at their own pace without being rushed or cut off.

### Communication Layer

**Twilio Integration**:
- Voice API for phone calls
- SMS API for text-based learning
- TwiML responses for call flow control
- Webhook endpoints: `/webhook/voice`, `/webhook/sms`

**WebSocket Protocol**:
- Bidirectional audio streaming
- JSON message format for control signals
- Keepalive pings every 20 seconds
- Auto-reconnection logic

### Deployment Architecture

**Backend Deployment**:
- Platform: Fly.io
- Runtime: Python 3.11+
- Process model: Async/await with FastAPI
- Environment: Production uses environment variables for secrets

**Frontend/Admin Deployment**:
- Build tool: Vite
- Deployment: Static hosting (separate from backend)
- API communication: REST calls to backend

Design decision: Separate deployments allow independent scaling and updates of frontend vs. backend components.

## External Dependencies

### Third-Party Services

1. **Telnyx** (Primary Voice/SMS Gateway - NEW)
   - Call Control API v2 for voice handling
   - JSON-based command system
   - Event-driven webhooks
   - Real-time call control via REST API
   
2. **Twilio** (Legacy Voice/SMS Gateway - Being Phased Out)
   - Voice API for phone call handling
   - SMS API for text messages
   - Media Streams API for audio streaming
   - TwiML-based response system

2. **Google Cloud Platform**
   - Text-to-Speech API for voice generation
   - Service account authentication
   - Project: bakameai
   - Credentials file: `google_credentials.json`

3. **ElevenLabs** (Alternative Voice AI)
   - ConvAI API for conversational voice
   - WebSocket-based real-time audio
   - Agent-based conversation management
   - Token: ELEVENLABS_WS_SECRET

4. **OpenAI**
   - GPT-4o-mini for conversation AI
   - Whisper API for speech-to-text
   - API key authentication
   - Rate limiting handled at application level

5. **Llama** (Alternative LLM)
   - Fallback option for GPT
   - Self-hosted or API-based deployment
   - Used when OpenAI is unavailable

6. **Deepgram** (Alternative STT)
   - Fallback for Whisper transcription
   - WebSocket-based streaming
   - API key authentication

### Data Storage

1. **Supabase PostgreSQL**
   - Connection: `db.pttxlvbyvhgvwbakabyc.supabase.co:5432`
   - Database: postgres
   - Tables: UserSession, ModuleUsage, WebUser, RefreshToken, ContentPage
   - Connection pooling via direct connection (non-pooler)
   - SSL required for connections

2. **Redis Cache**
   - Session storage and management
   - In-memory key-value store
   - Default: localhost:6379 (development)
   - Production: Redis Cloud or similar managed service
   - TTL-based session expiration

### Environment Variables Required

Backend (`bakame-backend/.env`):
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- `OPENAI_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS` (path to JSON file)
- `GOOGLE_CLOUD_PROJECT`
- `ELEVENLABS_AGENT_ID`, `ELEVENLABS_WS_SECRET`
- `LLAMA_API_KEY`
- `DEEPGRAM_API_KEY`
- `NEWSAPI_KEY`
- `REDIS_URL`
- `DATABASE_URL` (PostgreSQL connection string)
- `APP_ENV` (development/production)

### API Integrations

All external API calls use async HTTP clients (httpx/aiohttp) for non-blocking I/O. Authentication tokens are managed through environment variables and never hardcoded. Rate limiting and retry logic implemented at the service layer.