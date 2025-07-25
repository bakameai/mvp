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
        
        self.cultural_responses = {
            "frustrated": {
                "kinyarwanda": "Ntugire ubwoba",
                "meaning": "Don't be afraid",
                "response": "I understand this feels challenging. Remember, even the highest hills in Rwanda were climbed one step at a time. Ntugire ubwoba - don't be afraid. Let's break this down together, slowly and patiently."
            },
            "confident": {
                "kinyarwanda": "Byiza cyane!",
                "meaning": "Very good!",
                "response": "Byiza cyane! Your confidence shines like the morning sun over Lake Kivu. This positive energy will carry you far in your learning journey. Let's keep building on this strong foundation!"
            },
            "discouraged": {
                "kinyarwanda": "Komera",
                "meaning": "Be strong",
                "response": "Komera, my friend. Rwanda's story teaches us that from the darkest moments can come the brightest futures. Every learner faces challenges - this is how we grow stronger. Ubuntu reminds us we're in this together."
            },
            "motivated": {
                "kinyarwanda": "Urashaka kwiga!",
                "meaning": "You want to learn!",
                "response": "Urashaka kwiga! Your enthusiasm is like the energy of Kigali's bustling markets. This hunger for knowledge will take you places. Rwanda's future is built by learners like you!"
            },
            "confused": {
                "kinyarwanda": "Tuzabisobanura",
                "meaning": "We will explain it",
                "response": "Tuzabisobanura - we will explain it together. Like a patient teacher in a Rwandan village, I'm here to guide you step by step. No question is too small, no confusion too great to overcome."
            },
            "positive": {
                "kinyarwanda": "Murakoze cyane!",
                "meaning": "Thank you very much!",
                "response": "Murakoze cyane! Your positive spirit brings joy like children playing in Rwanda's green hills. This attitude will make your learning journey both successful and enjoyable."
            }
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
        
        cultural_response = self.cultural_responses.get(primary_emotion)
        if not cultural_response:
            return base_response
        
        emotional_prefix = ""
        if intensity > 0.7:
            emotional_prefix = f"{cultural_response['response']}\n\n"
        elif intensity > 0.5:
            emotional_prefix = f"{cultural_response['kinyarwanda']} ({cultural_response['meaning']})! "
        
        if primary_emotion in ["frustrated", "confused", "discouraged"]:
            messages = [
                {"role": "user", "content": f"The user seems {primary_emotion} about: {user_input}. Provide additional encouragement and support using Rwanda cultural context. Be extra patient and supportive."}
            ]
            
            if settings.use_llama:
                additional_support = await llama_service.generate_response(messages, module_name)
            else:
                additional_support = await openai_service.generate_response(messages, module_name)
            
            return f"{emotional_prefix}{base_response}\n\n{additional_support}"
        
        elif primary_emotion in ["confident", "motivated", "positive"]:
            return f"{emotional_prefix}{base_response}"
        
        return base_response
    
    def get_encouragement_phrase(self, emotion: str) -> str:
        """Get appropriate Kinyarwanda encouragement phrase"""
        cultural_response = self.cultural_responses.get(emotion, self.cultural_responses["positive"])
        return f"{cultural_response['kinyarwanda']} ({cultural_response['meaning']})"
    
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
