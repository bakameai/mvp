from typing import Dict, Any
from app.services.openai_service import openai_service

class GeneralModule:
    def __init__(self):
        self.module_name = "general"
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process general questions and conversations"""
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["help", "what can you do", "modules", "options", "menu"]):
            return self._get_help_message()
        
        
        messages = [{"role": "user", "content": user_input}]
        
        for interaction in user_context.get("conversation_history", [])[-3:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        response = await openai_service.generate_response(messages, self.module_name)
        
        if len(user_context.get("conversation_history", [])) % 5 == 0:
            response += "\n\nI can also help with specific subjects like English, Math, Reading, or Debate if you're interested!"
        
        return response
    
    def _get_help_message(self) -> str:
        """Get help message explaining available modules"""
        return """I'm BAKAME, your AI learning assistant! Here's what I can help you with:

ENGLISH - Grammar correction, pronunciation practice, and conversation
MATH - Mental arithmetic problems and step-by-step solutions  
COMPREHENSION - Short stories with questions to test understanding
DEBATE - Opinion topics to develop critical thinking skills
GENERAL - Ask me anything! I'm here to help with learning

Just say the name of what you'd like to try, like "English" or "Math". What interests you today?"""
    
    def get_welcome_message(self) -> str:
        """Get welcome message for General module"""
        return "Hello! I'm BAKAME, your AI learning assistant. I can help you with English, Math, Reading Comprehension, Debate practice, or answer any questions you have. What would you like to learn about today?"

general_module = GeneralModule()
