import os
import json
import base64
import audioop
import asyncio
from typing import Optional

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import Response
from app.services.redis_service import redis_service
from app.services.openai_service import openai_service
from app.services.llama_service import llama_service
from app.services.logging_service import logging_service
from app.modules.english_module import english_module
from app.modules.math_module import math_module
from app.modules.comprehension_module import comprehension_module
from app.modules.debate_module import debate_module
from app.modules.general_module import general_module

"""
ENV you must set in Fly (or locally):
  ELEVENLABS_API_KEY   -> your 11Labs User API key
  ELEVENLABS_AGENT_ID  -> your Agent ID (e.g., agent_0301k3y6dwrve6... )
  ELEVENLABS_WS_SECRET -> any random secret string (optional, for 11Labs MCP auth if you use it)
"""

EL_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
EL_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID", "")

EL_WS_URL = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={EL_AGENT_ID}"

MODULES = {
    "english": english_module,
    "math": math_module,
    "comprehension": comprehension_module,
    "debate": debate_module,
    "general": general_module
}

AUDIO_BUFFER_DURATION = 3.0
SILENCE_THRESHOLD = 0.01

app = FastAPI()


@app.post("/webhook/call")
async def twilio_webhook(From: str = Form(...), To: str = Form(...)):
    phone_number = From
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="wss://{os.getenv('FLY_APP_NAME_DOMAIN', 'bakame-elevenlabs-mcp.fly.dev')}/twilio-stream">
      <Parameter name="phone_number" value="{phone_number}" />
    </Stream>
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


async def process_audio_buffer(audio_buffer: bytearray, phone_number: str, session_id: str, el_ws):
    """Process accumulated audio through BAKAME AI pipeline"""
    try:
        if not phone_number:
            print("[BAKAME] No phone number available, skipping AI processing", flush=True)
            return
        
        audio_bytes = bytes(audio_buffer)
        user_input = await openai_service.transcribe_audio(audio_bytes, "wav")
        
        if not user_input or len(user_input.strip()) < 2:
            print("[BAKAME] No meaningful transcription, skipping", flush=True)
            return
        
        print(f"[BAKAME] Transcribed: {user_input}", flush=True)
        
        if user_input.lower().strip() == "reset" or any(word in user_input.lower() for word in ["hello", "hi", "hey", "start", "new", "help", "menu", "general"]):
            redis_service.clear_user_context(phone_number)
            user_context = redis_service.get_user_context(phone_number)
            current_module_name = "general"
            redis_service.set_current_module(phone_number, current_module_name)
        else:
            user_context = redis_service.get_user_context(phone_number)
        
        user_context["phone_number"] = phone_number
        
        current_module_name = redis_service.get_current_module(phone_number) or "general"
        
        requested_module = user_context.get("user_state", {}).get("requested_module")
        if requested_module and requested_module in MODULES:
            current_module_name = requested_module
            redis_service.set_current_module(phone_number, current_module_name)
            user_context["user_state"]["requested_module"] = None
            redis_service.set_user_context(phone_number, user_context)
        
        current_module = MODULES.get(current_module_name, general_module)
        
        ai_response = await current_module.process_input(user_input, user_context)
        
        redis_service.add_to_conversation_history(phone_number, user_input, ai_response)
        
        await logging_service.log_interaction(
            phone_number=phone_number,
            session_id=session_id,
            module_name=current_module_name,
            interaction_type="voice",
            user_input=user_input,
            ai_response=ai_response
        )
        
        print(f"[BAKAME] AI Response: {ai_response}", flush=True)
        
    except Exception as e:
        print(f"[BAKAME] Error processing audio: {e}", flush=True)
        await logging_service.log_error(f"Voice processing error for {phone_number}: {str(e)}")


@app.websocket("/twilio-stream")
async def twilio_stream(ws: WebSocket):
    await ws.accept()
    print("[Twilio] WS connected", flush=True)

    audio_buffer = bytearray()
    buffer_start_time = None
    phone_number = None
    session_id = None

    el_ws: Optional[websockets.WebSocketClientProtocol] = None
    el_to_twilio_task: Optional[asyncio.Task] = None

    try:
        print(f"[EL] Connecting to: {EL_WS_URL}", flush=True)
        print("[EL] Attempting connection without authentication headers (per docs)", flush=True)
        el_ws = await websockets.connect(EL_WS_URL)
        print("[EL] WS connected successfully!", flush=True)

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
                start_data = data.get("start", {})
                phone_number = start_data.get("customParameters", {}).get("phone_number")
                session_id = start_data.get("streamSid")
                print(f"[Twilio] Media start for {phone_number}", flush=True)

            elif event == "media":
                payload_b64 = data["media"]["payload"]
                pcm16k = twilio_ulaw8k_to_pcm16_16k(payload_b64)

                audio_buffer.extend(pcm16k)
                if buffer_start_time is None:
                    buffer_start_time = asyncio.get_event_loop().time()

                current_time = asyncio.get_event_loop().time()
                if (current_time - buffer_start_time >= AUDIO_BUFFER_DURATION or 
                    len(audio_buffer) > 32000):
                    
                    if len(audio_buffer) > 0:
                        await process_audio_buffer(audio_buffer, phone_number, session_id, el_ws)
                        audio_buffer.clear()
                        buffer_start_time = None

                if el_ws is not None:
                    try:
                        await el_ws.send(pcm16k)
                    except Exception as e:
                        print(f"[Twilio->EL] send error: {e}", flush=True)

            elif event == "stop":
                print("[Twilio] Media stop", flush=True)
                if len(audio_buffer) > 0:
                    await process_audio_buffer(audio_buffer, phone_number, session_id, el_ws)
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
