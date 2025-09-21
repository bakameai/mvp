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
        
        if "english" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "english"
            return "Switching to English learning! I can help you with grammar correction, pronunciation practice, and general English conversation. What would you like to work on?"
        
        elif "math" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "math"
            return "Switching to Mental Math! I'll give you arithmetic problems to solve. Say 'new problem' to get started!"
        
        elif "comprehension" in user_input_lower or "reading" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "comprehension"
            return "Switching to Reading Comprehension! I'll share short stories with you and then ask questions. Say 'new story' to begin!"
        
        elif "debate" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "debate"
            return "Switching to Debate Practice! I'll present interesting topics and challenge your thinking. Ready for a topic?"
        
        messages = [{"role": "user", "content": user_input}]
        
        for interaction in user_context.get("conversation_history", [])[-3:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        response = await openai_service.generate_response(messages, self.module_name)
        
        if len(user_context.get("conversation_history", [])) % 3 == 0:
            response += "\n\nBy the way, I can also help you with English, Math, Reading Comprehension, or Debate practice. Just say the name of what you'd like to try!"
        
        return response
    
    def _get_help_message(self) -> str:
        """Get help message explaining available modules"""
        return """I'm BAKAME, your AI learning assistant! Here's what I can help you with:

📚 ENGLISH - Grammar correction, pronunciation practice, and conversation
🔢 MATH - Mental arithmetic problems and step-by-step solutions  
📖 COMPREHENSION - Short stories with questions to test understanding
🗣️ DEBATE - Opinion topics to develop critical thinking skills
❓ GENERAL - Ask me anything! I'm here to help with learning

Just say the name of what you'd like to try, like "English" or "Math". What interests you today?"""
    
    def get_welcome_message(self) -> str:
        """Get welcome message for General module"""
        return "Hello! I'm BAKAME, your AI learning assistant. I can help you with English, Math, Reading Comprehension, Debate practice, or answer any questions you have. What would you like to learn about today?"

general_module = GeneralModule()
