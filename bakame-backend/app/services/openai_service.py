import openai
from typing import List, Dict, Any
import io
from app.config import settings

openai.api_key = settings.openai_api_key

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav") -> str:
        """Transcribe audio using OpenAI Whisper"""
        try:
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"
            
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            
            return transcript.strip()
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""
    
    async def generate_response(self, messages: List[Dict[str, str]], module_name: str = "general") -> str:
        """Generate response using GPT-3.5"""
        try:
            system_prompts = {
                "english": "You are an English tutor helping students improve their grammar, pronunciation, and vocabulary. Provide clear corrections and explanations. Keep responses concise for voice/SMS delivery.",
                "comprehension": "You are a reading comprehension tutor. Present short stories and ask questions to test understanding. Provide feedback on answers. Keep content appropriate for all ages.",
                "math": "You are a mental math tutor. Generate arithmetic problems and provide step-by-step solutions. Encourage students and track their progress. Keep explanations simple.",
                "debate": "You are a debate coach. Present opinion-based topics and challenge students' reasoning. Encourage critical thinking while being respectful. Keep exchanges engaging.",
                "general": "You are BAKAME, a helpful and conversational AI learning assistant. Engage naturally with students, answer their questions thoughtfully, and provide educational support across all subjects. You can help with English, Math, Reading Comprehension, and Debate, but respond naturally to any topic. Keep responses concise for voice/SMS delivery while being warm and encouraging."
            }
            
            system_prompt = system_prompts.get(module_name, system_prompts["general"])
            
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=full_messages,
                max_tokens=150,  # Keep responses concise for voice/SMS
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again."

openai_service = OpenAIService()
