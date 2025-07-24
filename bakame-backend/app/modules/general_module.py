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
            return "Awesome! 🌟 Let's dive into English together! I'm so excited to help you with grammar, pronunciation, or just have a great conversation to build your confidence. English is such a beautiful language - what aspect would you like to explore?"
        
        elif "math" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "math"
            return "Yes! 🧮✨ Time for some fun with numbers! I love helping people discover how satisfying math can be. We'll start easy and work our way up as you get stronger. Ready to flex those mental muscles?"
        
        elif "comprehension" in user_input_lower or "reading" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "comprehension"
            return "Oh wonderful! 📚✨ I absolutely love sharing stories and exploring them together! Stories are like little adventures waiting to unfold. Ready to dive into a tale and see what catches your imagination?"
        
        elif "debate" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "debate"
            return "Ooh, I love this! 🤔💭 Ready for some friendly intellectual sparring? I'm excited to explore different perspectives with you and really dig into some fascinating topics. Let's get those mental gears turning!"
        
        messages = [{"role": "user", "content": user_input}]
        
        for interaction in user_context.get("conversation_history", [])[-5:]:
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
        return "Hey there! I'm BAKAME, your friendly AI learning companion! 😊 I'm here to chat and help you learn in whatever way feels right for you. Whether you want to practice English, tackle some math, dive into stories, or have a good debate - I'm excited to explore together! What sounds interesting to you today?"

general_module = GeneralModule()
