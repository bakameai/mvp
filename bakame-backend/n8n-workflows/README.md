# BAKAME n8n Integration Layer

## Overview

This n8n workflow acts as an **orchestration and monitoring layer** for the BAKAME telephony system. It does NOT duplicate the AI processing logic - instead, it forwards all requests to the FastAPI backend and provides additional capabilities like analytics logging and workflow orchestration.

## Architecture

```
Twilio → n8n Webhook → FastAPI Backend → AI Processing
                ↓
         Analytics Logging
```

### Why Use n8n?

The n8n layer provides:
- **Monitoring & Analytics**: Track call/SMS events independently
- **Workflow Orchestration**: Add additional integrations (CRM, notifications, etc.)
- **Load Balancing**: Can route to multiple backend instances
- **A/B Testing**: Route different users to different backends
- **Fallback Logic**: Implement backup systems if primary fails

## Quick Start

1. Install n8n: `npm install -g n8n`
2. Start n8n: `n8n start`
3. Import `telephony-automation.json` in the n8n web interface
4. Set environment variables:
   - `BACKEND_URL` - Your FastAPI backend URL (e.g., `https://app-pyzfduqr.fly.dev`)
   - `ANALYTICS_URL` - Optional separate analytics endpoint
5. Configure Twilio webhooks to point to your n8n instance
6. Activate the workflow

## Workflow Flow

### Voice Calls
1. Twilio sends webhook to n8n
2. n8n logs the event for analytics
3. n8n forwards the request to FastAPI `/webhook/call`
4. FastAPI handles WebSocket streaming, AI processing, and TTS
5. n8n returns the TwiML response to Twilio

### SMS Messages
1. Twilio sends SMS webhook to n8n
2. n8n logs the event for analytics
3. n8n forwards SMS data to FastAPI `/webhook/sms`
4. FastAPI processes through learning modules and generates response
5. n8n returns the TwiML response to Twilio

## Important Notes

⚠️ **This workflow does NOT handle AI processing** - all AI logic (transcription, GPT, TTS, modules) happens in the FastAPI backend.

✅ **Use this workflow for**:
- Analytics and monitoring
- Additional integrations (Slack notifications, CRM updates, etc.)
- A/B testing different backend configurations
- Implementing fallback/retry logic

❌ **Do NOT use this workflow for**:
- Replacing the FastAPI backend
- Duplicating AI processing logic
- Direct Twilio integration (backend handles that better)

## Backend Architecture

The FastAPI backend (`bakame-backend/app/`) handles:
- **Voice**: Real-time WebSocket audio streaming with ElevenLabs/Google TTS
- **SMS**: Direct module processing with Redis session management
- **Learning Modules**: English, Math, Reading, Debate, General Q&A
- **Database**: PostgreSQL for persistence, Redis for sessions
- **Logging**: Comprehensive interaction logging

## Alternative: Direct Integration

If you don't need n8n's orchestration features, you can point Twilio webhooks directly to:
- Voice: `https://your-backend.fly.dev/webhook/call`
- SMS: `https://your-backend.fly.dev/webhook/sms`

This is simpler and has lower latency, but you lose the workflow orchestration capabilities.
