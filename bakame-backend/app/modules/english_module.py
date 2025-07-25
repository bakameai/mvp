from typing import Dict, Any
from app.services.openai_service import openai_service
from app.services.llama_service import llama_service
from app.services.emotional_intelligence_service import emotional_intelligence_service
from app.services.gamification_service import gamification_service
from app.services.predictive_analytics_service import predictive_analytics
from app.config import settings

class EnglishModule:
    def __init__(self):
        self.module_name = "english"
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process English learning input"""
        
        emotion_data = await emotional_intelligence_service.detect_emotion(user_input)
        emotional_intelligence_service.track_emotional_journey(user_context, emotion_data)
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["exit", "quit", "stop", "back", "menu", "hello", "hi"]):
            user_context.setdefault("user_state", {})["requested_module"] = "general"
            return "Returning to main menu. How can I help you today?"
        
        gamification_service.update_progress(user_context, "session_complete", self.module_name)
        
        if any(word in user_input_lower for word in ["grammar", "correct", "fix"]):
            base_response = await self._grammar_correction(user_input, user_context)
        elif any(word in user_input_lower for word in ["repeat", "practice", "pronunciation"]):
            base_response = await self._repeat_practice(user_input, user_context)
        elif any(word in user_input_lower for word in ["help", "learn", "teach"]):
            base_response = await self._english_tutoring(user_input, user_context)
        else:
            base_response = await self._english_tutoring(user_input, user_context)
        
        new_achievements = gamification_service.check_achievements(user_context)
        if new_achievements:
            achievement_msg = "\n\n" + "\n".join([ach["message"] for ach in new_achievements])
            base_response += achievement_msg
        
        return await emotional_intelligence_service.generate_emotionally_aware_response(
            user_input, base_response, emotion_data, self.module_name
        )
    
    async def _grammar_correction(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Provide grammar correction and feedback"""
        messages = [
            {"role": "user", "content": f"Please correct any grammar mistakes in this sentence and explain the corrections: '{user_input}'"}
        ]
        
        for interaction in user_context.get("conversation_history", [])[-4:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        if settings.use_llama:
            response = await llama_service.generate_response(messages, self.module_name)
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        return response
    
    async def _repeat_practice(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Provide pronunciation and repetition practice"""
        messages = [
            {"role": "user", "content": f"Help me practice pronunciation. Give me feedback on how I said: '{user_input}' and provide a similar sentence to practice."}
        ]
        
        if settings.use_llama:
            response = await llama_service.generate_response(messages, self.module_name)
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        return response
    
    async def _english_tutoring(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """General English tutoring and conversation"""
        messages = [
            {"role": "user", "content": user_input}
        ]
        
        for interaction in user_context.get("conversation_history", [])[-4:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        if settings.use_llama:
            response = await llama_service.generate_response(messages, self.module_name)
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        return response
    
    def get_welcome_message(self) -> str:
        """Get welcome message for English module"""
        return "Muraho! 🌟 I'm so excited to practice English with you! English opens many doors in Rwanda and connects us to the global community while we maintain our beautiful Kinyarwanda heritage. Whether you want to improve grammar, pronunciation, or just have great conversations - I'm here to help. What aspect of English would you like to explore together?"

english_module = EnglishModule()
