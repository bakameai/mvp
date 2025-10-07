import os
from typing import AsyncGenerator
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import VoiceSettings
from app.config import settings

class ElevenLabsTTSService:
    def __init__(self):
        self.client = AsyncElevenLabs(api_key=settings.elevenlabs_api_key)
        self.voice_id = "JBFqnCBsd6RMkjVDRZzb"
        self.model_id = "eleven_flash_v2_5"
        
    async def synthesize_text_streaming(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize text to speech using Eleven Labs TTS streaming."""
        try:
            print(f"[ElevenLabs TTS] Synthesizing: {text[:100]}...", flush=True)
            
            audio_stream = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                output_format="pcm_16000",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.3,
                    use_speaker_boost=True
                )
            )
            
            async for chunk in audio_stream:
                if isinstance(chunk, bytes) and len(chunk) > 0:
                    yield chunk
                    
        except Exception as e:
            print(f"[ElevenLabs TTS] Error synthesizing text: {e}", flush=True)
            return
