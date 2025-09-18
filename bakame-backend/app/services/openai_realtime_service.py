import asyncio
import json
import base64
import websockets
from typing import Optional, Dict, Any, AsyncGenerator
from app.config import settings
from app.services.redis_service import redis_service

class OpenAIRealtimeService:
    def __init__(self):
        self.ws: Optional[websockets.WebSocketServerProtocol] = None
        self.session_id: Optional[str] = None
        self.phone_number: Optional[str] = None
        self.current_module: str = "general"
        
    async def connect(self) -> bool:
        """Connect to OpenAI Realtime API"""
        try:
            url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
            headers = [
                ("Authorization", f"Bearer {settings.openai_api_key}"),
                ("OpenAI-Beta", "realtime=v1")
            ]
            
            self.ws = await websockets.connect(url, additional_headers=headers)
            print("[OpenAI Realtime] Connected successfully", flush=True)
            return True
        except Exception as e:
            print(f"[OpenAI Realtime] Connection failed: {e}", flush=True)
            return False
    
    async def configure_session(self, phone_number: str):
        """Configure session with BAKAME educational context"""
        self.phone_number = phone_number
        
        user_context = redis_service.get_user_context(phone_number)
        self.current_module = redis_service.get_current_module(phone_number) or "general"
        
        system_prompts = {
            "english": "You're a friendly, encouraging English conversation partner who understands Rwandan culture deeply. Help with grammar, pronunciation, and vocabulary while being culturally sensitive. Use examples from Rwandan daily life, incorporate Kinyarwanda phrases when helpful (like 'Muraho' for hello, 'Murakoze' for thank you), and adapt your tone to the user's mood. Reference Rwanda's beautiful hills, community values of Ubuntu, and local contexts. Think step-by-step about their needs and respond conversationally.",
            
            "comprehension": "You're an engaging storyteller who loves Rwandan culture and traditions. Share tales that reflect Rwandan values like Ubuntu, unity, and community support. Reference Rwanda's history of resilience, beautiful landscapes from Kigali to Volcanoes National Park, and daily life. Ask thoughtful questions that spark curiosity about both stories and Rwandan heritage. Use Kinyarwanda phrases naturally and be encouraging. Think through their understanding and respond like a supportive Rwandan elder sharing wisdom.",
            
            "math": "You're an enthusiastic math mentor who makes numbers fun using Rwandan contexts. Use examples with Rwandan francs (RWF), local measurements, and familiar scenarios from Rwandan life - like calculating distances between Kigali and Butare, or market transactions. Reference Rwanda's progress in technology and education. Explain concepts conversationally, celebrate successes with phrases like 'Byiza cyane!' (very good), and provide gentle encouragement. Think through problems step-by-step using culturally relevant examples.",
            
            "debate": "You're a thoughtful discussion partner who understands Rwandan society and values deeply. Engage in respectful debates that consider Rwandan perspectives, history, and current challenges like development goals and regional integration. Be curious about their viewpoints while incorporating understanding of Rwandan culture, Ubuntu philosophy, and community values. Reference Rwanda's journey of unity and reconciliation. Keep discussions engaging and intellectually stimulating while being culturally sensitive.",
            
            "general": "You're BAKAME, a warm and intelligent AI learning companion who understands Rwandan culture deeply. Chat naturally while being helpful and educational. Reference Rwandan traditions, values like Ubuntu and unity, and daily life when appropriate. Use Kinyarwanda greetings and phrases naturally (Muraho, Murakoze, Byiza, etc.). Be curious, encouraging, and adapt your personality to match the user's energy. Think through their questions carefully and respond like a knowledgeable Rwandan friend who genuinely cares about their learning journey."
        }
        
        instructions = system_prompts.get(self.current_module, system_prompts["general"])
        
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": instructions,
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {"type": "server_vad", "threshold": 0.5, "prefix_padding_ms": 300, "silence_duration_ms": 500},
                "tools": [],
                "tool_choice": "auto",
                "temperature": 0.8,
                "max_response_output_tokens": 4096
            }
        }
        
        await self.ws.send(json.dumps(session_config))
        print(f"[OpenAI Realtime] Session configured for {self.current_module} module", flush=True)
    
    async def send_audio(self, audio_data: bytes):
        """Send audio data to OpenAI Realtime API"""
        if not self.ws:
            return
            
        try:
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            message = {
                "type": "input_audio_buffer.append",
                "audio": audio_b64
            }
            
            await self.ws.send(json.dumps(message))
        except Exception as e:
            print(f"[OpenAI Realtime] Error sending audio: {e}", flush=True)
    
    async def commit_audio_buffer(self):
        """Commit the audio buffer to trigger processing"""
        if not self.ws:
            return
            
        try:
            message = {
                "type": "input_audio_buffer.commit"
            }
            
            await self.ws.send(json.dumps(message))
        except Exception as e:
            print(f"[OpenAI Realtime] Error committing audio buffer: {e}", flush=True)
    
    async def listen_for_responses(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Listen for responses from OpenAI Realtime API"""
        if not self.ws:
            return
            
        try:
            async for message in self.ws:
                data = json.loads(message)
                yield data
        except Exception as e:
            print(f"[OpenAI Realtime] Error receiving response: {e}", flush=True)
    
    async def close(self):
        """Close the WebSocket connection"""
        if self.ws:
            await self.ws.close()
            self.ws = None
            print("[OpenAI Realtime] Connection closed", flush=True)

openai_realtime_service = OpenAIRealtimeService()
