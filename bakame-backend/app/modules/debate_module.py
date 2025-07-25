import random
from typing import Dict, Any
from app.services.openai_service import openai_service
from app.services.llama_service import llama_service
from app.services.newsapi_service import newsapi_service
from app.services.emotional_intelligence_service import emotional_intelligence_service
from app.services.gamification_service import gamification_service
from app.services.predictive_analytics_service import predictive_analytics
from app.config import settings

class DebateModule:
    def __init__(self):
        self.module_name = "debate"
        self.debate_topics = [
            "Should students be required to wear school uniforms?",
            "Is social media more helpful or harmful to society?",
            "Should homework be banned in elementary schools?",
            "Is it better to live in a city or in the countryside?",
            "Should everyone learn a second language?",
            "Is it more important to be smart or kind?",
            "Should children have chores at home?",
            "Is reading books better than watching movies?",
            "Should schools have longer or shorter summer breaks?",
            "Is it better to have a few close friends or many acquaintances?"
        ]
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process debate input"""
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["exit", "quit", "stop", "back", "menu", "hello", "hi"]):
            user_context.setdefault("user_state", {})["current_debate_topic"] = None
            user_context["user_state"]["requested_module"] = "general"
            return "Returning to main menu. How can I help you today?"
        
        current_topic = user_context.get("user_state", {}).get("current_debate_topic")
        debate_round = user_context.get("user_state", {}).get("debate_round", 0)
        
        if any(word in user_input_lower for word in ["new", "another", "next", "topic", "different"]):
            return await self._start_new_debate(user_context)
        
        if current_topic:
            return await self._continue_debate(user_input, current_topic, debate_round, user_context)
        
        return await self._start_new_debate(user_context)
    
    async def _start_new_debate(self, user_context: Dict[str, Any]) -> str:
        """Start a new debate topic using trending news"""
        
        print("DEBUG: Starting new debate, fetching trending topics...")
        trending_topics = await newsapi_service.get_trending_debate_topics(count=1)
        print(f"DEBUG: Got trending topics: {trending_topics}")
        
        if trending_topics:
            topic = trending_topics[0]
            print(f"DEBUG: Using trending topic: {topic}")
        else:
            topic = random.choice(self.debate_topics)
            print(f"DEBUG: Using fallback topic: {topic}")
        
        user_context.setdefault("user_state", {})["current_debate_topic"] = topic
        user_context["user_state"]["debate_round"] = 1
        user_context["user_state"]["user_position"] = None
        
        return f"Let's debate a trending topic! Here's what's making headlines: {topic}\n\nWhat's your opinion? Do you agree or disagree? Please share your thoughts and reasoning."
    
    async def _continue_debate(self, user_input: str, current_topic: str, debate_round: int, user_context: Dict[str, Any]) -> str:
        """Continue the debate conversation"""
        
        emotion_data = await emotional_intelligence_service.detect_emotion(user_input)
        emotional_intelligence_service.track_emotional_journey(user_context, emotion_data)
        
        user_stats = user_context.get("user_state", {})
        
        if not user_stats.get("user_position"):
            if any(word in user_input.lower() for word in ["agree", "yes", "support", "favor", "think so", "believe"]):
                user_stats["user_position"] = "agree"
            elif any(word in user_input.lower() for word in ["disagree", "no", "against", "oppose", "don't think", "don't believe"]):
                user_stats["user_position"] = "disagree"
            else:
                user_stats["user_position"] = "neutral"
        
        if debate_round == 1:
            prompt = f"Topic: {current_topic}\nUser's position: {user_input}\n\nAs a debate coach, acknowledge their position and provide a thoughtful counter-argument to challenge their thinking. Be respectful but thought-provoking."
        elif debate_round == 2:
            prompt = f"Topic: {current_topic}\nUser's latest argument: {user_input}\n\nAs a debate coach, ask probing questions about their reasoning and present additional perspectives they might not have considered."
        else:
            prompt = f"Topic: {current_topic}\nUser's argument: {user_input}\n\nAs a debate coach, provide a thoughtful summary of the debate, acknowledge good points made, and suggest areas for further reflection. Keep it encouraging."
        
        messages = [{"role": "user", "content": prompt}]
        
        for interaction in user_context.get("conversation_history", [])[-4:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        if settings.use_llama:
            base_response = await llama_service.generate_response(messages, self.module_name)
        else:
            base_response = await openai_service.generate_response(messages, self.module_name)
        
        user_stats["debate_round"] = debate_round + 1
        
        points_earned = gamification_service.update_progress(
            user_context, "debate_response", self.module_name
        )
        
        if debate_round >= 3:
            user_stats["current_debate_topic"] = None
            user_stats["debate_round"] = 0
            user_stats["debates_completed"] = user_stats.get("debates_completed", 0) + 1
            
            gamification_service.update_progress(user_context, "completed_debate", self.module_name)
            
            new_achievements = gamification_service.check_achievements(user_context)
            if new_achievements:
                achievement_msg = "\n\n" + "\n".join([ach["message"] for ach in new_achievements])
                base_response += achievement_msg
            
            if points_earned > 0:
                base_response += f"\n\n+{points_earned} points earned! 🌟"
            
            base_response += "\n\nGreat debate! Would you like to try another topic?"
        
        return await emotional_intelligence_service.generate_emotionally_aware_response(
            user_input, base_response, emotion_data, self.module_name
        )
    
    def get_welcome_message(self) -> str:
        """Get welcome message for Debate module"""
        return "Muraho! Ready for some thoughtful discussion? 🤔 In Rwanda, we value respectful dialogue, Ubuntu, and learning from different perspectives. I love exploring ideas that matter to our community and nation-building. Debates help us think deeper and see things from new angles while respecting our values of unity and understanding. Want to dive into a good discussion?"

debate_module = DebateModule()
