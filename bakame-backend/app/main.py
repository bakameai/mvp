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
from app.services.logging_service import logging_service
from app.modules.english_module import english_module
from app.modules.math_module import math_module
from app.modules.comprehension_module import comprehension_module
from app.modules.debate_module import debate_module
from app.modules.general_module import general_module
from app.deepgram_tts_client import open_deepgram_tts

WS_STATE_INACTIVE = "INACTIVE"
WS_STATE_ACTIVE = "ACTIVE" 
WS_STATE_CLOSING = "CLOSING"
WS_STATE_CLOSED = "CLOSED"

SILENCE_THRESHOLD_MS = 250  # Reduced from 500ms for real-time conversation
BUFFER_CHECK_INTERVAL_MS = 5  # Faster buffer processing
SILENCE_CHECK_INTERVAL_MS = 50  # More responsive silence detection
FRAME_RATE_TARGET = 50  # Target 50fps
MAX_BUFFER_FRAMES = 150  # Increased from 100 for better buffering
VAD_RMS_THRESHOLD = 500  # RMS threshold for voice activity detection
VAD_ENERGY_THRESHOLD = 0.01  # Energy threshold for voice activity

"""
ENV you must set in Fly (or locally):
  GOOGLE_APPLICATION_CREDENTIALS -> path to service account JSON file
  GOOGLE_CLOUD_PROJECT -> your Google Cloud project ID
"""

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


def enhance_voice_audio(pcm16k: bytes) -> bytes:
    """
    Enhance voice audio quality before μ-law conversion.
    Applies amplitude normalization and voice-frequency optimization for 300-3400Hz range.
    """
    if not pcm16k:
        return pcm16k
    
    pcm16k = apply_voice_frequency_emphasis(pcm16k)
    
    max_val = audioop.max(pcm16k, 2)
    if max_val > 0:
        target_amplitude = int(32767 * 0.3)  # Reduce from 0.8 to 0.3 to prevent extreme amplification
        scale_factor = target_amplitude / max_val
        scale_factor = min(scale_factor, 3.0)  # Cap at 3x amplification
        if scale_factor != 1.0:
            pcm16k = audioop.mul(pcm16k, 2, scale_factor)
    
    return pcm16k

def apply_voice_frequency_emphasis(pcm16k: bytes) -> bytes:
    """
    Lightweight voice enhancement without blocking scipy operations.
    Applies basic frequency emphasis for voice clarity.
    """
    if not pcm16k:
        return pcm16k
    
    try:
        max_val = audioop.max(pcm16k, 2)
        if max_val > 0:
            target_amplitude = int(32767 * 0.6)
            scale_factor = min(2.0, target_amplitude / max_val)  # Max 2x gain
            enhanced = audioop.mul(pcm16k, 2, scale_factor)
            print(f"[VOICE] Light enhancement: {scale_factor:.1f}x gain", flush=True)
            return enhanced
        return pcm16k
    except Exception as e:
        print(f"[VOICE] Enhancement failed, using original: {e}", flush=True)
        return pcm16k

def twilio_ulaw8k_to_pcm16_16k(b64_payload: str) -> bytes:
    """
    Twilio sends 8k μ-law audio in base64. Convert -> 16kHz signed 16-bit PCM.
    Enhanced with light AGC targeting -18 dBFS RMS for optimal voice processing.
    """
    ulaw = base64.b64decode(b64_payload)
    pcm8k = audioop.ulaw2lin(ulaw, 2)  # width=2 bytes/sample
    
    pcm16k, _ = audioop.ratecv(pcm8k, 2, 1, 8000, 16000, None)
    
    try:
        import struct
        samples = struct.unpack(f'<{len(pcm16k)//2}h', pcm16k)
        
        if samples:
            # Light AGC targeting -18 dBFS RMS with moderate compression
            rms_level = (sum(s*s for s in samples) / len(samples)) ** 0.5
            target_rms = int(32767 * 0.18)  # -18 dBFS target
            
            if rms_level > 0:
                gain_factor = min(4.0, target_rms / rms_level)  # Max 12 dB gain
                
                normalized_samples = []
                for sample in samples:
                    scaled = int(sample * gain_factor)
                    clamped = max(-28000, min(28000, scaled))
                    normalized_samples.append(clamped)
                
                pcm16k = struct.pack(f'<{len(normalized_samples)}h', *normalized_samples)
                print(f"[AUDIO] Light AGC applied: gain {gain_factor:.1f}x, target -18 dBFS", flush=True)
        
    except Exception as e:
        print(f"[AUDIO] AGC failed, using original: {e}", flush=True)
    
    return pcm16k


