import openai
import os
from typing import Dict, Any

class OpenAIService:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAIAPI", "")
        
        if not api_key:
            print("[OpenAI] Warning: OPENAIAPI not set - service disabled")
            self.client = None
            self.enabled = False
        else:
            self.client = openai.OpenAI(api_key=api_key)
            self.enabled = True
            print(f"[OpenAI] Initialized with key: {api_key[:20]}...")
    
    async def generate_response(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Generate response using GPT-4 - completely fresh each time, no history"""
        if not self.enabled or self.client is None:
            return "OpenAI service is not configured. Please set OPENAIAPI environment variable."
        
        try:
            # Fresh call every time - no conversation history
            messages = [
                {
                    "role": "system", 
                    "content": "You are an English teacher helping someone learn English through natural conversation. Start fresh with each interaction. Correct mistakes gently and keep the conversation engaging. Do not reference any previous calls or conversations."
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

# Module-level instance - safe to import even if OPENAIAPI is not set
# Service will be disabled but won't crash the app
openai_service = OpenAIService()