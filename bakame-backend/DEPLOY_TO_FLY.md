# Deploy to Fly.io

## Prerequisites
- Fly.io CLI installed (`flyctl`)
- Authenticated with Fly.io (`flyctl auth login`)

## Environment Variables Needed

Make sure these secrets are set in Fly.io:

```bash
flyctl secrets set TELNYX_API_KEY="your_telnyx_api_key"
flyctl secrets set OPENAI_API_KEY="your_openai_api_key"
flyctl secrets set REDIS_URL="your_redis_url"
flyctl secrets set DATABASE_URL="your_postgres_url"
flyctl secrets set ELEVENLABS_AGENT_ID="your_elevenlabs_agent_id"
flyctl secrets set ELEVENLABS_WS_SECRET="your_elevenlabs_secret"
flyctl secrets set NEWSAPI_KEY="your_newsapi_key"
```

## Deploy Steps

1. **Navigate to backend directory:**
   ```bash
   cd bakame-backend
   ```

2. **Check current secrets:**
   ```bash
   flyctl secrets list
   ```

3. **Deploy:**
   ```bash
   flyctl deploy
   ```

4. **Verify deployment:**
   ```bash
   flyctl status
   flyctl logs
   ```

5. **Update Telnyx webhook URL to:**
   ```
   https://app-pyzfduqr.fly.dev/telnyx/incoming
   ```

## Testing WebSocket

The WebSocket endpoint will be available at:
```
wss://app-pyzfduqr.fly.dev/telnyx/stream/{call_control_id}
```

## Troubleshooting

- Check logs: `flyctl logs`
- Check app status: `flyctl status`
- SSH into app: `flyctl ssh console`
- Restart app: `flyctl apps restart app-pyzfduqr`