def pcm16_16k_to_mulaw8k_20ms_frames(pcm16k: bytes, state=None) -> tuple[list[bytes], any]:
    """
    Input:  16-bit PCM, 16kHz, mono
    Output: list of 20ms μ-law frames at 8kHz; each frame is 160 bytes
    Enhanced with voice quality optimizations for Twilio compliance.
    """
    enhanced_pcm16k = enhance_voice_audio(pcm16k)
    
    pcm8k, new_state = audioop.ratecv(enhanced_pcm16k, 2, 1, 16000, 8000, state)
    mulaw = audioop.lin2ulaw(pcm8k, 2)
    FRAME_BYTES = 160
    frames = [mulaw[i:i+FRAME_BYTES] for i in range(0, len(mulaw), FRAME_BYTES) if len(mulaw[i:i+FRAME_BYTES]) == FRAME_BYTES]
    return frames, new_state

async def send_twilio_media_frames(ws, stream_sid: str, mulaw_frames: list[bytes], connection_active=True):
    """
    Sends μ-law frames to Twilio with STRICT 50fps pacing (exactly 20ms intervals).
    Each frame must be exactly 160 bytes μ-law → ~214 base64 chars.
    Codec: G.711 μ-law, Sample rate: 8 kHz, Frame size: 20ms, Frame rate: 50fps exactly.
    """
    if not stream_sid or not connection_active:
        return 0

    try:
        if not ws or ws.client_state.name not in ["CONNECTED", "OPEN"]:
            print(f"[FRAME] WebSocket not ready for sending, state: {getattr(ws, 'client_state', {}).get('name', 'unknown')}", flush=True)
            return 0
    except Exception as e:
        print(f"[FRAME] WebSocket connection validation failed: {e}", flush=True)
        return 0

    frame_count = 0
    
    for frame in mulaw_frames:
        if not connection_active:
            break
            
        frame_count += 1
        
        if len(frame) != 160:
            print(f"[FRAME] WARNING: Frame {frame_count} size {len(frame)} != 160 bytes, skipping", flush=True)
            continue
            
        payload_b64 = base64.b64encode(frame).decode("ascii")
        msg = {
            "event": "media",
            "streamSid": stream_sid,
            "media": {"payload": payload_b64}
        }
        
        print(f"[FRAME] Sending frame {frame_count}, size=160, streamSid={stream_sid[:8]}..., payload_len={len(payload_b64)}", flush=True)
        
        max_retries = 2
        retry_count = 0
        frame_sent = False
        
        while retry_count <= max_retries and not frame_sent and connection_active:
            try:
                if ws.client_state.name not in ["CONNECTED", "OPEN"]:
                    print(f"[FRAME] WebSocket closed during send, state: {ws.client_state.name}", flush=True)
                    return frame_count
                
                await ws.send_text(json.dumps(msg))
                frame_sent = True
                if retry_count > 0:
                    print(f"[FRAME] Frame {frame_count} sent successfully after {retry_count} retries", flush=True)
            except Exception as e:
                retry_count += 1
                error_msg = str(e).lower()
                
                if any(keyword in error_msg for keyword in ["once a close message", "closed", "not connected", "accept first"]):
                    print(f"[FRAME] WebSocket connection error, stopping frame send: {e}", flush=True)
                    return frame_count
                
                if retry_count <= max_retries:
                    print(f"[FRAME] Frame {frame_count} send failed (attempt {retry_count}/{max_retries + 1}): {e}", flush=True)
                    await asyncio.sleep(0.005)
                else:
                    print(f"[FRAME] Frame {frame_count} send failed permanently after {max_retries + 1} attempts: {e}", flush=True)

        await asyncio.sleep(0.02)
    
    return frame_count

def one_khz_tone_mulaw_8k_1s() -> list[bytes]:
    """Generate 1kHz test tone for 1 second at 8kHz μ-law, sliced into 20ms frames."""
    import math, struct
    sr = 8000
    dur = 1.0
    freq = 1000.0
    amp = 12000
    samples = bytearray()
    for n in range(int(sr*dur)):
        val = int(amp * math.sin(2*math.pi*freq*(n/sr)))
        samples += struct.pack("<h", val)
    enhanced_samples = enhance_voice_audio(bytes(samples))
    mulaw = audioop.lin2ulaw(enhanced_samples, 2)
    FRAME_BYTES = 160
    frames = [mulaw[i:i+FRAME_BYTES] for i in range(0, len(mulaw), FRAME_BYTES) if len(mulaw[i:i+FRAME_BYTES]) == FRAME_BYTES]
    print(f"[TEST] Generated 1s enhanced test tone: {len(frames)} frames ({len(frames)/50:.1f}s)", flush=True)
    return frames

