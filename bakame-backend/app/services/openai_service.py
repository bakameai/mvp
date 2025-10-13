import openai
import os
from typing import Dict, Any

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAIAPI")
        if not api_key:
            raise ValueError("OPENAIAPI environment variable not set")
        self.client = openai.OpenAI(api_key=api_key)
        print(f"[OpenAI] Initialized with key: {api_key[:20]}...")
    
    async def generate_response(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Generate response using GPT-4 - completely fresh each time, no history"""
        try:
            # Fresh call every time - no conversation history
            messages = [
                {
                    "role": "system", 
                    "content": "You are an English teacher helping someone learn English through natural conversation. Correct mistakes gently and keep the conversation engaging."
                },
                {"role": "user", "content": user_input}
            ]
            
            print(f"[OpenAI] Making fresh API call")
            print(f"[OpenAI] User input: {user_input}")
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300,
                temperature=0.9
            )
            
            result = response.choices[0].message.content.strip()
            print(f"[OpenAI] API Response received: {result[:100]}...")
            
            return result
            
        except Exception as e:
            print(f"[OpenAI] ERROR calling API: {e}")
            return f"Error: {str(e)}"

openai_service = OpenAIService()