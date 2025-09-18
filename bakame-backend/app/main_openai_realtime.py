import os
import json
import base64
import audioop
import asyncio
import io
import wave
import time
import math
import struct
from typing import Optional
from collections import deque

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import Response
from app.services.redis_service import redis_service
from app.services.openai_service import openai_service
from app.services.openai_realtime_service import OpenAIRealtimeService
from app.services.logging_service import logging_service
from app.modules.english_module import english_module
from app.modules.math_module import math_module
from app.modules.comprehension_module import comprehension_module
from app.modules.debate_module import debate_module
from app.modules.general_module import general_module

app = FastAPI()

def twilio_ulaw8k_to_openai_pcm24k(b64_payload: str) -> bytes:
    """
    Convert Twilio μ-law@8k to OpenAI Realtime API PCM16@24k format
    """
    ulaw = base64.b64decode(b64_payload)
    pcm8k = audioop.ulaw2lin(ulaw, 2)
    
    pcm24k, _ = audioop.ratecv(pcm8k, 2, 1, 8000, 24000, None)
    
    return pcm24k

def openai_pcm24k_to_twilio_ulaw8k_frames(pcm24k: bytes, state=None) -> tuple[list[bytes], any]:
    """
    Convert OpenAI Realtime API PCM16@24k to Twilio μ-law@8k 20ms frames
    """
    pcm8k, new_state = audioop.ratecv(pcm24k, 2, 1, 24000, 8000, state)
    
    mulaw = audioop.lin2ulaw(pcm8k, 2)
    
    FRAME_BYTES = 160
    frames = [mulaw[i:i+FRAME_BYTES] for i in range(0, len(mulaw), FRAME_BYTES) if len(mulaw[i:i+FRAME_BYTES]) == FRAME_BYTES]
    
    return frames, new_state

async def send_twilio_media_frames(ws, stream_sid: str, mulaw_frames: list[bytes]):
    """
    Sends μ-law frames to Twilio with STRICT 50fps pacing (exactly 20ms intervals).
    """
    if not stream_sid:
        return 0

    try:
        if ws.client_state.name not in ["CONNECTED", "OPEN"]:
            print(f"[FRAME] WebSocket not ready for sending, state: {ws.client_state.name}", flush=True)
            return 0

        frames_sent = 0
        for frame in mulaw_frames:
            if len(frame) != 160:
                continue
                
            frame_b64 = base64.b64encode(frame).decode('utf-8')
            
            media_message = {
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": frame_b64
                }
            }
            
            await ws.send_text(json.dumps(media_message))
            frames_sent += 1
            
            await asyncio.sleep(0.02)
        
        return frames_sent
        
    except Exception as e:
        print(f"[FRAME] Error sending frames: {e}", flush=True)
        return 0

@app.websocket("/twilio-stream")
async def twilio_stream(ws: WebSocket):
    await ws.accept()
    print(f"[Twilio] WS connected at {time.time()}, state: {ws.client_state.name}", flush=True)

    connection_active = True
    phone_number = None
    session_id = None
    stream_sid = None
    audio_conversion_state = None
    
    openai_realtime = OpenAIRealtimeService()
    openai_connected = await openai_realtime.connect()
    
    if not openai_connected:
        print("[Bridge] Failed to connect to OpenAI Realtime API", flush=True)
        await ws.close()
        return

    try:
        async def handle_openai_responses():
            nonlocal audio_conversion_state
            async for response in openai_realtime.listen_for_responses():
                if not connection_active:
                    break
                    
                event_type = response.get("type")
                
                if event_type == "response.audio.delta":
                    audio_b64 = response.get("delta", "")
                    if audio_b64 and stream_sid:
                        try:
                            audio_data = base64.b64decode(audio_b64)
                            frames, audio_conversion_state = openai_pcm24k_to_twilio_ulaw8k_frames(audio_data, audio_conversion_state)
                            
                            if frames:
                                frames_sent = await send_twilio_media_frames(ws, stream_sid, frames)
                                print(f"[OpenAI→Twilio] Sent {len(frames)} audio frames", flush=True)
                        except Exception as e:
                            print(f"[OpenAI→Twilio] Audio conversion error: {e}", flush=True)
                
                elif event_type == "response.audio_transcript.delta":
                    transcript = response.get("delta", "")
                    if transcript:
                        print(f"[OpenAI] Response transcript: {transcript}", flush=True)
                
                elif event_type == "input_audio_buffer.speech_started":
                    print("[OpenAI] User started speaking", flush=True)
                
                elif event_type == "input_audio_buffer.speech_stopped":
                    print("[OpenAI] User stopped speaking", flush=True)
                
                elif event_type == "error":
                    error_msg = response.get("error", {}).get("message", "Unknown error")
                    print(f"[OpenAI] Error: {error_msg}", flush=True)

        openai_task = asyncio.create_task(handle_openai_responses())
        
        while connection_active:
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                print("[Twilio] WebSocket receive timeout", flush=True)
                break
            except Exception as e:
                print(f"[Twilio] WebSocket receive error: {e}", flush=True)
                break
            
            data = json.loads(msg)
            event = data.get("event")
            
            if event == "start":
                start_data = data.get("start", {})
                phone_number = start_data.get("customParameters", {}).get("phone_number")
                session_id = start_data.get("streamSid")
                stream_sid = session_id
                
                print(f"[Twilio] Media start for {phone_number}, streamSid: {session_id}", flush=True)
                
                await openai_realtime.configure_session(phone_number)
            
            elif event == "media":
                media_data = data.get("media", {})
                payload_b64 = media_data.get("payload", "")
                
                if payload_b64:
                    try:
                        pcm24k = twilio_ulaw8k_to_openai_pcm24k(payload_b64)
                        await openai_realtime.send_audio(pcm24k)
                    except Exception as e:
                        print(f"[Twilio→OpenAI] Audio conversion error: {e}", flush=True)
            
            elif event == "stop":
                print(f"[Twilio] Media stop at {time.time()}", flush=True)
                break

    except Exception as e:
        print(f"[Bridge] Error: {e}", flush=True)
    finally:
        print(f"[Bridge] Cleanup starting at {time.time()}", flush=True)
        connection_active = False
        
        if 'openai_task' in locals():
            openai_task.cancel()
            try:
                await asyncio.wait_for(openai_task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        
        await openai_realtime.close()
        
        try:
            if ws.client_state.name in ["CONNECTED", "OPEN"]:
                await ws.close()
        except Exception as e:
            print(f"[Bridge] Error closing Twilio WebSocket: {e}", flush=True)
        
        print(f"[Bridge] Cleanup completed at {time.time()}", flush=True)

@app.post("/webhook/call")
async def twilio_webhook(
    From: str = Form(...),
    To: str = Form(...),
    CallSid: str = Form(...),
    AccountSid: str = Form(...),
    CallStatus: str = Form(...)
):
    """Handle incoming Twilio voice calls and set up media streaming"""
    print(f"[Webhook] Incoming call from {From} to {To}, CallSid: {CallSid}", flush=True)
    
    twiml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://bakame-elevenlabs-mcp.fly.dev/twilio-stream">
            <Parameter name="phone_number" value="{From}" />
        </Stream>
    </Connect>
</Response>'''
    
    return Response(content=twiml_response, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
