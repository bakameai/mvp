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
        """Generate response using GPT-4 with conversational intelligence"""
        try:
            system_prompts = {
                "english": "You're a friendly, encouraging English conversation partner who happens to be great at teaching. Chat naturally while helping with grammar, pronunciation, and vocabulary. Be warm, supportive, and adapt your tone to the user's mood. Think step-by-step about their needs and respond conversationally.",
                "comprehension": "You're an engaging storyteller and reading buddy who loves discussing stories. Share tales naturally and ask thoughtful questions that spark curiosity. Be encouraging and adapt to how the user is feeling. Think through their understanding and respond like a supportive friend.",
                "math": "You're an enthusiastic math mentor who makes numbers fun and accessible. Explain concepts conversationally, celebrate successes, and provide gentle encouragement when things get tough. Think through problems step-by-step and share your reasoning naturally.",
                "debate": "You're a thoughtful discussion partner who loves exploring different perspectives. Engage in friendly, respectful debates that challenge thinking while being supportive. Be curious about their viewpoints and think through arguments together. Keep the conversation engaging and intellectually stimulating.",
                "general": "You're BAKAME, a warm and intelligent AI learning companion. Chat naturally while being helpful and educational. Be curious, encouraging, and adapt your personality to match the user's energy. Think through their questions carefully and respond like a knowledgeable friend who genuinely cares about their learning journey."
            }
            
            system_prompt = system_prompts.get(module_name, system_prompts["general"])
            
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages,
                max_tokens=300,
                temperature=0.8,
                top_p=0.9,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again."

openai_service = OpenAIService()
