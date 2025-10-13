from typing import Dict, Any
from app.services.openai_service import openai_service
from app.services.llama_service import llama_service
from app.config import settings

class GeneralModule:
    def __init__(self):
        self.module_name = "general"
    
    async def process(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process general questions and conversations using OpenAI/Llama"""
        
        user_input_lower = user_input.lower()
        
        # Handle greetings and initial interactions
        if user_input == "Hello" or "hello" in user_input_lower:
            # Generate contextual welcome using AI
            messages = [
                {"role": "system", "content": "You're BAKAME, a warm AI learning companion. Generate a friendly greeting."},
                {"role": "user", "content": "The user just said hello. Greet them warmly and ask what they'd like to learn today."}
            ]
            if settings.use_llama:
                return await llama_service.generate_response(messages, self.module_name)
            else:
                return await openai_service.generate_response(messages, self.module_name)
        
        # Handle silence
        if "[User was silent]" in user_input:
            messages = [
                {"role": "system", "content": "The user hasn't spoken. Gently encourage them to speak or ask if they need help."},
                {"role": "user", "content": "User is silent"}
            ]
            if settings.use_llama:
                return await llama_service.generate_response(messages, self.module_name)
            else:
                return await openai_service.generate_response(messages, self.module_name)
        
        # Module selection logic
        if "english" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "english"
            messages = [{"role": "user", "content": "Welcome me to English practice briefly."}]
            if settings.use_llama:
                return await llama_service.generate_response(messages, "english")
            else:
                return await openai_service.generate_response(messages, "english")
                
        elif "math" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "math"
            messages = [{"role": "user", "content": "Welcome me to math practice briefly."}]
            if settings.use_llama:
                return await llama_service.generate_response(messages, "math")
            else:
                return await openai_service.generate_response(messages, "math")
                
        elif "comprehension" in user_input_lower or "reading" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "comprehension"
            messages = [{"role": "user", "content": "Welcome me to reading practice briefly."}]
            if settings.use_llama:
                return await llama_service.generate_response(messages, "comprehension")
            else:
                return await openai_service.generate_response(messages, "comprehension")
                
        elif "debate" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "debate"
            messages = [{"role": "user", "content": "Welcome me to debate practice briefly."}]
            if settings.use_llama:
                return await llama_service.generate_response(messages, "debate")
            else:
                return await openai_service.generate_response(messages, "debate")
        
        # General conversation - Always use AI for responses
        conversation_history = user_context.get("conversation_history", [])
        
        # Build message history for context
        messages = []
        
        # Include recent conversation history (last 5 exchanges)
        for interaction in conversation_history[-5:]:
            if "user" in interaction:
                messages.append({"role": "user", "content": interaction["user"]})
            if "ai" in interaction:
                messages.append({"role": "assistant", "content": interaction["ai"]})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        # Generate response using OpenAI or Llama
        if settings.use_llama:
            response = await llama_service.generate_response(messages, self.module_name)
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        
        # Store this interaction in conversation history
        if "conversation_history" not in user_context:
            user_context["conversation_history"] = []
        user_context["conversation_history"].append({
            "user": user_input,
            "ai": response
        })
        
        return response

general_module = GeneralModule()