import os
import json
import base64
import audioop
import asyncio
from typing import Optional

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

"""
ENV you must set in Fly (or locally):
  ELEVENLABS_API_KEY   -> your 11Labs User API key
  ELEVENLABS_AGENT_ID  -> your Agent ID (e.g., agent_0301k3y6dwrve6... )
  ELEVENLABS_WS_SECRET -> any random secret string (optional, for 11Labs MCP auth if you use it)
"""

EL_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
EL_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID", "")

EL_WS_URL = f"wss://api.elevenlabs.io/v1/convai/stream?agent_id={EL_AGENT_ID}"

app = FastAPI()


@app.post("/webhook/call")
def twilio_webhook():
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="wss://{os.getenv('FLY_APP_NAME_DOMAIN', 'bakame-elevenlabs-mcp.fly.dev')}/twilio-stream"/>
  </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


def twilio_ulaw8k_to_pcm16_16k(b64_payload: str) -> bytes:
    """Twilio sends 8k μ-law audio in base64. Convert -> 16kHz signed 16-bit PCM."""
    ulaw = base64.b64decode(b64_payload)
    pcm8k = audioop.ulaw2lin(ulaw, 2)  # width=2 bytes/sample
    pcm16k, _ = audioop.ratecv(pcm8k, 2, 1, 8000, 16000, None)
    return pcm16k


def pcm16_16k_to_twilio_ulaw8k(pcm16k: bytes) -> str:
    """From 16k PCM16 -> μ-law 8k (base64) for Twilio playback."""
    pcm8k, _ = audioop.ratecv(pcm16k, 2, 1, 16000, 8000, None)
    ulaw = audioop.lin2ulaw(pcm8k, 2)
    return base64.b64encode(ulaw).decode("ascii")


@app.websocket("/twilio-stream")
async def twilio_stream(ws: WebSocket):
    await ws.accept()
    print("[Twilio] WS connected", flush=True)

    el_headers = {
        "Authorization": f"Bearer {EL_API_KEY}",
    }

    el_ws: Optional[websockets.WebSocketClientProtocol] = None
    el_to_twilio_task: Optional[asyncio.Task] = None

    try:
        el_ws = await websockets.connect(EL_WS_URL)
        print("[EL] WS connected", flush=True)

        async def pump_el_to_twilio():
            """Read audio chunks from 11Labs and push back to Twilio."""
            try:
                async for raw in el_ws:
                    msg = None
                    if isinstance(raw, (bytes, bytearray)):
                        pcm16k = bytes(raw)
                        ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                        out = {"event": "media", "media": {"payload": ulaw_b64}}
                        await ws.send_text(json.dumps(out))
                    else:
                        try:
                            msg = json.loads(raw)
                        except Exception:
                            msg = None

                        if msg and "audio" in msg:
                            pcm16k = base64.b64decode(msg["audio"])
                            ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                            out = {"event": "media", "media": {"payload": ulaw_b64}}
                            await ws.send_text(json.dumps(out))
            except Exception as e:
                print(f"[EL->Twilio] pump error: {e}", flush=True)

        el_to_twilio_task = asyncio.create_task(pump_el_to_twilio())

        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)

            event = data.get("event")
            if event == "start":
                print(f"[Twilio] Media start: {data.get('start')}", flush=True)

            elif event == "media":
                payload_b64 = data["media"]["payload"]
                pcm16k = twilio_ulaw8k_to_pcm16_16k(payload_b64)

                if el_ws is not None:
                    try:
                        await el_ws.send(pcm16k)
                    except Exception as e:
                        print(f"[Twilio->EL] send error: {e}", flush=True)

            elif event == "stop":
                print("[Twilio] Media stop", flush=True)
                break


    except WebSocketDisconnect:
        print("[Twilio] WS disconnected", flush=True)
    except Exception as e:
        print(f"[Bridge] error: {e}", flush=True)
    finally:
        try:
            if el_to_twilio_task:
                el_to_twilio_task.cancel()
        except Exception:
            pass
        try:
            if el_ws:
                await el_ws.close()
        except Exception:
            pass
        try:
            await ws.close()
        except Exception:
            pass
        print("[Bridge] closed", flush=True)
