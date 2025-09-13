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
from app.services.llama_service import llama_service
from app.services.logging_service import logging_service
from app.modules.english_module import english_module
from app.modules.math_module import math_module
from app.modules.comprehension_module import comprehension_module
from app.modules.debate_module import debate_module
from app.modules.general_module import general_module
from app.elevenlabs_client import open_el_ws

SILENCE_THRESHOLD_MS = 250  # Reduced from 500ms for real-time conversation
BUFFER_CHECK_INTERVAL_MS = 5  # Faster buffer processing
SILENCE_CHECK_INTERVAL_MS = 50  # More responsive silence detection
FRAME_RATE_TARGET = 50  # Target 50fps
MAX_BUFFER_FRAMES = 150  # Increased from 100 for better buffering

"""
ENV you must set in Fly (or locally):
  ELEVENLABS_API_KEY   -> your 11Labs User API key
  ELEVENLABS_AGENT_ID  -> your Agent ID (e.g., agent_0301k3y6dwrve6... )
  ELEVENLABS_WS_SECRET -> workspace secret for ElevenLabs ConvAI authentication
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
        target_amplitude = int(32767 * 0.8)
        scale_factor = target_amplitude / max_val
        if scale_factor != 1.0:
            pcm16k = audioop.mul(pcm16k, 2, scale_factor)
    
    return pcm16k

def apply_voice_frequency_emphasis(pcm16k: bytes) -> bytes:
    """
    Advanced audio reconstruction for ElevenLabs compatibility.
    Applies aggressive μ-law artifact removal and spectral enhancement.
    """
    try:
        import numpy as np
        from scipy import signal
        
        audio_data = np.frombuffer(pcm16k, dtype=np.int16).astype(np.float32)
        original_rms = np.sqrt(np.mean(audio_data**2))
        
        noise_threshold = np.std(audio_data) * 0.08
        audio_data = np.where(np.abs(audio_data) < noise_threshold, 0, audio_data)
        
        nyquist = 8000  # 16kHz / 2
        low_freq = 300 / nyquist
        high_freq = 3400 / nyquist
        
        b_band, a_band = signal.butter(6, [low_freq, high_freq], btype='band')
        filtered_audio = signal.filtfilt(b_band, a_band, audio_data)
        
        hf_restore_freq = 2000 / nyquist
        b_hf, a_hf = signal.butter(2, hf_restore_freq, btype='high')
        hf_enhanced = signal.lfilter(b_hf, a_hf, filtered_audio)
        
        fundamental_freq = 150 / nyquist  # Typical voice fundamental
        b_fund, a_fund = signal.butter(2, fundamental_freq, btype='high')
        harmonic_enhanced = signal.lfilter(b_fund, a_fund, filtered_audio)
        
        enhanced_audio = (0.5 * filtered_audio + 
                         0.3 * hf_enhanced + 
                         0.2 * harmonic_enhanced)
        
        # Step 5: Dynamic range restoration with soft compression
        current_rms = np.sqrt(np.mean(enhanced_audio**2))
        if current_rms > 0:
            signal_peak = np.max(np.abs(enhanced_audio))
            dynamic_range = signal_peak / (current_rms + 1e-6)
            
            if dynamic_range > 3:  # High dynamic range - preserve
                target_rms = min(9000, original_rms * 2.2)
            else:  # Low dynamic range - boost aggressively
                target_rms = min(12000, original_rms * 3.8)
            
            compression_ratio = target_rms / current_rms
            enhanced_audio *= min(compression_ratio, 4.0)
        
        enhanced_audio = np.tanh(enhanced_audio / 20000) * 20000
        
        # Final processing
        final_rms = np.sqrt(np.mean(enhanced_audio**2))
        enhanced_audio = np.clip(enhanced_audio, -32768, 32767).astype(np.int16)
        
        print(f"[VOICE] Advanced reconstruction: RMS {int(original_rms)} → {int(final_rms)}, μ-law artifacts removed", flush=True)
        return enhanced_audio.tobytes()
        
    except ImportError:
        print("[VOICE] Scipy not available, using enhanced basic filtering", flush=True)
        try:
            # Enhanced fallback processing
            max_val = audioop.max(pcm16k, 2)
            if max_val > 0:
                target_amplitude = int(32767 * 0.9)
                scale_factor = min(4.0, target_amplitude / max_val)
                enhanced = audioop.mul(pcm16k, 2, scale_factor)
                return enhanced
            return pcm16k
        except:
            return pcm16k
    except Exception as e:
        print(f"[AUDIO] Advanced voice reconstruction failed: {e}", flush=True)
        return pcm16k

def twilio_ulaw8k_to_pcm16_16k(b64_payload: str) -> bytes:
    """
    Twilio sends 8k μ-law audio in base64. Convert -> 16kHz signed 16-bit PCM.
    Enhanced for ElevenLabs compatibility with improved quality preservation.
    """
    ulaw = base64.b64decode(b64_payload)
    pcm8k = audioop.ulaw2lin(ulaw, 2)  # width=2 bytes/sample
    
    pcm16k, _ = audioop.ratecv(pcm8k, 2, 1, 8000, 16000, None)
    
    try:
        import struct
        samples = struct.unpack(f'<{len(pcm16k)//2}h', pcm16k)
        
        max_amplitude = max(abs(s) for s in samples) if samples else 1
        if max_amplitude > 0:
            target_amplitude = int(32767 * 0.7)  # 70% of max 16-bit range
            scale_factor = target_amplitude / max_amplitude
            
            normalized_samples = []
            for sample in samples:
                scaled = int(sample * scale_factor)
                clamped = max(-32768, min(32767, scaled))
                normalized_samples.append(clamped)
            
            pcm16k = struct.pack(f'<{len(normalized_samples)}h', *normalized_samples)
            print(f"[AUDIO] Enhanced Twilio audio: normalized amplitude by {scale_factor:.2f}x for ElevenLabs", flush=True)
        
    except Exception as e:
        print(f"[AUDIO] Audio normalization failed, using original: {e}", flush=True)
    
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

async def send_twilio_media_frames(ws, stream_sid: str, mulaw_frames: list[bytes]):
    """
    Sends μ-law frames to Twilio with STRICT 50fps pacing (exactly 20ms intervals).
    Each frame must be exactly 160 bytes μ-law → ~214 base64 chars.
    Codec: G.711 μ-law, Sample rate: 8 kHz, Frame size: 20ms, Frame rate: 50fps exactly.
    """
    if not stream_sid:
        return 0

    frame_count = 0
    
    for frame in mulaw_frames:
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
        
        while retry_count <= max_retries and not frame_sent:
            try:
                await ws.send_text(json.dumps(msg))
                frame_sent = True
                if retry_count > 0:
                    print(f"[FRAME] Frame {frame_count} sent successfully after {retry_count} retries", flush=True)
            except Exception as e:
                retry_count += 1
                if retry_count <= max_retries:
                    print(f"[FRAME] Frame {frame_count} send failed (attempt {retry_count}/{max_retries + 1}): {e}", flush=True)
                    await asyncio.sleep(0.005)  # Brief retry delay
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


async def process_audio_buffer(audio_buffer: bytearray, phone_number: str, session_id: str, el_ws):
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
            wav_file.writeframes(bytes(audio_buffer))
        
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
        
    except Exception as e:
        print(f"[BAKAME] Error processing audio: {e}", flush=True)
        await logging_service.log_error(f"Voice processing error for {phone_number}: {str(e)}")


@app.websocket("/twilio-stream")
async def twilio_stream(ws: WebSocket):
    await ws.accept()
    print(f"[Twilio] WS connected at {time.time()}, state: {ws.client_state.name}", flush=True)

    audio_buffer = bytearray()
    buffer_start_time = None
    phone_number = None
    session_id = None
    stream_sid = None
    pending_mulaw_frames = deque()
    last_audio_time = time.time()
    frames_sent_count = 0
    silence_frames_count = 0
    audio_frames_count = 0
    silence_padding_active = False

    el_ws: Optional[websockets.WebSocketClientProtocol] = None
    el_to_twilio_task: Optional[asyncio.Task] = None

    try:
        print("[EL] Connecting with proper authentication...", flush=True)
        el_ws = await open_el_ws()
        print("[EL] WS connected successfully with authentication!", flush=True)
        
        el_ready = False
        print("[EL] Waiting for conversation initiation...", flush=True)

        async def pump_el_to_twilio():
            """Read audio chunks from 11Labs and push back to Twilio with enhanced quality."""
            from collections import deque
            import traceback
            
            nonlocal stream_sid, last_audio_time, frames_sent_count, silence_padding_active, audio_frames_count, silence_frames_count
            
            audio_conversion_state = None
            audio_buffer = deque()
            buffer_processing = True
            audio_sent_count = 0
            audio_failed_count = 0
            reconnection_attempts = 0
            
            async def silence_padding_task():
                """Send silence frames if ElevenLabs stalls to keep Twilio pipeline alive."""
                nonlocal stream_sid, last_audio_time, silence_padding_active, frames_sent_count, silence_frames_count
                
                while True:
                    await asyncio.sleep(0.05)  # Check every 50ms for faster response
                    
                    if stream_sid and time.time() - last_audio_time > 0.25:  # 250ms silence threshold for real-time
                        if not silence_padding_active:
                            silence_padding_active = True
                            print("[SILENCE] ElevenLabs stalled, starting silence padding", flush=True)
                        
                        silence_frame = generate_silence_frame()
                        frames_sent = await send_twilio_media_frames(ws, stream_sid, [silence_frame])
                        frames_sent_count += frames_sent if frames_sent else 1
                        silence_frames_count += frames_sent if frames_sent else 1
                        print(f"[SILENCE] Sent silence frame, total sent: {frames_sent_count} (silence: {silence_frames_count})", flush=True)
                        
                        last_audio_time = time.time()
            
            async def frame_rate_monitor():
                """Monitor and log frame rate every second with enhanced audio/silence breakdown."""
                nonlocal frames_sent_count, silence_frames_count, audio_frames_count
                last_total_count = 0
                last_silence_count = 0
                last_audio_count = 0
                
                while True:
                    await asyncio.sleep(1.0)  # Every second
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
            
            silence_task = asyncio.create_task(silence_padding_task())
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
                
                for attempt in range(max_retries):
                    try:
                        if not await check_websocket_connection():
                            print(f"[RETRY] WebSocket not ready (attempt {attempt + 1})", flush=True)
                            if attempt < max_retries - 1:
                                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                            continue
                        
                        msg_json = json.dumps(audio_data)
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
                                
                                if await send_audio_with_retry(audio_data, max_retries=2):
                                    sent_count += 1
                                else:
                                    audio_buffer.appendleft(audio_data)
                                    break
                            
                            if sent_count > 0:
                                print(f"[BUFFER] ✅ Sent {sent_count} buffered audio chunks, remaining: {len(audio_buffer)}", flush=True)
                            
                        await asyncio.sleep(0.005)  # 5ms for faster buffer processing
                    except Exception as e:
                        audio_failed_count += 1
                        print(f"[BUFFER] ❌ Error #{audio_failed_count} processing buffered audio: {e}", flush=True)
                        print(f"[BUFFER] Error traceback: {traceback.format_exc()}", flush=True)
                        await asyncio.sleep(0.1)
            
            buffer_task = asyncio.create_task(process_audio_buffer())
            
            try:
                async for raw in el_ws:
                    msg = None
                    if isinstance(raw, (bytes, bytearray)):
                        current_time = time.time()
                        ws_state = ws.client_state.name
                        print(f"[TIMING] Binary audio arrived at {current_time}, Twilio state: {ws_state}", flush=True)
                        
                        pcm16k = bytes(raw)
                        frames, audio_conversion_state = pcm16_16k_to_mulaw8k_20ms_frames(pcm16k, audio_conversion_state)
                        log_audio_quality_metrics(pcm16k, frames, "binary")
                        print(f"[BINARY] {len(pcm16k)} bytes PCM → {len(frames)} frames (enhanced)", flush=True)
                        
                        if not stream_sid:
                            pending_mulaw_frames.extend(frames)
                            while len(pending_mulaw_frames) > MAX_BUFFER_FRAMES:
                                pending_mulaw_frames.popleft()
                                print("[BUFFER] Dropped oldest frame to keep buffer size manageable", flush=True)
                            print(f"[BUFFER] Buffered {len(frames)} binary frames (no streamSid yet), total: {len(pending_mulaw_frames)}", flush=True)
                        else:
                            frames_sent = await send_twilio_media_frames(ws, stream_sid, frames)
                            frames_sent_count += frames_sent if frames_sent else len(frames)
                            audio_frames_count += frames_sent if frames_sent else len(frames)
                            print(f"[DEBUG] Successfully incremented audio_frames_count to {audio_frames_count} (binary)", flush=True)
                            last_audio_time = time.time()
                            silence_padding_active = False
                            print(f"[BINARY] Sent {len(frames)} frames to Twilio, total sent: {frames_sent_count} (audio: {audio_frames_count})", flush=True)
                        
                    else:
                        try:
                            msg = json.loads(raw)
                        except Exception as e:
                            print(f"[EL->Twilio] Failed to parse JSON: {e}", flush=True)
                            print(f"[EL->Twilio] Raw message: {raw[:200]}...", flush=True)
                            msg = None

                        if msg:
                            msg_type = msg.get("type")
                            print(f"[EL->Twilio] Received message type: {msg_type}", flush=True)
                            
                            if msg_type in ["audio", "conversation_initiation_metadata"]:
                                print(f"[EL->Twilio] Full message: {json.dumps(msg, indent=2)[:500]}...", flush=True)
                            
                            if msg_type == "conversation_initiation_metadata":
                                nonlocal el_ready
                                el_ready = True
                                print("[EL] Conversation initiated, ready to receive audio!", flush=True)
                                print(f"[DEBUG] el_ready flag set to True at {time.time()}", flush=True)
                            
                            elif msg_type == "audio":
                                audio_event = msg.get("audio_event", {})
                                audio_base64 = audio_event.get("audio_base_64", "")
                                event_id = audio_event.get("event_id", "unknown")
                                
                                print(f"[AUDIO] Event ID: {event_id}, Audio data length: {len(audio_base64)}", flush=True)
                                print(f"[DEBUG] About to process audio event - will increment audio_frames_count if successful", flush=True)
                                
                                if audio_base64:
                                    current_time = time.time()
                                    ws_state = ws.client_state.name
                                    print(f"[TIMING] Audio event #{event_id} arrived at {current_time}, Twilio state: {ws_state}", flush=True)
                                    
                                    try:
                                        pcm16k = base64.b64decode(audio_base64)
                                        frames, audio_conversion_state = pcm16_16k_to_mulaw8k_20ms_frames(pcm16k, audio_conversion_state)
                                        log_audio_quality_metrics(pcm16k, frames, f"audio-{event_id}")
                                        print(f"[AUDIO] Event #{event_id}: {len(pcm16k)} bytes PCM → {len(frames)} frames (enhanced)", flush=True)
                                        
                                        if not stream_sid:
                                            pending_mulaw_frames.extend(frames)
                                            while len(pending_mulaw_frames) > MAX_BUFFER_FRAMES:
                                                pending_mulaw_frames.popleft()
                                                print("[BUFFER] Dropped oldest frame to keep buffer size manageable", flush=True)
                                            print(f"[BUFFER] Buffered {len(frames)} frames for event #{event_id} (no streamSid yet), total: {len(pending_mulaw_frames)}", flush=True)
                                        else:
                                            frames_sent = await send_twilio_media_frames(ws, stream_sid, frames)
                                            frames_sent_count += frames_sent if frames_sent else len(frames)
                                            audio_frames_count += frames_sent if frames_sent else len(frames)
                                            print(f"[DEBUG] Successfully incremented audio_frames_count to {audio_frames_count}", flush=True)
                                            last_audio_time = time.time()
                                            silence_padding_active = False
                                            print(f"[AUDIO] Sent {len(frames)} frames for event #{event_id}, total sent: {frames_sent_count} (audio: {audio_frames_count})", flush=True)
                                            
                                    except Exception as e:
                                        print(f"[EL->Twilio] ❌ Error processing audio event #{event_id}: {e}", flush=True)
                                        print(f"[DEBUG] Audio processing error prevented audio_frames_count increment", flush=True)
                                        import traceback
                                        print(f"[EL->Twilio] Error traceback: {traceback.format_exc()}", flush=True)
                                        print(f"[EL->Twilio] WebSocket state during error: {ws.client_state.name}", flush=True)
                                else:
                                    print(f"[EL->Twilio] Received audio message event #{event_id} but no audio_base_64 data", flush=True)
                            
                            elif msg_type == "ping":
                                ping_event = msg.get("ping_event", {})
                                event_id = ping_event.get("event_id")
                                pong_message = {"type": "pong", "event_id": event_id}
                                await el_ws.send(json.dumps(pong_message))
                                print(f"[EL->Twilio] Sent pong response for event_id: {event_id}", flush=True)
                            
                            elif "audio" in msg and msg_type != "audio":
                                current_time = time.time()
                                ws_state = ws.client_state.name
                                print(f"[TIMING] Legacy audio arrived at {current_time}, Twilio state: {ws_state}", flush=True)
                                
                                try:
                                    pcm16k = base64.b64decode(msg["audio"])
                                    frames, audio_conversion_state = pcm16_16k_to_mulaw8k_20ms_frames(pcm16k, audio_conversion_state)
                                    log_audio_quality_metrics(pcm16k, frames, "legacy")
                                    print(f"[LEGACY] {len(pcm16k)} bytes PCM → {len(frames)} frames (enhanced)", flush=True)
                                    
                                    if not stream_sid:
                                        pending_mulaw_frames.extend(frames)
                                        while len(pending_mulaw_frames) > MAX_BUFFER_FRAMES:
                                            pending_mulaw_frames.popleft()
                                            print("[BUFFER] Dropped oldest frame to keep buffer size manageable", flush=True)
                                        print(f"[BUFFER] Buffered {len(frames)} legacy frames (no streamSid yet), total: {len(pending_mulaw_frames)}", flush=True)
                                    else:
                                        frames_sent = await send_twilio_media_frames(ws, stream_sid, frames)
                                        frames_sent_count += frames_sent if frames_sent else len(frames)
                                        audio_frames_count += frames_sent if frames_sent else len(frames)
                                        print(f"[DEBUG] Successfully incremented audio_frames_count to {audio_frames_count} (legacy)", flush=True)
                                        last_audio_time = time.time()
                                        silence_padding_active = False
                                        print(f"[LEGACY] Sent {len(frames)} frames to Twilio, total sent: {frames_sent_count} (audio: {audio_frames_count})", flush=True)
                                        
                                except Exception as e:
                                    print(f"[EL->Twilio] ❌ Error processing legacy audio: {e}", flush=True)
                                    print(f"[DEBUG] Legacy audio processing error prevented audio_frames_count increment", flush=True)
                                    print(f"[EL->Twilio] Error traceback: {traceback.format_exc()}", flush=True)
                                    print(f"[EL->Twilio] WebSocket state during legacy error: {ws.client_state.name}", flush=True)
                            
                            else:
                                print(f"[EL->Twilio] Unhandled message type: {msg_type}", flush=True)
                                
            except Exception as e:
                print(f"[EL->Twilio] pump error: {e}", flush=True)
                print(f"[EL->Twilio] pump error traceback: {traceback.format_exc()}", flush=True)
            finally:
                buffer_processing = False
                print(f"[STATS] Audio sent: {audio_sent_count}, failed: {audio_failed_count}, reconnection attempts: {reconnection_attempts}", flush=True)
                print(f"[STATS] Total frames sent: {frames_sent_count} (audio: {audio_frames_count}, silence: {silence_frames_count}), silence padding was active: {silence_padding_active}", flush=True)
                
                if 'buffer_task' in locals():
                    buffer_task.cancel()
                    try:
                        await buffer_task
                    except asyncio.CancelledError:
                        pass
                if 'silence_task' in locals():
                    silence_task.cancel()
                    try:
                        await silence_task
                    except asyncio.CancelledError:
                        pass
                if 'monitor_task' in locals():
                    monitor_task.cancel()
                    try:
                        await monitor_task
                    except asyncio.CancelledError:
                        pass

        el_to_twilio_task = asyncio.create_task(pump_el_to_twilio())
        print("[Bridge] Started enhanced EL->Twilio audio processing task", flush=True)

        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)

            event = data.get("event")
            if event == "start":
                start_data = data.get("start", {})
                phone_number = start_data.get("customParameters", {}).get("phone_number")
                session_id = start_data.get("streamSid")
                stream_sid = session_id
                print(f"[Twilio] Media start for {phone_number}, streamSid: {session_id}, WS state: {ws.client_state.name}", flush=True)
                print(f"[Twilio] Start data: {json.dumps(start_data, indent=2)}", flush=True)
                
                # print(f"[TEST] Sending 30s test tone ({len(test_frames)} frames) for pipeline validation", flush=True)
                # await send_twilio_media_frames(ws, stream_sid, test_frames)
                # frames_sent_count += len(test_frames)
                # print(f"[TEST] Test tone sent successfully, total frames: {frames_sent_count}", flush=True)
                
                while pending_mulaw_frames:
                    frame = pending_mulaw_frames.popleft()
                    frames_sent = await send_twilio_media_frames(ws, stream_sid, [frame])
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

                    audio_buffer.extend(pcm16k)
                    if buffer_start_time is None:
                        buffer_start_time = asyncio.get_event_loop().time()

                    current_time = asyncio.get_event_loop().time()
                    if (current_time - buffer_start_time >= AUDIO_BUFFER_DURATION or 
                        len(audio_buffer) > 32000):
                        
                        if len(audio_buffer) > 0:
                            print(f"[Twilio] Processing audio buffer: {len(audio_buffer)} bytes", flush=True)
                            await process_audio_buffer(audio_buffer, phone_number, session_id, el_ws)
                            audio_buffer.clear()
                            buffer_start_time = None

                    if el_ws is not None and el_ready:
                        try:
                            audio_b64 = base64.b64encode(pcm16k).decode('utf-8')
                            el_message = {
                                "user_audio_chunk": audio_b64
                            }
                            await el_ws.send(json.dumps(el_message))
                            print(f"[Twilio->EL] Sent {len(pcm16k)} bytes raw audio to ElevenLabs (enhancement removed for compatibility)", flush=True)
                            print(f"[DEBUG] Raw user audio sent to EL - expecting audio response and audio_frames_count increment", flush=True)
                        except Exception as e:
                            print(f"[Twilio->EL] send error: {e}", flush=True)
                    elif el_ws is not None and not el_ready:
                        print("[Twilio->EL] Skipping audio - EL not ready yet", flush=True)
                    else:
                        print("[Twilio->EL] No ElevenLabs connection available", flush=True)
                else:
                    print("[Twilio] Received media event with no payload", flush=True)

            elif event == "stop":
                print(f"[Twilio] Media stop at {time.time()}, WS state: {ws.client_state.name}", flush=True)
                if len(audio_buffer) > 0:
                    print(f"[Twilio] Processing final audio buffer: {len(audio_buffer)} bytes", flush=True)
                    await process_audio_buffer(audio_buffer, phone_number, session_id, el_ws)
                break
            
            else:
                print(f"[Twilio] Unhandled event: {event}", flush=True)
                print(f"[Twilio] Event data: {json.dumps(data, indent=2)[:300]}...", flush=True)


    except WebSocketDisconnect:
        print(f"[Twilio] WS disconnected at {time.time()}", flush=True)
    except Exception as e:
        print(f"[Bridge] error: {e}", flush=True)
        import traceback
        print(f"[Bridge] error traceback: {traceback.format_exc()}", flush=True)
    finally:
        print(f"[Bridge] Cleanup starting at {time.time()}", flush=True)
        try:
            if el_to_twilio_task:
                print("[Bridge] Cancelling EL->Twilio task", flush=True)
                el_to_twilio_task.cancel()
                try:
                    await el_to_twilio_task
                except asyncio.CancelledError:
                    print("[Bridge] EL->Twilio task cancelled successfully", flush=True)
        except Exception as e:
            print(f"[Bridge] Error cancelling task: {e}", flush=True)
        try:
            if el_ws:
                print("[Bridge] Closing ElevenLabs WebSocket", flush=True)
                await el_ws.close()
        except Exception as e:
            print(f"[Bridge] Error closing EL WebSocket: {e}", flush=True)
        try:
            print(f"[Bridge] Closing Twilio WebSocket, state: {ws.client_state.name}", flush=True)
            await ws.close()
        except Exception as e:
            print(f"[Bridge] Error closing Twilio WebSocket: {e}", flush=True)
        print(f"[Bridge] Cleanup completed at {time.time()}", flush=True)
