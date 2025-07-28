import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
from app.services.llama_service import llama_service
from app.services.openai_service import openai_service
from app.config import settings

class EmotionalIntelligenceService:
    def __init__(self):
        self.emotion_patterns = {
            "frustrated": [
                r"difficult|hard|can't|cannot|don't understand|confused|stuck|frustrated|annoying",
                r"this is too|i give up|i quit|why is this|hate this|stupid"
            ],
            "confident": [
                r"easy|simple|got it|understand|know|sure|confident|ready|bring it",
                r"i can do|piece of cake|no problem|let's go|excited"
            ],
            "discouraged": [
                r"tired|bored|pointless|useless|waste|give up|quit|stop|enough",
                r"not good|bad at|terrible|awful|hopeless|never learn"
            ],
            "motivated": [
                r"want to learn|excited|love|enjoy|fun|interesting|amazing|cool",
                r"more please|another|keep going|let's continue|teach me"
            ],
            "confused": [
                r"what|how|why|don't get|unclear|lost|mixed up|not sure",
                r"explain|help|repeat|again|slower|simpler"
            ],
            "positive": [
                r"good|great|awesome|wonderful|nice|perfect|excellent|brilliant",
                r"thank you|thanks|appreciate|helpful|love it|amazing"
            ]
        }
        
        self.sentiment_responses = {
            "frustrated": "No worries—we'll take it one step at a time.",
            "angry": "No worries—we'll take it one step at a time.",
            "confused": "You're doing fine. Let's try together.",
            "hesitant": "You're doing fine. Let's try together.",
            "happy": "Nice work! You're improving fast.",
            "confident": "Nice work! You're improving fast.",
            "sad": "Want to take a break or change topics?",
            "tired": "Want to take a break or change topics?",
            "neutral": "Still with me?",
            "quiet": "Ready for the next one?",
            "discouraged": "No worries—we'll take it one step at a time.",
            "motivated": "Nice work! You're improving fast.",
            "positive": "Nice work! You're improving fast."
        }
    
    async def detect_emotion(self, user_input: str, conversation_context: List[Dict] = None) -> Dict[str, Any]:
        """Detect emotional state from user input"""
        
        user_input_lower = user_input.lower()
        detected_emotions = []
        confidence_scores = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            total_matches = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, user_input_lower))
                total_matches += matches
            
            if total_matches > 0:
                confidence = min(total_matches * 0.3, 1.0)
                detected_emotions.append(emotion)
                confidence_scores[emotion] = confidence
        
        if not detected_emotions:
            detected_emotions = ["neutral"]
            confidence_scores["neutral"] = 0.5
        
        primary_emotion = max(detected_emotions, key=lambda e: confidence_scores.get(e, 0))
        
        return {
            "primary_emotion": primary_emotion,
            "all_emotions": detected_emotions,
            "confidence_scores": confidence_scores,
            "emotional_intensity": max(confidence_scores.values()) if confidence_scores else 0.5
        }
    
    async def generate_emotionally_aware_response(self, user_input: str, base_response: str, 
                                                emotion_data: Dict[str, Any], module_name: str = "general") -> str:
        """Generate response that adapts to user's emotional state"""
        
        primary_emotion = emotion_data.get("primary_emotion", "neutral")
        intensity = emotion_data.get("emotional_intensity", 0.5)
        
        if primary_emotion == "neutral" or intensity < 0.3:
            return base_response
        
        sentiment_response = self.sentiment_responses.get(primary_emotion)
        if not sentiment_response:
            return base_response
        
        if intensity > 0.5:
            return f"{sentiment_response} {base_response}"
        
        return base_response
    
    def get_encouragement_phrase(self, emotion: str) -> str:
        """Get appropriate encouragement phrase"""
        return self.sentiment_responses.get(emotion, "Thanks for learning with me—you're doing great.")
    
    def track_emotional_journey(self, user_context: Dict[str, Any], emotion_data: Dict[str, Any]):
        """Track user's emotional journey over time"""
        user_stats = user_context.setdefault("user_state", {})
        emotional_history = user_stats.setdefault("emotional_history", [])
        
        emotional_history.append({
            "timestamp": str(datetime.utcnow()),
            "primary_emotion": emotion_data.get("primary_emotion"),
            "intensity": emotion_data.get("emotional_intensity"),
            "all_emotions": emotion_data.get("all_emotions", [])
        })
        
        if len(emotional_history) > 20:
            emotional_history[:] = emotional_history[-20:]
        
        user_stats["current_emotional_state"] = emotion_data.get("primary_emotion")
        user_stats["emotional_trend"] = self._calculate_emotional_trend(emotional_history)
    
    def _calculate_emotional_trend(self, emotional_history: List[Dict]) -> str:
        """Calculate overall emotional trend"""
        if len(emotional_history) < 3:
            return "stable"
        
        recent_emotions = [entry["primary_emotion"] for entry in emotional_history[-5:]]
        positive_emotions = ["confident", "motivated", "positive"]
        negative_emotions = ["frustrated", "discouraged", "confused"]
        
        positive_count = sum(1 for emotion in recent_emotions if emotion in positive_emotions)
        negative_count = sum(1 for emotion in recent_emotions if emotion in negative_emotions)
        
        if positive_count > negative_count + 1:
            return "improving"
        elif negative_count > positive_count + 1:
            return "declining"
        else:
            return "stable"

emotional_intelligence_service = EmotionalIntelligenceService()
