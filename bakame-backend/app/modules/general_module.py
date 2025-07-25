from typing import Dict, Any
from app.services.openai_service import openai_service
from app.services.llama_service import llama_service
from app.config import settings

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
            return "Muraho! 🌟 Let's dive into English together! I'm excited to help you with grammar, pronunciation, or just have a great conversation. English opens many doors in Rwanda and beyond - what aspect would you like to explore?"
        
        elif "math" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "math"
            return "Yego! 🧮✨ Time for some fun with numbers! Math is everywhere in Rwanda - from calculating Rwandan francs to measuring land. We'll start easy and work our way up. Ready to strengthen those mental muscles?"
        
        elif "comprehension" in user_input_lower or "reading" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "comprehension"
            return "Byiza cyane! 📚✨ I love sharing stories that reflect our beautiful Rwandan culture and beyond! Stories teach us about life, values, and wisdom. Ready to explore some tales together?"
        
        elif "debate" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "debate"
            return "Ni byiza! 🤔💭 Ready for some thoughtful discussion? In Rwanda, we value respectful dialogue and Ubuntu - let's explore different perspectives together and strengthen our critical thinking!"
        
        messages = [{"role": "user", "content": user_input}]
        
        for interaction in user_context.get("conversation_history", [])[-5:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        if settings.use_llama:
            response = await llama_service.generate_response(messages, self.module_name)
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        
        if len(user_context.get("conversation_history", [])) % 3 == 0:
            response += "\n\nMurabona, I can also help you with English, Math, Reading Comprehension, or Debate practice. Just say what you'd like to try!"
        
        return response
    
    def _get_help_message(self) -> str:
        """Get help message explaining available modules"""
        return """Muraho! I'm BAKAME, your AI learning companion for Rwanda! Here's what I can help you with:

📚 ENGLISH - Grammar, pronunciation, and conversation practice
🔢 MATH - Mental arithmetic with Rwandan contexts and examples
📖 COMPREHENSION - Stories reflecting Rwandan culture and values
🗣️ DEBATE - Thoughtful discussions on topics relevant to Rwanda
❓ GENERAL - Ask me anything! I'm here to support your learning journey

Just say what you'd like to try, like "English" or "Math". Ni iki gikureba uyu munsi? (What interests you today?)"""
    
    def get_welcome_message(self) -> str:
        """Get welcome message for General module"""
        return "Muraho! I'm BAKAME, your friendly AI learning companion for Rwanda! 😊 I'm here to chat and help you learn in whatever way feels right for you. Whether you want to practice English, tackle some math with Rwandan examples, explore stories, or have thoughtful debates - I'm excited to learn together! Ni iki gikureba uyu munsi? (What interests you today?)"

general_module = GeneralModule()
