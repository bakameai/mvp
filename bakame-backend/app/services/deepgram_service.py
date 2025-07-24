import requests
import tempfile
import os
from typing import Optional
from app.config import settings

class DeepgramService:
    def __init__(self):
        self.api_key = settings.deepgram_api_key
        self.base_url = "https://api.deepgram.com/v1/speak"
    
    async def text_to_speech(self, text: str, voice: str = "aura-asteria-en") -> Optional[str]:
        """Convert text to speech using Deepgram and return temporary file path"""
        try:
            print(f"DEBUG: Deepgram - API key: {self.api_key[:10]}...")
            print(f"DEBUG: Deepgram - Text length: {len(text)}")
            print(f"DEBUG: Deepgram - Voice: {voice}")
            
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text
            }
            
            params = {
                "model": voice,
                "encoding": "wav"
            }
            
            print(f"DEBUG: Deepgram - Making request to: {self.base_url}")
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                params=params
            )
            
            print(f"DEBUG: Deepgram - Response status: {response.status_code}")
            if response.status_code == 200:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.write(response.content)
                temp_file.close()
                print(f"DEBUG: Deepgram - Audio saved to: {temp_file.name}")
                return temp_file.name
            else:
                print(f"Deepgram TTS error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in Deepgram TTS: {e}")
            return None
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary audio file"""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error cleaning up temp file: {e}")

deepgram_service = DeepgramService()
