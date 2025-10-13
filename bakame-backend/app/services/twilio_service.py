import requests
import os
from typing import Optional

# Legacy Twilio imports - kept for backward compatibility
# These are now optional as we migrate to Telnyx
try:
    from twilio.rest import Client
    from twilio.twiml import TwiML
    from twilio.twiml.voice_response import VoiceResponse
    from twilio.twiml.messaging_response import MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    
from app.config import settings
from app.services.deepgram_service import deepgram_service
from app.services.openai_service import openai_service

class TwilioService:
    """Legacy Twilio Service - being phased out in favor of Telnyx"""
    
    def __init__(self):
        # Make Twilio initialization optional
        self.client = None
        self.phone_number = None
        
        if TWILIO_AVAILABLE:
            # Try to initialize if credentials exist in environment
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            phone_number = os.getenv("TWILIO_PHONE_NUMBER")
            
            if account_sid and auth_token:
                self.client = Client(account_sid, auth_token)
                self.phone_number = phone_number
                print("[Twilio] Legacy service initialized (for backward compatibility)")
            else:
                print("[Twilio] No credentials found - service disabled (using Telnyx instead)")
    
    async def create_voice_response(self, message: str, gather_input: bool = True, timeout: int = 60) -> str:
        """Create TwiML voice response using Twilio Say verb
        
        Args:
            message: The text to speak
            gather_input: Whether to gather speech input from the user
            timeout: Seconds to wait for user speech (default 60 seconds)
        """
        if not TWILIO_AVAILABLE:
            return "<!-- Twilio not available - using Telnyx instead -->"
        
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
        if not TWILIO_AVAILABLE:
            return "<!-- Twilio not available - using Telnyx instead -->"
        
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