def generate_30s_test_tone() -> list[bytes]:
    """Generate 30 seconds of 1kHz test tone for pipeline stability validation."""
    import math, struct
    sr = 8000
    dur = 30.0  # 30 seconds
    freq = 1000.0
    amp = 12000
    samples = bytearray()
    for n in range(int(sr * dur)):
        val = int(amp * math.sin(2 * math.pi * freq * (n / sr)))
        samples += struct.pack("<h", val)
    enhanced_samples = enhance_voice_audio(bytes(samples))
    mulaw = audioop.lin2ulaw(enhanced_samples, 2)
    FRAME_BYTES = 160
    frames = [mulaw[i:i+FRAME_BYTES] for i in range(0, len(mulaw), FRAME_BYTES) if len(mulaw[i:i+FRAME_BYTES]) == FRAME_BYTES]
    print(f"[TEST] Generated 30s enhanced test tone: {len(frames)} frames ({len(frames)/50:.1f}s)", flush=True)
    return frames

def generate_silence_frame() -> bytes:
    """Generate a 20ms silence frame (160 bytes of μ-law silence = 0xFF)."""
    return bytes([0xFF] * 160)

def log_audio_quality_metrics(pcm16k: bytes, frames: list[bytes], event_id: str = "unknown"):
    """Log audio quality metrics for monitoring enhancement effectiveness."""
    if pcm16k and frames:
        rms_level = audioop.rms(pcm16k, 2)
        max_level = audioop.max(pcm16k, 2)
        dynamic_range = max_level / max(rms_level, 1)  # Avoid division by zero
        
        print(f"[QUALITY] Event {event_id}: RMS={rms_level}, Max={max_level}, "
              f"Dynamic Range={dynamic_range:.2f}, Frames={len(frames)}", flush=True)
def detect_voice_activity(pcm16k: bytes) -> bool:
    """Detect voice activity using RMS and energy thresholds."""
    if not pcm16k or len(pcm16k) < 2:
        return False
    
    try:
        rms_level = audioop.rms(pcm16k, 2)
        max_level = audioop.max(pcm16k, 2)
        energy_ratio = rms_level / max(max_level, 1)
        
        has_voice = rms_level > VAD_RMS_THRESHOLD and energy_ratio > VAD_ENERGY_THRESHOLD
        return has_voice
    except Exception as e:
        print(f"[VAD] Error detecting voice activity: {e}", flush=True)
        return False




async def process_audio_buffer(audio_buffer: deque, phone_number: str, session_id: str, google_tts_client):
    """Process accumulated audio through BAKAME AI pipeline"""
    try:
        if not phone_number:
            print("[BAKAME] No phone number available, skipping AI processing", flush=True)
            return
        
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(b''.join(audio_buffer))
        
        wav_bytes = wav_buffer.getvalue()
        user_input = await openai_service.transcribe_audio(wav_bytes, "wav")
        
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
        
        return ai_response
        
    except Exception as e:
        print(f"[BAKAME] Error processing audio: {e}", flush=True)
        await logging_service.log_error(f"Voice processing error for {phone_number}: {str(e)}")
        return None


