import openai
from typing import Dict, Any
from app.config import settings

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def generate_response(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Generate response using GPT-4 for natural English conversation teaching"""
        try:
            # Build conversation history from context
            messages = [
                {
                    "role": "system", 
                    "content": """You are an English teacher having a natural conversation to help someone learn English. 
                    Your goal is to teach English through conversation - correct mistakes gently, suggest better ways to express ideas, 
                    and keep the conversation flowing naturally. Be encouraging and supportive. 
                    Focus on practical, everyday English. Keep responses conversational and engaging.
                    Do not mention modules, lessons, or structured curriculum - just have a natural teaching conversation."""
                }
            ]
            
            # Add conversation history if available (last 5 exchanges for context)
            conversation_history = user_context.get("conversation_history", [])
            for interaction in conversation_history[-5:]:
                if "user" in interaction:
                    messages.append({"role": "user", "content": interaction["user"]})
                if "ai" in interaction:
                    messages.append({"role": "assistant", "content": interaction["ai"]})
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            print(f"[OpenAI] Calling GPT-4o-mini for English conversation")
            print(f"[OpenAI] User said: {user_input}")
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300,
                temperature=0.9,  # Natural conversation temperature
                top_p=0.95,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            result = response.choices[0].message.content.strip()
            print(f"[OpenAI] Response: {result[:100]}...")
            
            # Store this interaction in conversation history
            if "conversation_history" not in user_context:
                user_context["conversation_history"] = []
            user_context["conversation_history"].append({
                "user": user_input,
                "ai": result
            })
            
            return result
            
        except Exception as e:
            print(f"[OpenAI] Error generating response: {e}")
            return "I'm having trouble understanding. Could you try saying that again?"

openai_service = OpenAIService()