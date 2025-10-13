# Twilio to Telnyx Migration Guide

## Overview
This document describes the migration from Twilio's TwiML-based voice system to Telnyx's Call Control API for the BAKAME Learning Assistant backend.

## Architecture Changes

### Previous Architecture (Twilio)
- **Protocol**: TwiML (XML-based responses)
- **Flow**: Webhook receives call → Returns TwiML → Twilio executes commands
- **Voice Handling**: `<Say>`, `<Gather>`, `<Hangup>` XML verbs
- **Session Management**: Stateless, context passed via webhook URLs

### New Architecture (Telnyx)
- **Protocol**: RESTful JSON API with Call Control commands
- **Flow**: Webhook receives events → App sends commands to Telnyx API → Telnyx executes
- **Voice Handling**: `speak`, `gather`, `hangup` API commands
- **Session Management**: Call Control ID maintains session state

## Key Component Mappings

| Twilio Component | Telnyx Equivalent | Description |
|-----------------|-------------------|-------------|
| TwiML `<Say>` | `speak` command | Text-to-speech functionality |
| TwiML `<Gather>` | `gather` or `gather_using_speak` | Collect user input (DTMF/speech) |
| TwiML `<Hangup>` | `hangup` command | End the call |
| TwiML `<Redirect>` | Event-driven webhooks | Flow control via event handling |
| `VoiceResponse()` | JSON API calls | Response format change |
| `/webhook/call` | `/telnyx/incoming` | Main webhook endpoint |
| `SpeechResult` | `digits` in gather.ended | User input handling |

## File Changes

### 1. Dependencies (`pyproject.toml`)
```diff
- twilio = "^9.6.5"
+ telnyx = "^2.0.0"
```

### 2. Configuration (`app/config.py`)
```diff
- twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
- twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
- twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "")
+ telnyx_api_key: str = os.getenv("TELNYX_API_KEY", "")
+ telnyx_phone_number: str = os.getenv("TELNYX_PHONE_NUMBER", "")
+ telnyx_public_key: Optional[str] = os.getenv("TELNYX_PUBLIC_KEY", "")
+ telnyx_api_url: str = "https://api.telnyx.com/v2"
```

### 3. Service Layer
- **Old**: `app/services/twilio_service.py` - TwiML generation
- **New**: `app/services/telnyx_service.py` - API command methods

### 4. Routing Layer
- **Old**: `app/routers/webhooks.py` - Returns XML responses
- **New**: `app/routers/telnyx_webhooks.py` - Handles JSON events, sends API commands

## Environment Variables

Create a `.env` file with:
```env
# Telnyx Configuration
TELNYX_API_KEY=KEY_YOUR_TELNYX_API_KEY_HERE
TELNYX_PHONE_NUMBER=+1234567890
TELNYX_PUBLIC_KEY=YOUR_PUBLIC_KEY_HERE  # Optional, for webhook verification

# Keep existing variables
OPENAIAPI=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
DATABASE_URL=your_database_url
REDIS_URL=redis://localhost:6379/0
```

## Webhook Configuration in Telnyx

1. Log into Telnyx Mission Control Portal
2. Navigate to "Phone Numbers" → Select your number
3. Configure webhooks:
   - **Connection Type**: TeXML Application or Call Control
   - **Webhook URL**: `https://your-domain.fly.dev/telnyx/incoming`
   - **Webhook API Version**: V2
   - **HTTP Method**: POST

## Event Flow Comparison

### Twilio Flow
```
1. Incoming call → POST /webhook/call
2. Return TwiML with <Gather><Say>Welcome</Say></Gather>
3. User speaks → POST /webhook/voice/process with SpeechResult
4. Return TwiML with response
```

### Telnyx Flow
```
1. call.initiated event → POST /telnyx/incoming
2. Send answer_call command
3. call.answered event → Send gather_using_speak command
4. call.gather.ended event → Process input, send next command
5. Continue until hangup
```

## API Endpoint Changes

| Purpose | Twilio Endpoint | Telnyx Endpoint |
|---------|-----------------|-----------------|
| Incoming call webhook | `/webhook/call` | `/telnyx/incoming` |
| Process voice input | `/webhook/voice/process` | Handled via events in `/telnyx/incoming` |
| SMS webhook | `/webhook/sms` | Not migrated yet |
| Health check | `/webhook/health` | `/telnyx/health` |

## Testing the Migration

### 1. Local Testing
```bash
# Install dependencies
cd bakame-backend
poetry install

# Set environment variables
export TELNYX_API_KEY="your_test_key"
export TELNYX_PHONE_NUMBER="+1234567890"

# Run the server
uvicorn app.main:app --reload --port 8000
```

### 2. Use ngrok for webhook testing
```bash
ngrok http 8000
# Configure Telnyx webhook to: https://your-ngrok-url.ngrok.io/telnyx/incoming
```

### 3. Test Call Flow
```bash
# Call your Telnyx number
# Check logs in bakame_telnyx.log
# Verify events are received and commands are sent
```

### 4. Debug Endpoints
- `POST /telnyx/test/speak` - Test speak command with call_control_id
- `GET /telnyx/health` - Check service status

## Logging and Debugging

All Telnyx events and API calls are logged to:
- Console output
- `bakame_telnyx.log` file

Log format includes:
- Event types received
- Call Control IDs
- API commands sent
- Response status
- Error messages

## Rollback Plan

The migration keeps both systems in parallel:
- Twilio endpoints remain at `/webhook/*` (marked as legacy)
- Telnyx endpoints are at `/telnyx/*`
- Can switch back by updating phone number webhook configuration

## Common Issues and Solutions

### Issue: Call not answering
**Solution**: Ensure `answer_call` is sent immediately on `call.initiated`

### Issue: No audio playing
**Solution**: Wait for `call.answered` event before sending speak commands

### Issue: Gather not working
**Solution**: Use `gather_using_speak` for combined prompt and input collection

### Issue: Webhook not receiving events
**Solution**: Check webhook URL configuration and firewall settings

## Performance Improvements

1. **Reduced Latency**: Direct API calls vs XML parsing
2. **Better Control**: Fine-grained command control
3. **Event-Driven**: React to specific call events
4. **Logging**: Comprehensive event tracking

## Next Steps

1. Test with sandbox Telnyx number
2. Port production number from Twilio to Telnyx
3. Update monitoring and alerting
4. Implement SMS migration (if needed)
5. Add webhook signature verification for production

## Support Contacts

- Telnyx Support: support@telnyx.com
- Telnyx Docs: https://developers.telnyx.com
- API Reference: https://developers.telnyx.com/docs/api/v2