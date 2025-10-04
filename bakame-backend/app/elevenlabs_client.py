import os
import sys
import websockets
from websockets.exceptions import InvalidStatusCode

ELEVENLABS_WSS_BASE = "wss://api.elevenlabs.io/v1/convai/conversation"

def _mask(s: str, show: int = 4) -> str:
    if not s:
        return ""
    return ("*" * max(0, len(s) - show)) + s[-show:]

async def open_el_ws():
    agent_id = os.environ.get("ELEVENLABS_AGENT_ID", "").strip()
    if not agent_id:
        print("[EL] ERROR: ELEVENLABS_AGENT_ID not set", flush=True)
        raise RuntimeError("ELEVENLABS_AGENT_ID not set")

    ws_secret = os.environ.get("ELEVENLABS_WS_SECRET", "").strip()  # workspace secret
    user_api  = os.environ.get("ELEVENLABS_API_KEY", "").strip()    # optional fallback

    url = f"{ELEVENLABS_WSS_BASE}?agent_id={agent_id}"

    if ws_secret:
        print(
            f"[EL] attempting WS -> {url}  (auth=Bearer { _mask(ws_secret) })",
            flush=True,
        )
        try:
            return await websockets.connect(
                url,
                additional_headers={"Authorization": f"Bearer {ws_secret}"},
                ping_interval=20,  # 20 second keepalive
                ping_timeout=10,   # 10 second timeout
                max_size=2**20,    # 1MB max message size
                max_queue=32,      # Optimize send queue
            )
        except InvalidStatusCode as e:
            print(f"[EL] connect failed (Bearer) status={getattr(e, 'status_code', 'unknown')}", flush=True)
            if getattr(e, "status_code", None) != 403:
                raise  # not an auth issue; bubble up

    if user_api:
        print(
            f"[EL] retrying WS -> {url}  (auth=xi-api-key { _mask(user_api) })",
            flush=True,
        )
        return await websockets.connect(
            url,
            additional_headers={"xi-api-key": user_api},
            ping_interval=20,  # 20 second keepalive
            ping_timeout=10,   # 10 second timeout
            max_size=2**20,    # 1MB max message size
            max_queue=32,      # Optimize send queue
        )

    raise RuntimeError(
        "Failed to authenticate to ElevenLabs ConvAI WS. "
        "Set ELEVENLABS_WS_SECRET (workspace secret) and optionally ELEVENLABS_API_KEY."
    )
