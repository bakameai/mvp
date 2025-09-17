import asyncio
import base64
import os
from typing import Dict, Any, Optional, AsyncGenerator
from google.cloud import texttospeech
from google.oauth2 import service_account
import grpc

class GoogleTTSService:
    def __init__(self):
        credentials_path = "/home/ubuntu/repos/mvp/bakame-backend/google_credentials.json"
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        
        credentials = credentials.with_quota_project("bakameai")
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)
        self.voice_config = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000
        )
    
    async def synthesize_text_streaming(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize text to speech using Google Cloud TTS streaming."""
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice_config,
                audio_config=self.audio_config
            )
            
            audio_data = response.audio_content
            chunk_size = 1600
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                if chunk:
                    yield chunk
                    await asyncio.sleep(0.02)
                    
        except Exception as e:
            print(f"[Google TTS] Error synthesizing text: {e}", flush=True)
            return

google_tts_service = GoogleTTSService()
