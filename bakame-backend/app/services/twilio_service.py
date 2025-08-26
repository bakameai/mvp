from twilio.rest import Client
from twilio.twiml import TwiML
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
from app.config import settings
from app.services.deepgram_service import deepgram_service
from app.services.openai_service import openai_service

class TwilioService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.phone_number = settings.twilio_phone_number
    
    async def create_voice_response(self, message: str, gather_input: bool = True, call_sid: str = None) -> str:
        """Create TwiML voice response with barge-in support"""
        response = VoiceResponse()
        
        try:
            if call_sid and gather_input:
                connect = response.connect()
                stream = connect.stream(url=f'wss://your-domain.com/webhook/media-stream')
                
            sentences = self._split_into_sentences(message)
            
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
                
                for i, sentence in enumerate(sentences):
                    if call_sid:
                        barge_in = redis_service.get_session_data(call_sid, "barge_in")
                        if barge_in:
                            redis_service.delete_session_data(call_sid, "barge_in")
                            redis_service.delete_session_data(call_sid, "tts_playing")
                            break
                    
                    gather.say(sentence, voice='man', language='en-US')
                    
                    if i < len(sentences) - 1:
                        gather.pause(length=1)
                
                if call_sid:
                    redis_service.delete_session_data(call_sid, "tts_playing")
                
                response.say("I didn't hear anything. Please try again.", voice='man', language='en-US')
                response.redirect('/webhook/voice/process')
            else:
                response.say(message, voice='man', language='en-US')
                response.hangup()
                    
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
    
    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences for chunked playback"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
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
