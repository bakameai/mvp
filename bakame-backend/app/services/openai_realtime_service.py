import asyncio
import json
import base64
import logging
from typing import Optional, Dict, Any, Callable
import websockets
from app.config import settings

logger = logging.getLogger(__name__)

class OpenAIRealtimeService:
    """
    Service to handle OpenAI Realtime API WebSocket connections for voice-to-voice conversations.
    Supports bidirectional audio streaming between Telnyx calls and OpenAI's Realtime API.
    """
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.url = "wss://api.openai.com/v1/realtime?model=gpt-realtime"
        self.ws: Optional[Any] = None
        self.is_connected = False
        
        # Audio configuration
        self.input_audio_format = "g711_ulaw"  # Compatible with Telnyx 8kHz µ-law
        self.output_audio_format = "g711_ulaw"
        
        # Event handlers
        self.on_audio_delta: Optional[Callable] = None
        self.on_transcript: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
    
    async def connect(self, instructions: str = "You are a helpful AI assistant.", voice: str = "alloy"):
        """
        Establish WebSocket connection to OpenAI Realtime API.
        
        Args:
            instructions: System instructions for the AI assistant
            voice: Voice to use (alloy, echo, shimmer, ash, ballad, coral, sage, verse)
        """
        try:
            logger.info("Connecting to OpenAI Realtime API...")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            self.ws = await websockets.connect(
                self.url,
                additional_headers=headers
            )
            
            self.is_connected = True
            logger.info("Connected to OpenAI Realtime API")
            
            # Configure the session
            await self.configure_session(instructions, voice)
            
        except Exception as e:
            logger.error(f"Error connecting to OpenAI Realtime API: {str(e)}")
            raise
    
    async def configure_session(self, instructions: str, voice: str):
        """Configure the Realtime API session with audio format and AI instructions."""
        try:
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"],
                    "instructions": instructions,
                    "voice": voice,
                    "input_audio_format": self.input_audio_format,
                    "output_audio_format": self.output_audio_format,
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 500
                    },
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "temperature": 0.8
                }
            }
            
            await self.send_event(session_config)
            logger.info(f"Session configured with voice: {voice}, audio format: {self.input_audio_format}")
            
        except Exception as e:
            logger.error(f"Error configuring session: {str(e)}")
            raise
    
    async def send_event(self, event: Dict[str, Any]):
        """Send a JSON event to the Realtime API."""
        if not self.is_connected or not self.ws:
            raise RuntimeError("Not connected to OpenAI Realtime API")
        
        try:
            await self.ws.send(json.dumps(event))
        except Exception as e:
            logger.error(f"Error sending event: {str(e)}")
            raise
    
    async def send_audio(self, audio_bytes: bytes):
        """
        Send audio chunk to OpenAI Realtime API.
        
        Args:
            audio_bytes: Raw audio bytes in g711_ulaw format
        """
        try:
            # Encode audio as base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            event = {
                "type": "input_audio_buffer.append",
                "audio": audio_base64
            }
            
            await self.send_event(event)
            
        except Exception as e:
            logger.error(f"Error sending audio: {str(e)}")
            raise
    
    async def listen_for_events(self):
        """Listen for events from OpenAI Realtime API and handle them."""
        if not self.is_connected or not self.ws:
            raise RuntimeError("Not connected to OpenAI Realtime API")
        
        try:
            async for message in self.ws:
                try:
                    event = json.loads(message)
                    await self.handle_event(event)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing event: {str(e)}")
                    continue
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("OpenAI Realtime API connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error listening for events: {str(e)}")
            raise
    
    async def handle_event(self, event: Dict[str, Any]):
        """Handle incoming events from OpenAI Realtime API."""
        event_type = event.get("type", "")
        
        try:
            if event_type == "session.created":
                logger.info("Session created successfully")
            
            elif event_type == "session.updated":
                logger.info("Session updated successfully")
            
            elif event_type == "response.output_audio.delta":
                # Audio chunk received from AI
                audio_base64 = event.get("delta", {}).get("audio", "")
                if audio_base64 and self.on_audio_delta:
                    audio_bytes = base64.b64decode(audio_base64)
                    await self.on_audio_delta(audio_bytes)
            
            elif event_type == "response.output_audio.done":
                logger.info("Audio response completed")
            
            elif event_type == "response.audio_transcript.delta":
                # Live transcript of AI response
                transcript = event.get("delta", {}).get("transcript", "")
                if transcript and self.on_transcript:
                    await self.on_transcript(transcript, "assistant")
            
            elif event_type == "conversation.item.input_audio_transcription.completed":
                # User's speech transcribed
                transcript = event.get("transcript", "")
                if transcript and self.on_transcript:
                    await self.on_transcript(transcript, "user")
            
            elif event_type == "response.done":
                logger.info("Response completed")
            
            elif event_type == "error":
                error_msg = event.get("error", {}).get("message", "Unknown error")
                logger.error(f"OpenAI Realtime API error: {error_msg}")
                if self.on_error:
                    await self.on_error(error_msg)
            
            else:
                logger.warning(f"Unhandled OpenAI event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling event {event_type}: {str(e)}")
    
    async def commit_audio_buffer(self):
        """Commit the audio buffer to trigger a response from the AI."""
        try:
            event = {
                "type": "input_audio_buffer.commit"
            }
            await self.send_event(event)
            logger.info("Audio buffer committed")
        except Exception as e:
            logger.error(f"Error committing audio buffer: {str(e)}")
            raise
    
    async def create_response(self):
        """Manually trigger a response from the AI (when VAD is disabled)."""
        try:
            event = {
                "type": "response.create"
            }
            await self.send_event(event)
            logger.info("Response creation triggered")
        except Exception as e:
            logger.error(f"Error creating response: {str(e)}")
            raise
    
    async def cancel_response(self):
        """Cancel an ongoing AI response."""
        try:
            event = {
                "type": "response.cancel"
            }
            await self.send_event(event)
            logger.info("Response cancelled")
        except Exception as e:
            logger.error(f"Error cancelling response: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close the WebSocket connection."""
        if self.ws:
            await self.ws.close()
            self.is_connected = False
            logger.info("Disconnected from OpenAI Realtime API")
    
    async def run_conversation(self, 
                              audio_input_handler: Callable,
                              audio_output_handler: Callable,
                              transcript_handler: Optional[Callable] = None,
                              error_handler: Optional[Callable] = None):
        """
        Run a complete conversation session.
        
        Args:
            audio_input_handler: Async function that provides audio input
            audio_output_handler: Async function to handle audio output
            transcript_handler: Optional function to handle transcripts
            error_handler: Optional function to handle errors
        """
        self.on_audio_delta = audio_output_handler
        self.on_transcript = transcript_handler
        self.on_error = error_handler
        
        # Start listening for events in the background
        listen_task = asyncio.create_task(self.listen_for_events())
        
        # Run the audio input handler
        try:
            await audio_input_handler()
        except Exception as e:
            logger.error(f"Error in audio input handler: {str(e)}")
        finally:
            # Cleanup
            listen_task.cancel()
            await self.disconnect()
