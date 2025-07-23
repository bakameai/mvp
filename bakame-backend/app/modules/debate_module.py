import random
from typing import Dict, Any
from app.services.openai_service import openai_service

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
            return self._start_new_debate(user_context)
        
        if current_topic:
            return await self._continue_debate(user_input, current_topic, debate_round, user_context)
        
        return self._start_new_debate(user_context)
    
    def _start_new_debate(self, user_context: Dict[str, Any]) -> str:
        """Start a new debate topic"""
        
        topic = random.choice(self.debate_topics)
        
        user_context.setdefault("user_state", {})["current_debate_topic"] = topic
        user_context["user_state"]["debate_round"] = 1
        user_context["user_state"]["user_position"] = None
        
        return f"Let's debate! Here's today's topic: {topic}\n\nWhat's your opinion? Do you agree or disagree? Please share your thoughts and reasoning."
    
    async def _continue_debate(self, user_input: str, current_topic: str, debate_round: int, user_context: Dict[str, Any]) -> str:
        """Continue the debate conversation"""
        
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
        
        for interaction in user_context.get("conversation_history", [])[-2:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        response = await openai_service.generate_response(messages, self.module_name)
        
        user_stats["debate_round"] = debate_round + 1
        
        if debate_round >= 3:
            user_stats["current_debate_topic"] = None
            user_stats["debate_round"] = 0
            user_stats["debates_completed"] = user_stats.get("debates_completed", 0) + 1
            response += "\n\nGreat debate! Would you like to try another topic?"
        
        return response
    
    def get_welcome_message(self) -> str:
        """Get welcome message for Debate module"""
        return "Welcome to Debate Practice! I'll present you with interesting topics and challenge your thinking. This helps develop critical thinking and argumentation skills. Ready for a topic?"

debate_module = DebateModule()
