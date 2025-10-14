import asyncio
import json
import base64
import logging
from typing import Dict, Any, Optional
from fastapi import WebSocket
from app.services.openai_realtime_service import OpenAIRealtimeService
from app.services.telnyx_service import telnyx_service

logger = logging.getLogger(__name__)

class VoiceBridgeService:
    """
    Bridge service that connects Telnyx media streams to OpenAI Realtime API.
    Handles bidirectional audio streaming between phone calls and AI.
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def start_session(self, call_control_id: str, telnyx_ws: WebSocket):
        """
        Start a voice AI session for a phone call.
        
        Args:
            call_control_id: Telnyx call control ID
            telnyx_ws: WebSocket connection from Telnyx media stream
        """
        try:
            logger.info(f"Starting voice AI session for call: {call_control_id}")
            
            # Create OpenAI Realtime service instance
            openai_service = OpenAIRealtimeService()
            
            # Connect to OpenAI Realtime API
            await openai_service.connect(
                instructions="You are a helpful AI assistant. Have natural, friendly conversations with callers.",
                voice="alloy"
            )
            
            # Store session info
            self.active_sessions[call_control_id] = {
                "openai_service": openai_service,
                "telnyx_ws": telnyx_ws,
                "stream_id": None
            }
            
            # Set up audio handlers
            openai_service.on_audio_delta = lambda audio: self.send_audio_to_telnyx(
                call_control_id, audio
            )
            openai_service.on_transcript = lambda text, role: self.log_transcript(
                call_control_id, text, role
            )
            
            # Start listening tasks
            await asyncio.gather(
                self.listen_to_telnyx(call_control_id, telnyx_ws),
                openai_service.listen_for_events()
            )
            
        except Exception as e:
            logger.error(f"Error starting voice session: {str(e)}")
            await self.end_session(call_control_id)
            raise
    
    async def listen_to_telnyx(self, call_control_id: str, websocket: WebSocket):
        """Listen for audio and events from Telnyx media stream."""
        try:
            while True:
                data = await websocket.receive_text()
                event = json.loads(data)
                
                await self.handle_telnyx_event(call_control_id, event)
                
        except Exception as e:
            logger.error(f"Error listening to Telnyx: {str(e)}")
            await self.end_session(call_control_id)
    
    async def handle_telnyx_event(self, call_control_id: str, event: Dict[str, Any]):
        """Handle events from Telnyx media stream."""
        event_type = event.get("event")
        
        try:
            session = self.active_sessions.get(call_control_id)
            if not session:
                logger.warning(f"No active session for call: {call_control_id}")
                return
            
            if event_type == "start":
                # Stream started
                stream_id = event.get("stream_id")
                session["stream_id"] = stream_id
                logger.info(f"Telnyx stream started: {stream_id}")
                
                # Log media format
                media_format = event.get("start", {}).get("media_format", {})
                logger.info(f"Media format: {media_format}")
            
            elif event_type == "media":
                # Audio chunk received from Telnyx
                payload = event.get("media", {}).get("payload", "")
                if payload:
                    # Decode base64 audio
                    audio_bytes = base64.b64decode(payload)
                    
                    # Forward to OpenAI
                    openai_service = session["openai_service"]
                    await openai_service.send_audio(audio_bytes)
            
            elif event_type == "stop":
                # Stream ended
                logger.info(f"Telnyx stream stopped for call: {call_control_id}")
                await self.end_session(call_control_id)
            
            elif event_type == "dtmf":
                # DTMF (button press) detected
                digit = event.get("dtmf", {}).get("digit", "")
                logger.info(f"DTMF detected: {digit}")
            
            elif event_type == "error":
                # Error from Telnyx
                error_msg = event.get("payload", {}).get("detail", "Unknown error")
                logger.error(f"Telnyx stream error: {error_msg}")
                await self.end_session(call_control_id)
            
            else:
                logger.debug(f"Unhandled Telnyx event: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling Telnyx event: {str(e)}")
    
    async def send_audio_to_telnyx(self, call_control_id: str, audio_bytes: bytes):
        """Send audio response from OpenAI back to Telnyx."""
        try:
            session = self.active_sessions.get(call_control_id)
            if not session:
                return
            
            telnyx_ws = session["telnyx_ws"]
            
            # Encode audio as base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Send to Telnyx in their expected format
            message = {
                "event": "media",
                "media": {
                    "payload": audio_base64
                }
            }
            
            await telnyx_ws.send_text(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Error sending audio to Telnyx: {str(e)}")
    
    async def log_transcript(self, call_control_id: str, text: str, role: str):
        """Log transcripts from the conversation."""
        logger.info(f"[{call_control_id}] {role.upper()}: {text}")
    
    async def end_session(self, call_control_id: str):
        """End a voice AI session and cleanup."""
        try:
            session = self.active_sessions.get(call_control_id)
            if not session:
                return
            
            logger.info(f"Ending voice session for call: {call_control_id}")
            
            # Disconnect OpenAI
            openai_service = session["openai_service"]
            await openai_service.disconnect()
            
            # Remove session
            del self.active_sessions[call_control_id]
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
    
    async def clear_audio_queue(self, call_control_id: str):
        """Clear all queued audio in Telnyx (stop playback)."""
        try:
            session = self.active_sessions.get(call_control_id)
            if not session:
                return
            
            telnyx_ws = session["telnyx_ws"]
            
            clear_message = {
                "event": "clear"
            }
            
            await telnyx_ws.send_text(json.dumps(clear_message))
            logger.info(f"Cleared audio queue for call: {call_control_id}")
            
        except Exception as e:
            logger.error(f"Error clearing audio queue: {str(e)}")

# Create singleton instance
voice_bridge_service = VoiceBridgeService()
