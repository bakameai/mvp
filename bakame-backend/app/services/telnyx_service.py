import telnyx
import requests
import json
import logging
import asyncio
import urllib.parse
from typing import Optional, Dict, Any
from functools import partial
from app.config import settings

logger = logging.getLogger(__name__)

class TelnyxService:
    """
    Service to handle Telnyx Call Control API interactions.
    Replaces TwilioService's TwiML-based approach with JSON-based commands.
    """
    
    def __init__(self):
        # Set up Telnyx API key
        telnyx.api_key = settings.telnyx_api_key
        self.api_url = settings.telnyx_api_url
        self.phone_number = settings.telnyx_phone_number
        
        # Headers for direct API calls
        self.headers = {
            "Authorization": f"Bearer {settings.telnyx_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def handle_incoming_call(self, webhook_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Handle incoming call webhook from Telnyx
        
        Returns a status response for Telnyx
        """
        try:
            # Log the incoming webhook
            logger.info(f"Incoming call webhook: {json.dumps(webhook_data, indent=2)}")
            
            # Extract event data
            event_type = webhook_data.get("data", {}).get("event_type")
            call_control_id = webhook_data.get("data", {}).get("payload", {}).get("call_control_id")
            call_session_id = webhook_data.get("data", {}).get("payload", {}).get("call_session_id")
            from_number = webhook_data.get("data", {}).get("payload", {}).get("from")
            
            logger.info(f"Event: {event_type}, Call Control ID: {call_control_id}, From: {from_number}")
            
            # Return 200 OK to acknowledge webhook
            return {"status": "ok", "message": "Webhook received"}
            
        except Exception as e:
            logger.error(f"Error handling incoming call: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def speak(self, call_control_id: str, text: str, voice: str = "male", language: str = "en-US") -> Dict[str, Any]:
        """
        Send speak command to Telnyx Call Control API
        Equivalent to Twilio's <Say> verb
        
        Args:
            call_control_id: The unique identifier for the call
            text: Text to speak
            voice: Voice to use (male/female)
            language: Language code (e.g., 'en-US')
        """
        try:
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/speak"
            
            payload = {
                "payload": text,
                "voice": voice,
                "language": language,
                "payload_type": "text"
            }
            
            logger.info(f"Sending speak command: {payload}")
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(requests.post, url, json=payload, headers=self.headers)
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Speak command response: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending speak command: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def gather(self, call_control_id: str, prompt_text: str, 
                    timeout_millis: int = 60000, 
                    inter_digit_timeout_millis: int = 5000,
                    maximum_digits: int = 128,
                    terminating_digit: str = "#",
                    valid_digits: str = "0123456789*#") -> Dict[str, Any]:
        """
        Send gather command to collect DTMF or speech input
        Equivalent to Twilio's <Gather> verb
        
        Args:
            call_control_id: The unique identifier for the call
            prompt_text: Text to speak before gathering input
            timeout_millis: Overall timeout for gathering input (in milliseconds)
            inter_digit_timeout_millis: Timeout between digits
            maximum_digits: Maximum number of digits to collect
            terminating_digit: Digit that ends gathering
            valid_digits: Valid digits to accept
        """
        try:
            # First, speak the prompt
            await self.speak(call_control_id, prompt_text)
            
            # Then send gather command
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/gather"
            
            payload = {
                "timeout_millis": timeout_millis,
                "inter_digit_timeout_millis": inter_digit_timeout_millis,
                "maximum_digits": maximum_digits,
                "terminating_digit": terminating_digit,
                "valid_digits": valid_digits
            }
            
            logger.info(f"Sending gather command: {payload}")
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Gather command response: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending gather command: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def gather_using_speak(self, call_control_id: str, prompt_text: str,
                                 timeout_millis: int = 60000,
                                 voice: str = "male",
                                 language: str = "en-US") -> Dict[str, Any]:
        """
        Combined gather with speak - more similar to Twilio's approach
        This uses the gather_using_speak endpoint which combines both actions
        """
        try:
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/gather_using_speak"
            
            payload = {
                "payload": prompt_text,
                "voice": voice,
                "language": language,
                "payload_type": "text",
                "timeout_millis": timeout_millis,
                "inter_digit_timeout_millis": 5000,
                "maximum_digits": 128,
                "terminating_digit": "#",
                "valid_digits": "0123456789*#"
            }
            
            logger.info(f"Sending gather_using_speak command: {payload}")
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Gather using speak command response: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending gather_using_speak command: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def answer_call(self, call_control_id: str) -> Dict[str, Any]:
        """
        Answer an incoming call
        """
        try:
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/answer"
            
            logger.info(f"Answering call: {call_control_id}")
            
            response = requests.post(url, json={}, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Answer call response: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error answering call: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def hangup(self, call_control_id: str) -> Dict[str, Any]:
        """
        Hang up a call
        Equivalent to Twilio's <Hangup> verb
        """
        try:
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/hangup"
            
            logger.info(f"Hanging up call: {call_control_id}")
            
            response = requests.post(url, json={}, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Hangup response: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error hanging up call: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def transfer(self, call_control_id: str, to: str) -> Dict[str, Any]:
        """
        Transfer a call to another number
        """
        try:
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/transfer"
            
            payload = {
                "to": to
            }
            
            logger.info(f"Transferring call to: {to}")
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Transfer response: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error transferring call: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def start_streaming(self, call_control_id: str, stream_url: str,
                             track: str = "both_tracks",
                             codec: str = "PCMU") -> Dict[str, Any]:
        """
        Start media streaming for a call to enable real-time audio processing.
        
        Args:
            call_control_id: The unique identifier for the call
            stream_url: WebSocket URL where audio will be streamed (e.g., wss://yourserver.com/stream)
            track: Which audio to stream - 'inbound_track', 'outbound_track', or 'both_tracks'
            codec: Audio codec - 'PCMU' (G.711 µ-law), 'PCMA', 'OPUS', 'L16', etc. (case-sensitive!)
        """
        try:
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/streaming_start"
            
            payload = {
                "stream_url": stream_url,
                "stream_track": track,
                "stream_bidirectional_mode": "rtp",
                "stream_bidirectional_codec": codec
            }
            
            logger.info(f"Starting media stream to {stream_url} with codec {codec}")
            logger.info(f"Streaming payload: {payload}")
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Streaming started: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error starting streaming: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def stop_streaming(self, call_control_id: str) -> Dict[str, Any]:
        """
        Stop media streaming for a call.
        """
        try:
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/streaming_stop"
            
            logger.info(f"Stopping media stream for call: {call_control_id}")
            
            response = requests.post(url, json={}, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Streaming stopped: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error stopping streaming: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def start_recording(self, call_control_id: str, format: str = "wav", channels: str = "single", max_length: int = 120) -> Dict[str, Any]:
        """
        Start recording the call audio.
        
        Args:
            call_control_id: The unique identifier for the call
            format: Recording format (wav, mp3)
            channels: Recording channels (single or dual)
            max_length: Maximum recording length in seconds
        """
        try:
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/record_start"
            
            payload = {
                "format": format,
                "channels": channels,
                "max_length": max_length
            }
            
            logger.info(f"Starting recording for call: {call_control_id}")
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(requests.post, url, json=payload, headers=self.headers)
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Recording started: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error starting recording: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    async def stop_recording(self, call_control_id: str) -> Dict[str, Any]:
        """
        Stop recording the call audio.
        """
        try:
            encoded_id = urllib.parse.quote(call_control_id, safe='')
            url = f"{self.api_url}/calls/{encoded_id}/actions/record_stop"
            
            logger.info(f"Stopping recording for call: {call_control_id}")
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(requests.post, url, json={}, headers=self.headers)
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Recording stopped: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error stopping recording: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Telnyx webhook signature for security
        """
        try:
            if not settings.telnyx_public_key:
                logger.warning("Telnyx public key not configured, skipping signature verification")
                return True
            
            # Implement signature verification using Telnyx public key
            # This is a placeholder - actual implementation depends on Telnyx's signature method
            # Typically involves checking HMAC or similar cryptographic signature
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False

# Create a singleton instance
telnyx_service = TelnyxService()