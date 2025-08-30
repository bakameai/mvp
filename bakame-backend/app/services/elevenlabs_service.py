import aiohttp
import asyncio
from typing import Optional, Dict, Any
from app.config import settings

class ElevenLabsService:
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.agent_id = "bakame"
        
    async def create_conversation(self, phone_number: str, user_context: Dict[str, Any]) -> str:
        """Create new conversation with ElevenLabs agent"""
        try:
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "agent_id": self.agent_id,
                "user_id": phone_number,
                "context": {
                    "user_name": user_context.get("user_name", "friend"),
                    "current_module": user_context.get("current_module", "general"),
                    "curriculum_stage": user_context.get("curriculum_stage", "remember"),
                    "phone_number": phone_number
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/convai/conversations",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("conversation_id")
                    else:
                        print(f"ElevenLabs conversation creation failed: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error creating ElevenLabs conversation: {e}")
            return None
    
    async def send_message(self, conversation_id: str, message: str) -> Optional[str]:
        """Send message to ElevenLabs conversation and get response"""
        try:
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": message,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/convai/conversations/{conversation_id}/message",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("audio_url") or data.get("text")
                    else:
                        print(f"ElevenLabs message failed: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error sending message to ElevenLabs: {e}")
            return None

elevenlabs_service = ElevenLabsService()
