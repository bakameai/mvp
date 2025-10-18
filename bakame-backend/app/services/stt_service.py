import logging
import asyncio
from typing import Optional
from functools import partial
import requests
from app.config import settings

logger = logging.getLogger(__name__)

class STTService:
    """
    Service for Speech-to-Text using OpenAI Whisper API
    """
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.api_url = "https://api.openai.com/v1/audio/transcriptions"
    
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav") -> Optional[str]:
        """
        Transcribe audio to text using OpenAI Whisper API.
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (wav, mp3, etc.)
            
        Returns:
            Transcribed text or None if transcription failed
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            files = {
                "file": (f"audio.{audio_format}", audio_data, f"audio/{audio_format}")
            }
            
            data = {
                "model": "whisper-1",
                "language": "en"
            }
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    requests.post,
                    self.api_url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=30.0
                )
            )
            response.raise_for_status()
            
            result = response.json()
            transcription = result.get("text", "").strip()
            
            logger.info(f"Transcription successful: {transcription}")
            return transcription
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during transcription: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None

stt_service = STTService()
