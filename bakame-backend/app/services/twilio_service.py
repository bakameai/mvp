from twilio.rest import Client
from twilio.twiml import TwiML
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
import asyncio
from app.config import settings
from app.services.deepgram_service import deepgram_service
from app.services.openai_service import openai_service

class TwilioService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.phone_number = settings.twilio_phone_number
    
    async def create_voice_response(self, message: str, gather_input: bool = True, call_sid: str = None, **tts_kwargs) -> str:
        """Create TwiML voice response with Deepgram audio playback and sentiment-aware TTS"""
        response = VoiceResponse()
        
        try:
            if call_sid and gather_input:
                connect = response.connect()
                stream = connect.stream(url=f'wss://your-domain.com/webhook/media-stream')
            
            audio_chunks = await deepgram_service.generate_chunked_audio_with_fallback(
                message, call_sid=call_sid, **tts_kwargs
            )
            
            if gather_input:
                gather = response.gather(
                    input='speech',
                    timeout=10,
                    speech_timeout='auto',
                    action='/webhook/voice/process',
                    method='POST'
                )
                
                if call_sid:
                    from app.services.redis_service import redis_service
                    redis_service.set_session_data(call_sid, "tts_playing", "1", ttl=30)
                
                for i, chunk in enumerate(audio_chunks):
                    if call_sid:
                        barge_in = redis_service.get_session_data(call_sid, "barge_in")
                        if barge_in:
                            redis_service.delete_session_data(call_sid, "barge_in")
                            redis_service.delete_session_data(call_sid, "tts_playing")
                            for remaining_chunk in audio_chunks[i:]:
                                deepgram_service.cleanup_temp_file(remaining_chunk['audio_file'])
                            break
                    
                    audio_url = self._get_audio_url(chunk['audio_file'])
                    gather.play(audio_url)
                    
                    if chunk['pause_after'] > 0:
                        gather.pause(length=chunk['pause_after'] / 1000.0)  # Convert ms to seconds
                
                if call_sid:
                    redis_service.delete_session_data(call_sid, "tts_playing")
                
                fallback_audio = await deepgram_service.text_to_speech_with_fallback(
                    "I didn't hear anything. Please try again."
                )
                if fallback_audio:
                    fallback_url = self._get_audio_url(fallback_audio)
                    response.play(fallback_url)
                    asyncio.create_task(self._cleanup_after_delay(fallback_audio, 60))
                else:
                    response.say("I didn't hear anything. Please try again.", voice='woman', language='en-US')
                
                response.redirect('/webhook/voice/process')
            else:
                audio_file = await deepgram_service.text_to_speech_with_fallback(message)
                if audio_file:
                    audio_url = self._get_audio_url(audio_file)
                    response.play(audio_url)
                    asyncio.create_task(self._cleanup_after_delay(audio_file, 60))
                else:
                    response.say(message, voice='woman', language='en-US')
                response.hangup()
            
            if audio_chunks:
                asyncio.create_task(self._cleanup_audio_chunks(audio_chunks, 300))  # 5 minutes
                    
        except Exception as e:
            print(f"Error in voice response generation: {e}")
            if gather_input:
                gather = response.gather(
                    input='speech',
                    timeout=10,
                    speech_timeout='auto',
                    action='/webhook/voice/process',
                    method='POST'
                )
                gather.say("Welcome to BAKAME learning assistant. Please say what you need help with.", voice='man', language='en-US')
                response.say("I didn't hear anything. Please try again.", voice='man', language='en-US')
                response.redirect('/webhook/voice/process')
            else:
                response.say("Thank you for using BAKAME. Goodbye!", voice='man', language='en-US')
                response.hangup()
        
        return str(response)
    
    def _get_audio_url(self, audio_file_path: str) -> str:
        """Generate URL for audio file that Twilio can access"""
        relative_path = audio_file_path.replace('/tmp/', '')
        
        base_url = "https://app-lfzepwvu.fly.dev"
        return f"{base_url}/{relative_path}"
    
    async def _cleanup_after_delay(self, audio_file: str, delay_seconds: int):
        """Clean up audio file after specified delay"""
        await asyncio.sleep(delay_seconds)
        deepgram_service.cleanup_temp_file(audio_file)
    
    async def _cleanup_audio_chunks(self, audio_chunks: list, delay_seconds: int):
        """Clean up all audio chunk files after specified delay"""
        await asyncio.sleep(delay_seconds)
        for chunk in audio_chunks:
            deepgram_service.cleanup_temp_file(chunk['audio_file'])
    
    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences for chunked playback (legacy method)"""
        return deepgram_service.split_into_sentences(text)
    
    def create_sms_response(self, message: str) -> str:
        """Create TwiML SMS response"""
        response = MessagingResponse()
        response.message(message)
        return str(response)
    
    async def download_recording(self, recording_url: str) -> bytes:
        """Download audio recording from Twilio"""
        try:
            auth = (settings.twilio_account_sid, settings.twilio_auth_token)
            response = requests.get(recording_url, auth=auth)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading recording: {e}")
            return b""
    
    def send_sms(self, to_number: str, message: str):
        """Send SMS message"""
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            return message.sid
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return None

twilio_service = TwilioService()
