import websockets
import asyncio
import json
import base64
from typing import Dict, Any, Optional
from app.config import settings

class ElevenLabsService:
    def __init__(self):
        self.agent_id = settings.elevenlabs_agent_id
        self.websocket_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={self.agent_id}"
        self.websocket = None
        self.conversation_id = None
    
    async def open_websocket_connection(self):
        """Open a WebSocket connection to ElevenLabs ConvAI"""
        try:
            self.websocket = await websockets.connect(self.websocket_url, ping_interval=None)
            return True
        except Exception as e:
            print(f"Error opening ElevenLabs WebSocket connection: {e}")
            return False
    
    async def close_websocket_connection(self):
        """Close the WebSocket connection"""
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                print(f"Error closing ElevenLabs WebSocket connection: {e}")
            finally:
                self.websocket = None
                self.conversation_id = None
    
    async def initiate_conversation(self, user_context: Dict[str, Any]) -> bool:
        """Initiate a conversation with the ElevenLabs agent"""
        try:
            if not self.websocket:
                if not await self.open_websocket_connection():
                    return False
            
            conversation_init = {
                "type": "conversation_initiation_client_data",
                "conversation_config_override": {
                    "agent": {
                        "prompt": {
                            "prompt": f"You are BAKAME, a warm and intelligent AI learning companion who understands Rwandan culture deeply. The user's name is {user_context.get('user_name', 'friend')}. Chat naturally while being helpful and educational. Reference Rwandan traditions, values like Ubuntu and unity, and daily life when appropriate. Use Kinyarwanda greetings and phrases naturally (Muraho, Murakoze, Byiza, etc.). Be curious, encouraging, and adapt your personality to match the user's energy. Think through their questions carefully and respond like a knowledgeable Rwandan friend who genuinely cares about their learning journey."
                        }
                    }
                }
            }
            
            await self.websocket.send(json.dumps(conversation_init))
            
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "conversation_initiation_metadata":
                self.conversation_id = response_data.get("conversation_id")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error initiating ElevenLabs conversation: {e}")
            return False
    
    async def send_audio_chunk(self, audio_data: bytes) -> bool:
        """Send audio chunk to ElevenLabs agent"""
        try:
            if not self.websocket or not self.conversation_id:
                return False
            
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            audio_message = {
                "type": "user_audio_chunk",
                "chunk": audio_base64
            }
            
            await self.websocket.send(json.dumps(audio_message))
            return True
            
        except Exception as e:
            print(f"Error sending audio chunk to ElevenLabs: {e}")
            return False
    
    async def process_conversation(self, audio_data: bytes, user_context: Dict[str, Any]) -> Optional[str]:
        """Process a complete conversation turn with ElevenLabs agent"""
        try:
            if not await self.initiate_conversation(user_context):
                return None
            
            if not await self.send_audio_chunk(audio_data):
                return None
            
            response_text = ""
            audio_chunks = []
            
            while True:
                try:
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
                    response_data = json.loads(response)
                    
                    message_type = response_data.get("type")
                    
                    if message_type == "user_transcript":
                        user_transcript = response_data.get("user_transcript", {}).get("text", "")
                        print(f"User transcript: {user_transcript}")
                    
                    elif message_type == "agent_response":
                        response_text = response_data.get("agent_response", {}).get("text", "")
                        print(f"Agent response: {response_text}")
                    
                    elif message_type == "audio_event":
                        audio_event = response_data.get("audio_event", {})
                        if audio_event.get("event_id") == "audio_end":
                            break
                        
                        audio_base64 = audio_event.get("audio_base_64", "")
                        if audio_base64:
                            audio_chunks.append(base64.b64decode(audio_base64))
                    
                    elif message_type == "ping":
                        pong_message = {"type": "pong", "event_id": response_data.get("event_id")}
                        await self.websocket.send(json.dumps(pong_message))
                    
                    elif message_type == "conversation_end":
                        break
                        
                except asyncio.TimeoutError:
                    print("Timeout waiting for ElevenLabs response")
                    break
                except Exception as e:
                    print(f"Error processing ElevenLabs response: {e}")
                    break
            
            await self.close_websocket_connection()
            
            return response_text if response_text else "I'm sorry, I didn't catch that. Could you please try again?"
            
        except Exception as e:
            print(f"Error in ElevenLabs conversation processing: {e}")
            await self.close_websocket_connection()
            return None
    
    async def transcribe_audio(self, audio_data: bytes, user_context: Dict[str, Any]) -> Optional[str]:
        """Transcribe audio using ElevenLabs speech-to-text"""
        try:
            if not await self.initiate_conversation(user_context):
                return None
            
            if not await self.send_audio_chunk(audio_data):
                return None
            
            transcript = ""
            
            while True:
                try:
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=15.0)
                    response_data = json.loads(response)
                    
                    message_type = response_data.get("type")
                    
                    if message_type == "user_transcript":
                        transcript = response_data.get("user_transcript", {}).get("text", "")
                        break
                    
                    elif message_type == "ping":
                        pong_message = {"type": "pong", "event_id": response_data.get("event_id")}
                        await self.websocket.send(json.dumps(pong_message))
                        
                except asyncio.TimeoutError:
                    print("Timeout waiting for ElevenLabs transcription")
                    break
                except Exception as e:
                    print(f"Error getting ElevenLabs transcription: {e}")
                    break
            
            await self.close_websocket_connection()
            
            return transcript if transcript else None
            
        except Exception as e:
            print(f"Error in ElevenLabs transcription: {e}")
            await self.close_websocket_connection()
            return None

elevenlabs_service = ElevenLabsService()