@app.websocket("/twilio-stream")
async def twilio_stream(ws: WebSocket):
    await ws.accept()
    print(f"[Twilio] WS connected at {time.time()}, state: {ws.client_state.name}", flush=True)

    ws_state = WS_STATE_INACTIVE  # Start as INACTIVE, set ACTIVE only on "start" event
    cleanup_in_progress = False
    
    audio_buffer = deque()
    buffer_start_time = None
    phone_number = None
    session_id = None
    stream_sid = None
    pending_mulaw_frames = deque()
    last_audio_time = time.time()
    frames_sent_count = 0
    silence_frames_count = 0
    audio_frames_count = 0

    deepgram_tts_client = None
    deepgram_tts_task: Optional[asyncio.Task] = None
    tts_synthesis_task: Optional[asyncio.Task] = None
    tts_ready = False
    audio_conversion_state = None
    sender_task = None
    tts_synthesize_func = None
    AUDIO_BUFFER_DURATION = 3.0

    try:
        print("[Deepgram TTS] Connecting...", flush=True)
        deepgram_tts_client = await open_deepgram_tts()
        print("[Deepgram TTS] Connected successfully!", flush=True)
        
        tts_ready = True
        print("[Deepgram TTS] Ready for text synthesis...", flush=True)

        current_audio_queue = None
        
        def enqueue_audio_frames(frames: list[bytes]):
            """Enqueue audio frames for the 50fps sender."""
            nonlocal current_audio_queue
            if current_audio_queue is not None:
                for frame in frames:
                    current_audio_queue.append(frame)
                print(f"[QUEUE] Enqueued {len(frames)} audio frames", flush=True)

        async def dedicated_50fps_sender():
            """Send exactly one frame every 20ms - either audio or silence."""
            nonlocal stream_sid, frames_sent_count, silence_frames_count, audio_frames_count, ws_state, current_audio_queue
            
            audio_frame_queue = deque()
            current_audio_queue = audio_frame_queue
            last_frame_time = asyncio.get_event_loop().time()
            
            print("[50FPS] Dedicated sender started", flush=True)
            
            while ws_state == WS_STATE_ACTIVE and stream_sid:
                frame_start_time = asyncio.get_event_loop().time()
                
                if ws_state != WS_STATE_ACTIVE or not stream_sid:
                    print(f"[50FPS] State changed to {ws_state}, stopping sender", flush=True)
                    break
                
                try:
                    if not ws or ws.client_state.name not in ["CONNECTED", "OPEN"]:
                        print(f"[50FPS] WebSocket closed, stopping sender: {getattr(ws, 'client_state', {}).get('name', 'unknown')}", flush=True)
                        break
                except Exception as e:
                    print(f"[50FPS] Error checking WebSocket state: {e}", flush=True)
                    break
                
                if audio_frame_queue:
                    frame = audio_frame_queue.popleft()
                    frame_type = "audio"
                    audio_frames_count += 1
                else:
                    frame = generate_silence_frame()
                    frame_type = "silence"
                    silence_frames_count += 1
                
                frames_sent = await send_twilio_media_frames(ws, stream_sid, [frame], ws_state == WS_STATE_ACTIVE)
                if frames_sent == 0:  # WebSocket error occurred
                    print(f"[50FPS] WebSocket error during {frame_type} send, stopping immediately", flush=True)
                    ws_state = WS_STATE_CLOSING
                    break
                
                frames_sent_count += 1
                
                elapsed = asyncio.get_event_loop().time() - frame_start_time
                inter_frame_delta = frame_start_time - last_frame_time
                if inter_frame_delta > 0.025:  # Alert if >25ms
                    print(f"[50FPS] WARNING: Inter-frame delta {inter_frame_delta*1000:.1f}ms > 25ms", flush=True)
                
                last_frame_time = frame_start_time
                
                sleep_time = max(0, 0.02 - elapsed)
                await asyncio.sleep(sleep_time)
            
            print("[50FPS] Dedicated sender stopped", flush=True)
            return audio_frame_queue

        async def tts_synthesis_worker():
            """Separate task for TTS synthesis to avoid blocking receive loop."""
            nonlocal ws_state, deepgram_tts_client, tts_ready, audio_conversion_state, current_audio_queue
            
            synthesis_queue = asyncio.Queue()
            
            async def synthesize_text(text: str, context: str = "response"):
                """Synthesize text and enqueue audio frames."""
                nonlocal audio_conversion_state
                if not deepgram_tts_client or not tts_ready or ws_state != WS_STATE_ACTIVE:
                    print(f"[TTS] Skipping synthesis - TTS ready: {tts_ready}, state: {ws_state}", flush=True)
                    return
                
                try:
                    print(f"[TTS] Synthesizing {context}: {text[:100]}...", flush=True)
                    
                    async for audio_chunk in deepgram_tts_client.synthesize_response(text):
                        if ws_state != WS_STATE_ACTIVE:
                            print(f"[TTS] State changed during synthesis, stopping", flush=True)
                            break
                        
                        frames, audio_conversion_state = pcm16_16k_to_mulaw8k_20ms_frames(audio_chunk, audio_conversion_state)
                        if frames and current_audio_queue is not None:
                            enqueue_audio_frames(frames)
                            print(f"[TTS] Enqueued {len(frames)} {context} frames", flush=True)
                except Exception as e:
                    print(f"[TTS] Error synthesizing {context}: {e}", flush=True)
            
            nonlocal tts_synthesize_func
            tts_synthesize_func = synthesize_text
            
            print("[TTS] Synthesis worker started", flush=True)
            
            try:
                while ws_state in [WS_STATE_INACTIVE, WS_STATE_ACTIVE]:
                    try:
                        text, context = await asyncio.wait_for(synthesis_queue.get(), timeout=1.0)
                        await synthesize_text(text, context)
                    except asyncio.TimeoutError:
                        continue  # Check state and continue
                    except Exception as e:
                        print(f"[TTS] Synthesis worker error: {e}", flush=True)
                        break
            finally:
                print("[TTS] Synthesis worker stopped", flush=True)
            
            return synthesis_queue

        async def pump_deepgram_tts_monitoring():
            """Monitor Deepgram TTS and maintain frame rate statistics."""
            from collections import deque
            import traceback
            
            nonlocal stream_sid, last_audio_time, frames_sent_count, audio_frames_count, silence_frames_count, current_audio_queue
            
            audio_sent_count = 0
            audio_failed_count = 0
            reconnection_attempts = 0
            buffer_processing = True
            
            async def frame_rate_monitor():
                """Monitor and log frame rate every second with enhanced audio/silence breakdown."""
                nonlocal frames_sent_count, silence_frames_count, audio_frames_count, ws_state
                last_total_count = 0
                last_silence_count = 0
                last_audio_count = 0
                
                while ws_state == WS_STATE_ACTIVE:
                    await asyncio.sleep(1.0)  # Every second
                    
                    if ws_state != WS_STATE_ACTIVE:
                        break
                    
                    current_total = frames_sent_count
                    current_silence = silence_frames_count
                    current_audio = audio_frames_count
                    
                    total_fps = current_total - last_total_count
                    silence_fps = current_silence - last_silence_count
                    audio_fps = current_audio - last_audio_count
                    
                    last_total_count = current_total
                    last_silence_count = current_silence
                    last_audio_count = current_audio
                    
                    if total_fps > 0:
                        performance_status = "✅ OPTIMAL" if audio_fps >= 45 else "⚠️ DEGRADED" if audio_fps >= 30 else "❌ POOR" if audio_fps > 0 else "🔇 SILENCE"
                        print(f"[MONITOR] Frame rate: {total_fps} fps (audio: {audio_fps}, silence: {silence_fps}) | target: {FRAME_RATE_TARGET} fps | {performance_status}, total: {current_total}", flush=True)
            
            sender_task = None
            monitor_task = asyncio.create_task(frame_rate_monitor())
            
            async def check_websocket_connection():
                """Check if WebSocket connection is healthy and ready for sending"""
                try:
                    if ws.client_state.name not in ["CONNECTED", "OPEN"]:
                        print(f"[RECONNECT] WebSocket in invalid state: {ws.client_state.name}", flush=True)
                        return False
                    
                    return True
                    
                except Exception as e:
                    print(f"[RECONNECT] Connection check failed: {e}", flush=True)
                    return False
            
            async def send_audio_with_retry(audio_data, max_retries=3):
                """Send audio with retry logic and connection validation"""
                nonlocal audio_sent_count, audio_failed_count, reconnection_attempts
                
                if ws_state != WS_STATE_ACTIVE or ws.client_state.name not in ["CONNECTED", "OPEN"]:
                    print(f"[RETRY] Connection not ready: state={ws_state}, ws_state={ws.client_state.name}", flush=True)
                    return False
                
                for attempt in range(max_retries):
                    try:
                        if not await check_websocket_connection():
                            print(f"[RETRY] WebSocket not ready (attempt {attempt + 1})", flush=True)
                            if attempt < max_retries - 1:
                                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                            continue
                        
                        if isinstance(audio_data, dict) and "event" in audio_data and "media" in audio_data:
                            media_payload = audio_data.get("media", {}).get("payload", "")
                            if isinstance(media_payload, bytes):
                                print(f"[RETRY] Converting bytes payload to base64", flush=True)
                                audio_data["media"]["payload"] = base64.b64encode(media_payload).decode("ascii")
                            
                            msg_json = json.dumps(audio_data)
                        else:
                            print(f"[RETRY] ERROR: Invalid audio message format, type: {type(audio_data)}, keys: {list(audio_data.keys()) if isinstance(audio_data, dict) else 'N/A'}", flush=True)
                            return False
                            
                        await ws.send_text(msg_json)
                        audio_sent_count += 1
                        print(f"[RETRY] ✅ Audio sent successfully (attempt {attempt + 1}), total sent: {audio_sent_count}", flush=True)
                        return True
                        
                    except Exception as e:
                        audio_failed_count += 1
                        error_msg = str(e).lower()
                        print(f"[RETRY] Attempt {attempt + 1} failed: {e}", flush=True)
                        
                        if any(keyword in error_msg for keyword in ["not connected", "closed", "accept first", "connection"]):
                            reconnection_attempts += 1
                            print(f"[RETRY] Connection error detected (reconnection attempt #{reconnection_attempts})", flush=True)
                            
                            if attempt == 0:  # Only log this once per audio chunk
                                print(f"[RETRY] WebSocket connection lost, will buffer audio for later delivery", flush=True)
                            break
                        
                        if attempt < max_retries - 1:
                            await asyncio.sleep(0.1 * (2 ** attempt))
                
                return False
            
            async def process_audio_buffer():
                """Process buffered audio when WebSocket is ready with enhanced retry logic"""
                nonlocal audio_sent_count, audio_failed_count
                
                while buffer_processing:
                    try:
                        if audio_buffer and await check_websocket_connection():
                            sent_count = 0
                            max_batch = min(10, len(audio_buffer))  # Send up to 10 at once
                            
                            while audio_buffer and sent_count < max_batch:
                                audio_data = audio_buffer.popleft()
                                
                                if isinstance(audio_data, bytes) and len(audio_data) == 160:
                                    payload_b64 = base64.b64encode(audio_data).decode("ascii")
                                    audio_msg = {
                                        "event": "media",
                                        "streamSid": stream_sid,
                                        "media": {"payload": payload_b64}
                                    }
                                    
                                    if await send_audio_with_retry(audio_msg, max_retries=2):
                                        sent_count += 1
                                    else:
                                        audio_buffer.appendleft(audio_data)
                                        break
                                else:
                                    print(f"[BUFFER] Invalid audio data format: type={type(audio_data)}, len={len(audio_data) if hasattr(audio_data, '__len__') else 'N/A'}", flush=True)
                                    sent_count += 1  # Skip invalid data
                            
                            if sent_count > 0:
                                print(f"[BUFFER] ✅ Sent {sent_count} buffered audio chunks, remaining: {len(audio_buffer)}", flush=True)
                            
                        await asyncio.sleep(0.02)  # Exactly 20ms for 50fps target
                    except Exception as e:
                        audio_failed_count += 1
                        print(f"[BUFFER] ❌ Error #{audio_failed_count} processing buffered audio: {e}", flush=True)
                        print(f"[BUFFER] Error traceback: {traceback.format_exc()}", flush=True)
                        await asyncio.sleep(0.1)
            
            buffer_task = asyncio.create_task(process_audio_buffer())
            
            try:
                while buffer_processing:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                print(f"[Google TTS] monitoring error: {e}", flush=True)
                print(f"[Google TTS] monitoring error traceback: {traceback.format_exc()}", flush=True)
            finally:
                buffer_processing = False
                print(f"[STATS] Audio sent: {audio_sent_count}, failed: {audio_failed_count}, reconnection attempts: {reconnection_attempts}", flush=True)
                print(f"[STATS] Total frames sent: {frames_sent_count} (audio: {audio_frames_count}, silence: {silence_frames_count})", flush=True)
                
                if 'buffer_task' in locals():
                    buffer_task.cancel()
                    try:
                        await buffer_task
                    except asyncio.CancelledError:
                        pass
                if 'sender_task' in locals() and sender_task:
                    sender_task.cancel()
                    try:
                        remaining_queue = await sender_task
                        print(f"[CLEANUP] 50fps sender cancelled, {len(remaining_queue) if remaining_queue else 0} frames remaining", flush=True)
                    except asyncio.CancelledError:
                        pass
                current_audio_queue = None
                if 'monitor_task' in locals():
                    monitor_task.cancel()
                    try:
                        await monitor_task
                    except asyncio.CancelledError:
                        pass

        
        async def perform_cleanup(reason: str):
            """Centralized cleanup with guard against double execution."""
            nonlocal cleanup_in_progress, ws_state, sender_task, tts_synthesis_task, deepgram_tts_task, deepgram_tts_client, stream_sid
            
            if cleanup_in_progress:
                print(f"[CLEANUP] Already in progress, skipping ({reason})", flush=True)
                return
            
            cleanup_in_progress = True
            ws_state = WS_STATE_CLOSING
            
            print(f"[CLEANUP] Starting cleanup due to: {reason}", flush=True)
            
            # Stop frame sending immediately
            stream_sid = None
            
            # Cancel sender task
            if sender_task:
                print("[CLEANUP] Cancelling sender task", flush=True)
                sender_task.cancel()
                try:
                    remaining_queue = await asyncio.wait_for(sender_task, timeout=2.0)
                    print(f"[CLEANUP] Sender cancelled, {len(remaining_queue) if remaining_queue else 0} frames remaining", flush=True)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    print("[CLEANUP] Sender task cancellation completed", flush=True)
                sender_task = None
            
            if tts_synthesis_task:
                print("[CLEANUP] Cancelling TTS synthesis task", flush=True)
                tts_synthesis_task.cancel()
                try:
                    await asyncio.wait_for(tts_synthesis_task, timeout=2.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    print("[CLEANUP] TTS synthesis task cancelled", flush=True)
                tts_synthesis_task = None
            
            if deepgram_tts_task:
                print("[CLEANUP] Cancelling Deepgram TTS monitoring task", flush=True)
                deepgram_tts_task.cancel()
                try:
                    await asyncio.wait_for(deepgram_tts_task, timeout=3.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    print("[CLEANUP] Deepgram TTS monitoring cancelled", flush=True)
                deepgram_tts_task = None
            
            if deepgram_tts_client:
                try:
                    print("[CLEANUP] Closing Deepgram TTS client", flush=True)
                    await deepgram_tts_client.close()
                except Exception as e:
                    print(f"[CLEANUP] Error closing Deepgram TTS client: {e}", flush=True)
                deepgram_tts_client = None
            
            ws_state = WS_STATE_CLOSED
            print(f"[CLEANUP] Completed cleanup due to: {reason}", flush=True)

        # Don't start monitoring task immediately - wait for "start" event
        print("[Bridge] WebSocket connected, waiting for Twilio 'start' event", flush=True)

        while ws_state in [WS_STATE_INACTIVE, WS_STATE_ACTIVE]:
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                if ws_state == WS_STATE_ACTIVE and deepgram_tts_client and hasattr(deepgram_tts_client, 'ready') and deepgram_tts_client.ready:
                    print("[Twilio] WebSocket receive timeout during active synthesis, continuing...", flush=True)
                    continue
                else:
                    print("[Twilio] WebSocket receive timeout, no active synthesis, closing connection", flush=True)
                    await perform_cleanup("receive_timeout")
                    break
            except Exception as e:
                error_msg = str(e).lower()
                if any(keyword in error_msg for keyword in ["closed", "not connected", "accept first"]):
                    print(f"[Twilio] WebSocket receive error, connection lost: {e}", flush=True)
                    await perform_cleanup("websocket_error")
                    break
                else:
                    print(f"[Twilio] Unexpected receive error: {e}", flush=True)
                    await perform_cleanup("unexpected_error")
                    break
            
            data = json.loads(msg)

            event = data.get("event")
            if event == "start":
                start_data = data.get("start", {})
                phone_number = start_data.get("customParameters", {}).get("phone_number")
                session_id = start_data.get("streamSid")
                
                print(f"[Twilio] Start received for {phone_number}, streamSid: {session_id}", flush=True)
                
                stream_sid = session_id
                ws_state = WS_STATE_ACTIVE
                frames_sent_count = 0
                silence_frames_count = 0
                audio_frames_count = 0
                
                print(f"[Twilio] Media start for {phone_number}, streamSid: {session_id}, WS state: {ws.client_state.name}", flush=True)
                print(f"[Twilio] Start data: {json.dumps(start_data, indent=2)}", flush=True)
                
                if sender_task:
                    print("[Twilio] Cancelling previous sender task", flush=True)
                    sender_task.cancel()
                    try:
                        await sender_task
                    except asyncio.CancelledError:
                        pass
                
                if tts_synthesis_task:
                    print("[Twilio] Cancelling previous TTS synthesis task", flush=True)
                    tts_synthesis_task.cancel()
                    try:
                        await tts_synthesis_task
                    except asyncio.CancelledError:
                        pass
                
                if deepgram_tts_task:
                    print("[Twilio] Cancelling previous monitoring task", flush=True)
                    deepgram_tts_task.cancel()
                    try:
                        await deepgram_tts_task
                    except asyncio.CancelledError:
                        pass
                
                # Start all tasks after "start" event
                sender_task = asyncio.create_task(dedicated_50fps_sender())
                tts_synthesis_task = asyncio.create_task(tts_synthesis_worker())
                
                await asyncio.sleep(0.2)
                
                deepgram_tts_task = asyncio.create_task(pump_deepgram_tts_monitoring())
                print("[Twilio] Started dedicated 50fps sender, TTS synthesis, and monitoring tasks", flush=True)
                
                if deepgram_tts_client and tts_ready and tts_synthesize_func:
                    greeting_text = "Muraho! Welcome to BAKAME, your AI learning companion. I'm ready to help you learn!"
                    print(f"[GREETING] Queuing welcome message for synthesis", flush=True)
                    await tts_synthesize_func(greeting_text, "greeting")
                else:
                    print(f"[GREETING] TTS not ready - client: {bool(deepgram_tts_client)}, ready: {tts_ready}, func: {bool(tts_synthesize_func)}", flush=True)
                
                while pending_mulaw_frames:
                    frame = pending_mulaw_frames.popleft()
                    frames_sent = await send_twilio_media_frames(ws, stream_sid, [frame], ws_state == WS_STATE_ACTIVE)
                    if frames_sent == 0:  # WebSocket error occurred
                        print("[BUFFER] WebSocket error during buffer flush, stopping", flush=True)
                        break
                    frames_sent_count += frames_sent if frames_sent else 1
                    audio_frames_count += frames_sent if frames_sent else 1
                    print(f"[DEBUG] Successfully incremented audio_frames_count to {audio_frames_count} (buffer flush)", flush=True)
                    print(f"[BUFFER] Flushed buffered frame to Twilio, total sent: {frames_sent_count} (audio: {audio_frames_count})", flush=True)

            elif event == "media":
                media_data = data.get("media", {})
                payload_b64 = media_data.get("payload", "")
                track = media_data.get("track", "inbound")
                timestamp = media_data.get("timestamp", "unknown")
                
                print(f"[Twilio] Received media: track={track}, timestamp={timestamp}, payload_len={len(payload_b64)}", flush=True)
                
                if payload_b64:
                    pcm16k = twilio_ulaw8k_to_pcm16_16k(payload_b64)
                    
                    has_voice = detect_voice_activity(pcm16k)
                    if has_voice:
                        print(f"[VAD] Voice activity detected, buffering audio", flush=True)
                        audio_buffer.append(pcm16k)
                        if buffer_start_time is None:
                            buffer_start_time = asyncio.get_event_loop().time()
                    else:
                        print(f"[VAD] No voice activity, skipping audio chunk", flush=True)
                        continue
                    
                    current_time = asyncio.get_event_loop().time()
                    if (current_time - buffer_start_time >= AUDIO_BUFFER_DURATION or 
                        len(audio_buffer) > 32000):
                        
                        if len(audio_buffer) > 0:
                            print(f"[Twilio] Processing audio buffer: {len(audio_buffer)} chunks", flush=True)
                            ai_response = await process_audio_buffer(audio_buffer, phone_number, session_id, deepgram_tts_client)
                            audio_buffer.clear()
                            buffer_start_time = None
                            
                            if ai_response and ai_response.strip() and deepgram_tts_client and tts_ready and tts_synthesize_func:
                                try:
                                    print(f"[Deepgram TTS] Queuing response for synthesis: {ai_response[:100]}...", flush=True)
                                    
                                    if ws_state != WS_STATE_ACTIVE or ws.client_state.name not in ["CONNECTED", "OPEN"]:
                                        print(f"[Deepgram TTS] WebSocket not ready for synthesis, state: {ws.client_state.name}, ws_state: {ws_state}", flush=True)
                                        continue
                                    
                                    await tts_synthesize_func(ai_response, "response")
                                    print("[TTS] Response queued for synthesis", flush=True)
                                except Exception as e:
                                    print(f"[Deepgram TTS] Error queuing response: {e}", flush=True)

                    print(f"[Twilio→STT] Received {len(pcm16k)} bytes of audio data", flush=True)
                else:
                    print("[Twilio] Received media event with no payload", flush=True)

            elif event == "stop":
                print(f"[Twilio] Stop received at {time.time()}, WS state: {ws.client_state.name}", flush=True)
                
                ws_state = WS_STATE_CLOSING
                
                await perform_cleanup("stop_event")
                break
            
            else:
                print(f"[Twilio] Unhandled event: {event}", flush=True)
                print(f"[Twilio] Event data: {json.dumps(data, indent=2)[:300]}...", flush=True)


    except WebSocketDisconnect:
        print(f"[Twilio] WS disconnected at {time.time()}", flush=True)
        if ws_state != WS_STATE_CLOSED:
            await perform_cleanup("websocket_disconnect")
    except Exception as e:
        print(f"[Bridge] error: {e}", flush=True)
        import traceback
        print(f"[Bridge] error traceback: {traceback.format_exc()}", flush=True)
        if ws_state != WS_STATE_CLOSED:
            await perform_cleanup("exception")
    finally:
        try:
            if ws and ws.client_state.name in ["CONNECTED", "OPEN"]:
                print(f"[Bridge] Closing Twilio WebSocket, state: {ws.client_state.name}", flush=True)
                await ws.close()
        except Exception as e:
            if "close message" not in str(e).lower():
                print(f"[Bridge] Error closing Twilio WebSocket: {e}", flush=True)
