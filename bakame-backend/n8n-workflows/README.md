# BAKAME n8n Workflow Automation

## Quick Start

1. Install n8n: `npm install -g n8n`
2. Start n8n: `n8n start`
3. Import `telephony-automation.json` in the n8n web interface
4. Configure OpenAI and Twilio credentials
5. Set environment variables: `TWILIO_PHONE_NUMBER`, `BACKEND_URL`
6. Point Twilio webhooks to your n8n instance
7. Activate the workflow

## Workflow Flow

**Voice**: Call → Whisper → Module Selector → GPT → TTS → Response → Dashboard  
**SMS**: SMS → Module Selector → GPT → SMS Response → Dashboard

## Modules

- **English**: grammar, pronunciation
- **Math**: arithmetic, calculation  
- **Reading**: comprehension, stories
- **Debate**: critical thinking
- **General**: default fallback

Full documentation available in the complete README.
