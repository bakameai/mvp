from typing import Dict, Any
from app.services.openai_service import openai_service
from app.services.emotional_intelligence_service import emotional_intelligence_service
from app.services.gamification_service import gamification_service
from app.services.wellness_service import wellness_service
from app.services.economic_empowerment_service import economic_empowerment_service
from app.services.offline_service import offline_service
from app.services.multimodal_service import multimodal_service
from app.config import settings

class GeneralModule:
    def __init__(self):
        self.module_name = "general"
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process general questions and conversations"""
        
        emotion_data = await emotional_intelligence_service.detect_emotion(user_input)
        emotional_intelligence_service.track_emotional_journey(user_context, emotion_data)
        
        gamification_service.update_progress(user_context, "session_complete", self.module_name)
        
        user_input_lower = user_input.lower()
        
        if not user_context.get("user_name"):
            user_context["user_name"] = user_input.strip()
            from app.services.redis_service import redis_service
            redis_service.set_user_context(user_context.get("phone_number", ""), user_context)
            return f"Nice to meet you, {user_input.strip()}! Before we start learning, tell me: what subjects interest you most? For example, you could say 'I love math and want to practice calculations' or 'I need help with English conversation'."
        
        if not user_context.get("learning_preferences") and not any(word in user_input.lower() for word in ["english", "math", "reading", "debate", "help", "menu"]):
            user_context["learning_preferences"] = user_input.strip()
            from app.services.redis_service import redis_service
            redis_service.set_user_context(user_context.get("phone_number", ""), user_context)
            return f"Perfect! I understand you're interested in {user_input.strip()}. I can help with English, Math, Reading, and Debate. Based on what you told me, which would you like to start with today?"
        
        if any(word in user_input_lower for word in ["bye", "goodbye", "stop", "quit", "done"]):
            return f"Want to keep learning or stop for now? You did great today, {user_context.get('user_name', 'friend')}. I'll be here next time you call."
        
        if any(word in user_input_lower for word in ["help", "what can you do", "modules", "options", "menu"]):
            base_response = await self._get_help_message(user_context)
            return await emotional_intelligence_service.generate_emotionally_aware_response(
                user_input, base_response, emotion_data, self.module_name
            )
        
        if "english" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "english"
            messages = [{"role": "user", "content": "Welcome me to English practice briefly. Say 'Muraho' and ask what I'd like to work on."}]
            base_response = await openai_service.generate_response(messages, "english")
            return await emotional_intelligence_service.generate_emotionally_aware_response(
                user_input, base_response, emotion_data, "english"
            )
        
        elif "math" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "math"
            messages = [{"role": "user", "content": "Welcome me to math practice briefly. Say 'Muraho' and mention RWF examples."}]
            base_response = await openai_service.generate_response(messages, "math")
            return await emotional_intelligence_service.generate_emotionally_aware_response(
                user_input, base_response, emotion_data, "math"
            )
        
        elif "comprehension" in user_input_lower or "reading" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "comprehension"
            messages = [{"role": "user", "content": "Welcome me to reading practice briefly. Say 'Muraho' and mention Rwandan stories."}]
            return await openai_service.generate_response(messages, "comprehension")
        
        elif "debate" in user_input_lower:
            user_context.setdefault("user_state", {})["requested_module"] = "debate"
            messages = [{"role": "user", "content": "Welcome me to debate practice briefly. Say 'Muraho' and mention respectful dialogue."}]
            return await openai_service.generate_response(messages, "debate")
        
        elif any(word in user_input_lower for word in ["wellness", "health", "mood", "nutrition"]):
            if "mood" in user_input_lower:
                result = await wellness_service.conduct_mood_check(user_context.get("phone_number", ""), user_input)
                return result.get("message", "How are you feeling today? Reply with 1-5 (1=very sad, 5=very happy).")
            elif "nutrition" in user_input_lower:
                result = await wellness_service.provide_nutrition_guidance(user_context.get("phone_number", ""), user_input)
                return result.get("message", "What Rwandan food would you like to know about? Try 'ubwoba', 'igikoma', or 'amaru'.")
            else:
                result = await wellness_service.suggest_wellness_activity(user_context.get("phone_number", ""))
                return result.get("message", "Here's a wellness activity for you!")
        
        elif any(word in user_input_lower for word in ["money", "business", "savings", "entrepreneur", "financial"]):
            if "business" in user_input_lower:
                result = await economic_empowerment_service.suggest_business_idea(user_context.get("phone_number", ""))
                return result.get("message", "Here's a business idea for you!")
            elif "savings" in user_input_lower:
                result = await economic_empowerment_service.provide_savings_tip(user_context.get("phone_number", ""))
                return result.get("message", "Here's a savings tip!")
            else:
                result = await economic_empowerment_service.provide_financial_education(user_context.get("phone_number", ""), user_input)
                return result.get("message", "Let me help you with financial literacy!")
        
        messages = [{"role": "user", "content": user_input}]
        
        for interaction in user_context.get("conversation_history", [])[-5:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        response = await openai_service.generate_response(messages, self.module_name)
        
        if len(user_context.get("conversation_history", [])) % 3 == 0:
            response += "\n\nMurabona, I can also help you with English, Math, Reading Comprehension, or Debate practice. Just say what you'd like to try!"
        
        return response
    
    async def _get_help_message(self, user_context: Dict[str, Any]) -> str:
        """Get help message explaining available modules using Llama/OpenAI with Rwanda context"""
        messages = [
            {"role": "user", "content": "Please explain what learning modules you offer and how you can help me learn, using Kinyarwanda phrases naturally and referencing Rwanda culture."}
        ]
        
        response = await openai_service.generate_response(messages, self.module_name)
        
        return response + "\n\nJust say what you'd like to try, like 'English' or 'Math'. Ni iki gikureba uyu munsi? (What interests you today?)"
    
    async def get_welcome_message(self, user_context: Dict[str, Any] = None) -> str:
        """Get welcome message for General module - ask for name first"""
        user_name = user_context.get("user_name") if user_context else None
        
        if not user_name:
            return "Hello! I'm Bakame, your learning helper. What's your name?"
        else:
            return f"Hello {user_name}! I can help with English, Math, Reading, and Debate. What would you like to try?"

general_module = GeneralModule()
