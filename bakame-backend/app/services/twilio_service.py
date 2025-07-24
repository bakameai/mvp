from twilio.rest import Client
from twilio.twiml import TwiML
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
import requests
from app.config import settings
from app.services.openai_service import openai_service

class TwilioService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.phone_number = settings.twilio_phone_number
    
    def create_voice_response(self, message: str, gather_input: bool = True) -> str:
        """Create TwiML voice response"""
        response = VoiceResponse()
        
        if gather_input:
            gather = response.gather(
                input='speech',
                timeout=10,
                speech_timeout='auto',
                action='/webhook/voice/process',
                method='POST'
            )
            gather.say(message, voice='man', language='en-KE')
            
            response.say("I didn't hear anything. Please try again.", voice='man', language='en-KE')
            response.redirect('/webhook/voice/process')
        else:
            response.say(message, voice='man', language='en-KE')
            response.hangup()
        
        return str(response)
    
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
