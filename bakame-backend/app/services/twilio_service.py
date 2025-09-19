from twilio.rest import Client
from twilio.twiml import TwiML
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
from app.config import settings
from app.services.openai_service import openai_service

class TwilioService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.phone_number = settings.twilio_phone_number
    
    async def create_voice_response(self, message: str, gather_input: bool = True, end_call: bool = False) -> str:
        """Create TwiML voice response with premium neural voice"""
        response = VoiceResponse()
        
        try:
            voice_settings = {
                'voice': 'Polly.Joanna-Neural',  # Premium neural voice
                'language': 'en-US',
                'rate': 'medium',  # Natural speaking pace
            }
            
            clean_message = message
            
            if end_call:
                response.say(clean_message, **voice_settings)
                response.hangup()
            elif gather_input:
                gather = response.gather(
                    input='speech',
                    timeout=12,  # Slightly longer timeout for natural conversation
                    speech_timeout='auto',
                    action='/webhook/voice/process',
                    method='POST',
                    language='en-US',
                    hints='math, english, reading, debate, help, goodbye'  # Speech recognition hints
                )
                gather.say(clean_message, **voice_settings)
                
                fallback_msg = "I didn't catch that. Could you please repeat what you'd like to learn about? Or say goodbye to end our session."
                response.say(fallback_msg, **voice_settings)
                response.redirect('/webhook/voice/process')
            else:
                response.say(clean_message, **voice_settings)
                response.redirect('/webhook/voice/process')
                    
        except Exception as e:
            print(f"Error in voice response generation: {e}")
            gather = response.gather(
                input='speech',
                timeout=10,
                speech_timeout='auto',
                action='/webhook/voice/process',
                method='POST'
            )
            gather.say("Welcome to BAKAME learning assistant. Please say what you need help with.", voice='alice', language='en-US')
            response.say("I didn't hear anything. Please try again.", voice='alice', language='en-US')
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
