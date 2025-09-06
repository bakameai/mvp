import os
import logging
import websockets

logger = logging.getLogger(__name__)

ELEVENLABS_WSS_BASE = "wss://api.elevenlabs.io/v1/convai/conversation"

async def open_el_ws():
    """
    Opens a WebSocket to ElevenLabs ConvAI and logs exactly what URL/auth we use.
    If ELEVENLABS_WS_SECRET is set, we send it as Bearer auth. Otherwise, no auth header.
    Agent ID is taken from ELEVENLABS_AGENT_ID env (required).
    """
    agent_id = os.environ.get("ELEVENLABS_AGENT_ID", "").strip()
    if not agent_id:
        logger.error("[EL] missing ELEVENLABS_AGENT_ID env var")
        raise RuntimeError("ELEVENLABS_AGENT_ID not set")

    url = f"{ELEVENLABS_WSS_BASE}?agent_id={agent_id}"
    secret = os.environ.get("ELEVENLABS_WS_SECRET", "").strip()

    logger.info("[EL] attempting WS -> %s  (auth=%s)", url, "Bearer" if secret else "none")

    if secret:
        ws = await websockets.connect(
            url,
            extra_headers={"Authorization": f"Bearer {secret}"},
            ping_interval=None,
        )
    else:
        ws = await websockets.connect(url, ping_interval=None)

    return ws
