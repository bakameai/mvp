import json
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import Response

app = FastAPI()

WS_URL = "wss://bakame-elevenlabs-mcp.fly.dev/twilio-stream"

@app.post("/webhook/call")
async def inbound_call(_: Request):
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="{WS_URL}"/>
  </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.websocket("/twilio-stream")
async def twilio_stream(ws: WebSocket):
    await ws.accept()   # this is CRUCIAL for Twilio handshake

    print("[Twilio] WS connected", flush=True)

    try:
        while True:
            msg = await ws.receive_text()
            print(f"[Twilio] Incoming: {msg[:100]}...", flush=True)
    except Exception as e:
        print(f"[Twilio] WS error: {e}", flush=True)
    finally:
        await ws.close()
        print("[Twilio] WS closed", flush=True)
