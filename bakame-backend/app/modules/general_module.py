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
            return await self._get_help_message(user_context)
        
        if "english" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "english"
            messages = [{"role": "user", "content": "I want to practice English. Welcome me to the English learning module with enthusiasm, using Kinyarwanda phrases and referencing how English connects Rwanda to the global community."}]
            if settings.use_llama:
                return await llama_service.generate_response(messages, "english")
            else:
                return await openai_service.generate_response(messages, "english")
        
        elif "math" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "math"
            messages = [{"role": "user", "content": "I want to practice math. Welcome me to the math module with excitement, using Kinyarwanda phrases and mentioning Rwandan contexts like RWF currency and distances between cities."}]
            if settings.use_llama:
                return await llama_service.generate_response(messages, "math")
            else:
                return await openai_service.generate_response(messages, "math")
        
        elif "comprehension" in user_input_lower or "reading" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "comprehension"
            messages = [{"role": "user", "content": "I want to practice reading comprehension. Welcome me to the comprehension module with enthusiasm, using Kinyarwanda phrases and mentioning Rwandan stories and cultural values like Ubuntu."}]
            if settings.use_llama:
                return await llama_service.generate_response(messages, "comprehension")
            else:
                return await openai_service.generate_response(messages, "comprehension")
        
        elif "debate" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "debate"
            messages = [{"role": "user", "content": "I want to practice debate and discussion. Welcome me to the debate module with enthusiasm, using Kinyarwanda phrases and mentioning Rwanda's values of respectful dialogue and Ubuntu philosophy."}]
            if settings.use_llama:
                return await llama_service.generate_response(messages, "debate")
            else:
                return await openai_service.generate_response(messages, "debate")
        
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
    
    async def _get_help_message(self, user_context: Dict[str, Any]) -> str:
        """Get help message explaining available modules using Llama/OpenAI with Rwanda context"""
        messages = [
            {"role": "user", "content": "Please explain what learning modules you offer and how you can help me learn, using Kinyarwanda phrases naturally and referencing Rwanda culture."}
        ]
        
        if settings.use_llama:
            response = await llama_service.generate_response(messages, self.module_name)
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        
        return response + "\n\nJust say what you'd like to try, like 'English' or 'Math'. Ni iki gikureba uyu munsi? (What interests you today?)"
    
    async def get_welcome_message(self, user_context: Dict[str, Any] = None) -> str:
        """Get welcome message for General module using Llama/OpenAI with Rwanda context"""
        messages = [
            {"role": "user", "content": "Give me a warm welcome message as BAKAME, an AI learning companion for Rwanda. Use Kinyarwanda phrases naturally and mention the learning modules available. Be enthusiastic and culturally appropriate."}
        ]
        
        if settings.use_llama:
            response = await llama_service.generate_response(messages, self.module_name)
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        
        return response

general_module = GeneralModule()
