import openai
from typing import List, Dict, Any
from app.config import settings

openai.api_key = settings.openai_api_key

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    
    async def generate_response(self, messages: List[Dict[str, str]], module_name: str = "general") -> str:
        """Generate response using GPT-3.5"""
        try:
            system_prompts = {
                "general": "You are BAKAME, a helpful and conversational AI learning assistant. Engage naturally with students, answer their questions thoughtfully, and provide educational support across all subjects. Respond naturally to any topic they ask about. Keep responses concise for voice/SMS delivery while being warm and encouraging. Be like ChatGPT but focused on education."
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
