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
    
    async def create_voice_response(self, message: str, gather_input: bool = True, timeout: int = 60) -> str:
        """Create TwiML voice response using Twilio Say verb
        
        Args:
            message: The text to speak
            gather_input: Whether to gather speech input from the user
            timeout: Seconds to wait for user speech (default 60 seconds)
        """
        response = VoiceResponse()
        try:
            if gather_input:
                gather = response.gather(
                    input='speech',
                    timeout=timeout,  # Use configurable timeout (default 60 seconds)
                    speech_timeout='auto',
                    action='/webhook/voice/process',
                    method='POST'
                )
                gather.say(message, voice='man', language='en-US')
                # If no speech detected, redirect back to process endpoint
                # Don't say anything hardcoded, let AI handle it
                response.redirect('/webhook/voice/process')
            else:
                response.say(message, voice='man', language='en-US')
                # Don't hang up - keep the call going
                response.redirect('/webhook/voice/process')
        except Exception as e:
            response.say(f"Error: {str(e)}", voice='man', language='en-US')
            # Don't hang up on errors either - try to recover
            response.redirect('/webhook/voice/process')
        
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
