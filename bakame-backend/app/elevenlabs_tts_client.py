import asyncio
from typing import Optional, AsyncGenerator
from app.services.elevenlabs_tts_service import ElevenLabsTTSService

class ElevenLabsTTSClient:
    def __init__(self):
        self.ready = False
        self.conversation_active = False
        self.service = None
        
    async def connect(self):
        """Initialize Eleven Labs TTS connection."""
        try:
            print("[ElevenLabs TTS] Initializing client...", flush=True)
            self.service = ElevenLabsTTSService()
            
            test_text = "Connection test"
            test_success = False
            
            async for chunk in self.service.synthesize_text_streaming(test_text):
                if chunk and len(chunk) > 0:
                    test_success = True
                    break
            
            if test_success:
                print("[ElevenLabs TTS] ✅ Connection successful", flush=True)
                self.ready = True
                return True
            else:
                print("[ElevenLabs TTS] ❌ Connection failed - no audio response", flush=True)
                return False
                
        except Exception as e:
            print(f"[ElevenLabs TTS] ❌ Connection error: {e}", flush=True)
            return False
    
    async def synthesize_response(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize AI response text to audio stream."""
        if not self.ready or not self.service:
            print("[ElevenLabs TTS] Client not ready", flush=True)
            return
            
        async for audio_chunk in self.service.synthesize_text_streaming(text):
            yield audio_chunk
    
    async def close(self):
        """Close Eleven Labs TTS connection."""
        self.ready = False
        self.conversation_active = False
        self.service = None
        print("[ElevenLabs TTS] Connection closed", flush=True)

async def open_elevenlabs_tts():
    """Create and connect Eleven Labs TTS client."""
    client = ElevenLabsTTSClient()
    if await client.connect():
        return client
    else:
        raise RuntimeError("Failed to connect to Eleven Labs TTS")
