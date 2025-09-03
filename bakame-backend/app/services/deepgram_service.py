import requests
import tempfile
import os
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from app.config import settings

class DeepgramService:
    def __init__(self):
        self.api_key = settings.deepgram_api_key
        self.base_url = "https://api.deepgram.com/v1/speak"
        
        self.african_male_voices = {
            "aura-2-aries-en": "Warm, Energetic, Caring male voice",
            "aura-2-arcas-en": "Natural, Smooth, Clear male voice", 
            "aura-2-apollo-en": "Confident, Comfortable male voice"
        }
        
        self.default_voice = getattr(settings, 'tts_voice', 'aura-2-aries-en')
        self.default_rate = getattr(settings, 'tts_rate', 0.95)
        self.default_pitch = getattr(settings, 'tts_pitch', '-1st')
        self.default_style = getattr(settings, 'tts_style', 'conversational')
    
    async def text_to_speech(self, 
                            text: str, 
                            voice: str = None,
                            rate: float = None,
                            pitch: str = None,
                            style: str = None,
                            lang: str = "en",
                            **kwargs) -> Optional[str]:
        """Convert text to speech using Deepgram with kid-friendly settings"""
        voice = voice or self.default_voice
        rate = rate or self.default_rate
        pitch = pitch or self.default_pitch
        style = style or self.default_style
        
        try:
            print(f"DEBUG: Deepgram TTS - Voice: {voice}, Rate: {rate}, Pitch: {pitch}")
            print(f"DEBUG: Deepgram TTS - Text length: {len(text)}")
            
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text
            }
            
            params = {
                "model": voice,
                "encoding": "mulaw",  # Direct μ-law encoding for Twilio compatibility
                "sample_rate": 8000,  # Telephony standard sample rate
                "channels": 1,  # Mono
                "bit_depth": 8  # 8-bit for μ-law
            }
            
            if rate != 1.0:
                params["rate"] = str(rate)
            if pitch and pitch != "0st":
                params["pitch"] = pitch
            if style:
                params["style"] = style
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    params=params
                ) as response:
                    
                    print(f"DEBUG: Deepgram - Response status: {response.status}")
                    if response.status == 200:
                        audio_data = await response.read()
                        
                        call_sid = kwargs.get('call_sid', 'default')
                        audio_dir = f"/tmp/audio/tts/{call_sid}"
                        os.makedirs(audio_dir, exist_ok=True)
                        
                        sequence = kwargs.get('sequence', 1)
                        audio_file = f"{audio_dir}/{sequence}.wav"
                        
                        with open(audio_file, 'wb') as f:
                            f.write(audio_data)
                        
                        print(f"DEBUG: Deepgram - μ-law audio saved to: {audio_file}")
                        return audio_file
                    else:
                        error_text = await response.text()
                        print(f"Deepgram TTS error: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            print(f"Error in Deepgram TTS: {e}")
            return None
    
    def _get_audio_headers(self, file_path: str) -> dict:
        """Get proper headers for audio file serving"""
        file_size = os.path.getsize(file_path)
        return {
            "Content-Type": "audio/wav",
            "Content-Length": str(file_size),
            "Cache-Control": "no-cache"
        }
    
    def split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences for chunked playback with prosody"""
        import re
        
        abbreviations = ['Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'etc.', 'vs.', 'e.g.', 'i.e.']
        
        temp_text = text
        for i, abbr in enumerate(abbreviations):
            temp_text = temp_text.replace(abbr, f"__ABBR_{i}__")
        
        sentences = re.split(r'[.!?]+', temp_text)
        
        result = []
        for sentence in sentences:
            if sentence.strip():
                for i, abbr in enumerate(abbreviations):
                    sentence = sentence.replace(f"__ABBR_{i}__", abbr)
                
                if len(sentence) > 120:  # Approximate 2 lines
                    sub_sentences = re.split(r'[,;]|\s+(?:and|but|or|so)\s+', sentence)
                    result.extend([s.strip() for s in sub_sentences if s.strip()])
                else:
                    result.append(sentence.strip())
        
        return result
    
    async def _fallback_tts(self, text: str) -> Optional[str]:
        """Fallback TTS using OpenAI or Twilio Say as last resort"""
        try:
            from app.services.openai_service import openai_service
            if hasattr(openai_service, 'text_to_speech'):
                return await openai_service.text_to_speech(text)
        except Exception as e:
            print(f"OpenAI TTS fallback failed: {e}")
        
        return None
    
    async def text_to_speech_with_fallback(self, text: str, **kwargs) -> Optional[str]:
        """Text to speech with comprehensive fallback chain"""
        result = await self.text_to_speech(text, **kwargs)
        if result:
            return result
            
        print("Deepgram TTS failed, trying fallback providers...")
        return await self._fallback_tts(text)

    async def generate_chunked_audio(self, text: str, call_sid: str = None, **kwargs) -> list[Dict[str, Any]]:
        """Generate audio chunks with micro-pauses for natural prosody"""
        sentences = self.split_into_sentences(text)
        audio_chunks = []
        
        for i, sentence in enumerate(sentences):
            chunk_kwargs = {**kwargs, 'call_sid': call_sid or 'default', 'sequence': i + 1}
            audio_file = await self.text_to_speech(sentence, **chunk_kwargs)
            if audio_file:
                audio_chunks.append({
                    "audio_file": audio_file,
                    "text": sentence,
                    "sequence": i + 1,
                    "pause_after": 200 if i < len(sentences) - 1 else 0,
                    "headers": self._get_audio_headers(audio_file)
                })
        
        return audio_chunks
    
    async def generate_chunked_audio_with_fallback(self, text: str, call_sid: str = None, **kwargs) -> list[Dict[str, Any]]:
        """Generate audio chunks with fallback support"""
        sentences = self.split_into_sentences(text)
        audio_chunks = []
        
        for i, sentence in enumerate(sentences):
            chunk_kwargs = {**kwargs, 'call_sid': call_sid or 'default', 'sequence': i + 1}
            audio_file = await self.text_to_speech_with_fallback(sentence, **chunk_kwargs)
            
            if audio_file:
                audio_chunks.append({
                    "audio_file": audio_file,
                    "text": sentence,
                    "sequence": i + 1,
                    "pause_after": 200 if i < len(sentences) - 1 else 0,
                    "headers": self._get_audio_headers(audio_file)
                })
            else:
                return []
        
        return audio_chunks
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get list of available African male voices"""
        return self.african_male_voices.copy()
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary audio file"""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error cleaning up temp file: {e}")

deepgram_service = DeepgramService()
