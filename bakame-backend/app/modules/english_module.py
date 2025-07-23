from typing import Dict, Any
from app.services.openai_service import openai_service

class EnglishModule:
    def __init__(self):
        self.module_name = "english"
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process English learning input"""
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["grammar", "correct", "fix"]):
            return await self._grammar_correction(user_input, user_context)
        elif any(word in user_input_lower for word in ["repeat", "practice", "pronunciation"]):
            return await self._repeat_practice(user_input, user_context)
        elif any(word in user_input_lower for word in ["help", "learn", "teach"]):
            return await self._english_tutoring(user_input, user_context)
        else:
            return await self._english_tutoring(user_input, user_context)
    
    async def _grammar_correction(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Provide grammar correction and feedback"""
        messages = [
            {"role": "user", "content": f"Please correct any grammar mistakes in this sentence and explain the corrections: '{user_input}'"}
        ]
        
        for interaction in user_context.get("conversation_history", [])[-3:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        response = await openai_service.generate_response(messages, self.module_name)
        return response
    
    async def _repeat_practice(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Provide pronunciation and repetition practice"""
        messages = [
            {"role": "user", "content": f"Help me practice pronunciation. Give me feedback on how I said: '{user_input}' and provide a similar sentence to practice."}
        ]
        
        response = await openai_service.generate_response(messages, self.module_name)
        return response
    
    async def _english_tutoring(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """General English tutoring and conversation"""
        messages = [
            {"role": "user", "content": user_input}
        ]
        
        for interaction in user_context.get("conversation_history", [])[-3:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        response = await openai_service.generate_response(messages, self.module_name)
        return response
    
    def get_welcome_message(self) -> str:
        """Get welcome message for English module"""
        return "Welcome to English learning! I can help you with grammar correction, pronunciation practice, and general English conversation. What would you like to work on today?"

english_module = EnglishModule()
