from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import base64
import asyncio
from app.services.redis_service import redis_service

router = APIRouter()

class SimpleVAD:
    """Simple Voice Activity Detection using audio level thresholds"""
    
    def __init__(self, threshold: float = 0.01):
        self.threshold = threshold
        self.speech_frames = 0
        self.silence_frames = 0
        
    def detect_speech(self, audio_data: bytes) -> bool:
        """Detect if audio contains speech based on simple amplitude analysis"""
        if len(audio_data) < 160:  # Minimum frame size
            return False
            
        samples = []
        for i in range(0, len(audio_data), 2):
            if i + 1 < len(audio_data):
                sample = int.from_bytes(audio_data[i:i+2], byteorder='little', signed=True)
                samples.append(sample)
        
        if not samples:
            return False
            
        rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
        normalized_rms = rms / 32768.0  # Normalize to 0-1 range
        
        if normalized_rms > self.threshold:
            self.speech_frames += 1
            self.silence_frames = 0
            return self.speech_frames > 3  # Require 3+ consecutive speech frames
        else:
            self.silence_frames += 1
            self.speech_frames = 0
            return False

@router.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle Twilio Media Stream WebSocket connection for VAD and barge-in"""
    await websocket.accept()
    
    call_sid = None
    vad = SimpleVAD()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("event") == "connected":
                print("Media stream connected")
                
            elif message.get("event") == "start":
                call_sid = message.get("start", {}).get("callSid")
                print(f"Media stream started for call: {call_sid}")
                
            elif message.get("event") == "media":
                if call_sid:
                    payload = message.get("media", {}).get("payload", "")
                    audio_data = base64.b64decode(payload)
                    
                    speech_detected = vad.detect_speech(audio_data)
                    
                    if speech_detected:
                        tts_playing = redis_service.get_session_data(call_sid, "tts_playing")
                        
                        if tts_playing:
                            redis_service.set_session_data(call_sid, "barge_in", "1", ttl=5)
                            print(f"Barge-in detected for call: {call_sid}")
                            
            elif message.get("event") == "stop":
                print(f"Media stream stopped for call: {call_sid}")
                break
                
    except WebSocketDisconnect:
        print(f"Media stream disconnected for call: {call_sid}")
    except Exception as e:
        print(f"Error in media stream: {e}")
