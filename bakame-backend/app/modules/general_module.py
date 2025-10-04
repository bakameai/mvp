from typing import Dict, Any
from app.services.openai_service import openai_service

class GeneralModule:
    def __init__(self):
        self.module_name = "general"
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process general questions and conversations"""
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["help", "what can you do", "options", "menu"]):
            return self._get_help_message()
        
        messages = [{"role": "user", "content": user_input}]
        response = await openai_service.generate_response(messages, self.module_name)
        
        return response
    
    def _get_help_message(self) -> str:
        """Get help message for general assistance"""
        return "I'm BAKAME, your AI learning assistant! I can help you with any questions about English, Math, Reading, Science, or any other topic. Just ask me anything you'd like to learn about!"
    
    def get_welcome_message(self) -> str:
        """Get welcome message"""
        return "Hello! I'm BAKAME, your AI learning assistant. What would you like to learn about today?"

general_module = GeneralModule()
