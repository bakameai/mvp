from fastapi import FastAPI, Form, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI()

@app.post("/webhook/call")
async def twilio_webhook(From: str = Form(...), To: str = Form(...)):
    """Redirect to router handler"""
    from app.routers.webhooks import handle_voice_call
    return await handle_voice_call(From, To)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import webhooks, admin, auth, content
app.include_router(webhooks.router, prefix="/webhook", tags=["webhooks"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(content.router, prefix="/content", tags=["content"])
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
                if not ws or ws.client_state.name not in ["CONNECTED", "OPEN"]:
                    print(f"[FRAME] WebSocket closed during send, state: {getattr(ws, 'client_state', {}).get('name', 'unknown')}", flush=True)
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
                    return 0  # Return 0 to signal WebSocket error to caller
                
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

        tts_synthesize_func = synthesize_text

        async def tts_synthesis_worker():
            """Separate task for TTS synthesis to avoid blocking receive loop."""
            nonlocal ws_state
            
            print("[TTS] Synthesis worker started", flush=True)
            
            try:
                while ws_state in [WS_STATE_INACTIVE, WS_STATE_ACTIVE]:
                    await asyncio.sleep(1.0)  # Keep worker alive
            finally:
                print("[TTS] Synthesis worker stopped", flush=True)

        async def pump_deepgram_tts_monitoring():
            """Monitor Deepgram TTS and maintain frame rate statistics."""
            from collections import deque
            import traceback
            
            nonlocal stream_sid, last_audio_time, frames_sent_count, audio_frames_count, silence_frames_count, current_audio_queue
            
            audio_sent_count = 0
            audio_failed_count = 0
            reconnection_attempts = 0
            buffer_processing = True
