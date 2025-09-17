import asyncio
import os
from typing import Optional, AsyncGenerator
from google.cloud import texttospeech
from google.oauth2 import service_account
from app.services.google_tts_service import google_tts_service

class GoogleTTSClient:
    def __init__(self):
        self.ready = False
        self.conversation_active = False
        
    async def connect(self):
        """Initialize Google Cloud TTS connection."""
        try:
            print("[Google TTS] Initializing client...", flush=True)
            test_input = texttospeech.SynthesisInput(text="Connection test")
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000
            )
            
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/app/google_credentials.json")
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            
            credentials = credentials.with_quota_project("bakameai")
            client = texttospeech.TextToSpeechClient(credentials=credentials)
            
            response = client.synthesize_speech(
                request={
                    "input": test_input,
                    "voice": voice,
                    "audio_config": audio_config
                }
            )
            
            if response.audio_content:
                print("[Google TTS] ✅ Connection successful", flush=True)
                self.ready = True
                return True
            else:
                print("[Google TTS] ❌ Connection failed - no audio response", flush=True)
                return False
                
        except Exception as e:
            print(f"[Google TTS] ❌ Connection error: {e}", flush=True)
            return False
    
    async def synthesize_response(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize AI response text to audio stream."""
        if not self.ready:
            print("[Google TTS] Client not ready", flush=True)
            return
            
        async for audio_chunk in google_tts_service.synthesize_text_streaming(text):
            yield audio_chunk
    
    async def close(self):
        """Close Google TTS connection."""
        self.ready = False
        self.conversation_active = False
        print("[Google TTS] Connection closed", flush=True)

async def open_google_tts():
    """Create and connect Google TTS client."""
    client = GoogleTTSClient()
    if await client.connect():
        return client
    else:
        raise RuntimeError("Failed to connect to Google Cloud TTS")
