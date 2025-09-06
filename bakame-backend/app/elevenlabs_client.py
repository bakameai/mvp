import os
import websockets
import sys

ELEVENLABS_WSS_BASE = "wss://api.elevenlabs.io/v1/convai/conversation"

async def open_el_ws():
    agent_id = os.environ.get("ELEVENLABS_AGENT_ID", "").strip()
    if not agent_id:
        print("[EL] ERROR: ELEVENLABS_AGENT_ID not set", flush=True)
        raise RuntimeError("ELEVENLABS_AGENT_ID not set")

    url = f"{ELEVENLABS_WSS_BASE}?agent_id={agent_id}"
    secret = os.environ.get("ELEVENLABS_WS_SECRET", "").strip()

    print(f"[EL] attempting WS -> {url}  (auth={'Bearer' if secret else 'none'})", flush=True)

    if secret:
        ws = await websockets.connect(
            url,
            extra_headers={"Authorization": f"Bearer {secret}"},
            ping_interval=None,
        )
    else:
        ws = await websockets.connect(url, ping_interval=None)

    return ws
