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
        
        self.kid_friendly_voices = {
            "aura-asteria-en": "Warm, friendly female voice",
            "aura-luna-en": "Gentle, nurturing female voice", 
            "aura-stella-en": "Bright, encouraging female voice"
        }
        
        self.default_voice = getattr(settings, 'tts_voice', 'aura-asteria-en')
        self.default_rate = getattr(settings, 'tts_rate', 0.95)
        self.default_pitch = getattr(settings, 'tts_pitch', '+1st')
        self.default_style = getattr(settings, 'tts_style', 'conversational')
    
    async def text_to_speech(self, 
                            text: str, 
                            voice: str = None,
                            rate: float = None,
                            pitch: str = None,
                            style: str = None,
                            lang: str = "en") -> Optional[str]:
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
                "encoding": "linear16",  # Use linear16 for high quality before conversion
                "sample_rate": 24000,  # Supported sample rate for linear16
                "channels": 1,  # Mono
                "bit_depth": 16
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
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                        content = await response.read()
                        temp_file.write(content)
                        temp_file.close()
                        
                        telephony_file = await self._convert_to_telephony_format(temp_file.name)
                        
                        self.cleanup_temp_file(temp_file.name)
                        
                        print(f"DEBUG: Deepgram - Telephony audio saved to: {telephony_file}")
                        return telephony_file
                    else:
                        error_text = await response.text()
                        print(f"Deepgram TTS error: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            print(f"Error in Deepgram TTS: {e}")
            return None
    
    async def _convert_to_telephony_format(self, input_file: str) -> Optional[str]:
        """Convert audio to 8kHz mono μ-law for telephony"""
        try:
            from app.utils.audio_transcode import convert_to_telephony
            return await convert_to_telephony(input_file)
        except ImportError:
            print("WARNING: Advanced audio transcoding not available, using basic conversion")
            return input_file
    
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

    async def generate_chunked_audio(self, text: str, **kwargs) -> list[Dict[str, Any]]:
        """Generate audio chunks with micro-pauses for natural prosody"""
        sentences = self.split_into_sentences(text)
        audio_chunks = []
        
        for i, sentence in enumerate(sentences):
            audio_file = await self.text_to_speech(sentence, **kwargs)
            
            if audio_file:
                audio_chunks.append({
                    "audio_file": audio_file,
                    "text": sentence,
                    "sequence": i,
                    "pause_after": 200 if i < len(sentences) - 1 else 0  # 200ms pause between sentences
                })
        
        return audio_chunks
    
    async def generate_chunked_audio_with_fallback(self, text: str, **kwargs) -> list[Dict[str, Any]]:
        """Generate audio chunks with fallback support"""
        sentences = self.split_into_sentences(text)
        audio_chunks = []
        
        for i, sentence in enumerate(sentences):
            audio_file = await self.text_to_speech_with_fallback(sentence, **kwargs)
            
            if audio_file:
                audio_chunks.append({
                    "audio_file": audio_file,
                    "text": sentence,
                    "sequence": i,
                    "pause_after": 200 if i < len(sentences) - 1 else 0
                })
            else:
                return []
        
        return audio_chunks
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get list of available kid-friendly voices"""
        return self.kid_friendly_voices.copy()
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary audio file"""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error cleaning up temp file: {e}")

deepgram_service = DeepgramService()
