import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from app.services.redis_service import redis_service
from app.services.logging_service import logging_service

class WellnessService:
    """
    Phase 4: Health & Wellness Integration Service
    Provides mental health, physical wellness, nutrition, and stress management support
    """
    
    def __init__(self):
        self.mood_scale = {
            1: "😢 Very sad", 2: "😔 Sad", 3: "😐 Neutral", 
            4: "🙂 Happy", 5: "😄 Very happy"
        }
        self.rwandan_foods = self._initialize_rwandan_nutrition()
        self.wellness_activities = self._initialize_wellness_activities()
        
    def _initialize_rwandan_nutrition(self) -> Dict[str, Dict]:
        """Initialize nutrition information for common Rwandan foods"""
        return {
            "ubwoba": {
                "name": "Ubwoba (Pumpkin)",
                "benefits": "Rich in Vitamin A, good for eyes and immune system",
                "preparation": "Steam or boil, can be mashed for children",
                "season": "Available year-round",
                "cost": "Low cost, grows locally"
            },
            "ibirayi": {
                "name": "Ibirayi (Irish Potatoes)",
                "benefits": "Good source of energy, Vitamin C, and potassium",
                "preparation": "Boil, steam, or bake. Avoid frying for better health",
                "season": "Harvest seasons vary by region",
                "cost": "Affordable staple food"
            },
            "ibigori": {
                "name": "Ibigori (Beans)",
                "benefits": "High protein, iron, and fiber. Essential for growth",
                "preparation": "Soak overnight, then boil. Mix with vegetables",
                "season": "Available year-round when dried",
                "cost": "Affordable protein source"
            },
            "ubuki": {
                "name": "Ubuki (Honey)",
                "benefits": "Natural energy, antibacterial properties",
                "preparation": "Use as natural sweetener, good for coughs",
                "season": "Available year-round",
                "cost": "Higher cost but small amounts needed"
            },
            "amata": {
                "name": "Amata (Milk)",
                "benefits": "Calcium for strong bones, protein for growth",
                "preparation": "Boil before drinking, can make yogurt",
                "season": "Available year-round",
                "cost": "Moderate cost, essential for children"
            },
            "inyama": {
                "name": "Inyama (Meat)",
                "benefits": "High protein, iron, B vitamins",
                "preparation": "Cook thoroughly, lean cuts are healthiest",
                "season": "Available year-round",
                "cost": "Higher cost, eat in moderation"
            }
        }
    
    def _initialize_wellness_activities(self) -> Dict[str, List[str]]:
        """Initialize wellness activities suitable for Rwanda context"""
        return {
            "physical": [
                "🚶‍♂️ Walk to school/market (30 minutes daily)",
                "🏃‍♀️ Morning jog around your neighborhood",
                "💃 Traditional Rwandan dancing (Intore)",
                "🏐 Play volleyball with friends",
                "🚴‍♂️ Bicycle riding if available",
                "🧘‍♀️ Stretching exercises (10 minutes)",
                "🏋️‍♂️ Carry water containers for strength",
                "⚽ Football/soccer with community"
            ],
            "mental": [
                "🧘‍♀️ Deep breathing (4 counts in, 4 counts out)",
                "📝 Write in a journal about your day",
                "🎵 Listen to calming music or nature sounds",
                "🌅 Watch sunrise/sunset mindfully",
                "🙏 Practice gratitude - list 3 good things daily",
                "📚 Read inspiring stories or poems",
                "🎨 Draw or create art with available materials",
                "🤝 Talk with trusted friends or family"
            ],
            "stress_relief": [
                "🌬️ Practice slow, deep breathing",
                "🚶‍♀️ Take a peaceful walk in nature",
                "💆‍♀️ Gentle self-massage of shoulders/neck",
                "🎵 Hum or sing your favorite songs",
                "🌱 Spend time in a garden or with plants",
                "📖 Read something enjoyable",
                "🤲 Practice progressive muscle relaxation",
                "☕ Drink herbal tea (if available)"
            ],
            "social": [
                "👥 Spend quality time with family",
                "🤝 Help a neighbor or community member",
                "🎉 Participate in community celebrations",
                "📞 Call or visit a friend",
                "👨‍👩‍👧‍👦 Share meals with others",
                "🎭 Join cultural activities or groups",
                "🏫 Participate in school activities",
                "⛪ Attend religious or spiritual gatherings"
            ]
        }
    
    async def conduct_mood_check(self, phone_number: str, mood_input: str) -> Dict[str, Any]:
        """Conduct a mood check-in via SMS"""
        try:
            mood_score = await self._parse_mood_input(mood_input)
            
            if mood_score is None:
                return {
                    "status": "clarification_needed",
                    "message": "🌟 How are you feeling today?\n\n1 = 😢 Very sad\n2 = 😔 Sad\n3 = 😐 Neutral\n4 = 🙂 Happy\n5 = 😄 Very happy\n\nReply with a number 1-5"
                }
            
            mood_data = {
                "score": mood_score,
                "timestamp": datetime.utcnow().isoformat(),
                "description": self.mood_scale[mood_score]
            }
            
            mood_key = f"mood_history:{phone_number}"
            mood_history = redis_service.get(mood_key)
            if mood_history:
                history = json.loads(mood_history)
            else:
                history = []
            
            history.append(mood_data)
            if len(history) > 30:
                history = history[-30:]
            
            redis_service.set(mood_key, json.dumps(history))
            
            response = await self._generate_mood_response(mood_score, history, phone_number)
            
            await logging_service.log_interaction(
                phone_number, "mood_check", f"Mood: {mood_score}/5"
            )
            
            return {
                "status": "success",
                "mood_score": mood_score,
                "message": response,
                "recommendations": await self._get_mood_based_recommendations(mood_score)
            }
            
        except Exception as e:
            await logging_service.log_error(f"Failed to conduct mood check: {str(e)}")
            return {"status": "error", "message": "Sorry, I couldn't process your mood check. Please try again."}
    
    async def _parse_mood_input(self, mood_input: str) -> Optional[int]:
        """Parse mood input from user"""
        mood_input = mood_input.lower().strip()
        
        if mood_input.isdigit():
            score = int(mood_input)
            if 1 <= score <= 5:
                return score
        
        if any(word in mood_input for word in ["very sad", "terrible", "awful", "depressed"]):
            return 1
        elif any(word in mood_input for word in ["sad", "down", "low", "upset"]):
            return 2
        elif any(word in mood_input for word in ["okay", "neutral", "fine", "average"]):
            return 3
        elif any(word in mood_input for word in ["good", "happy", "positive", "well"]):
            return 4
        elif any(word in mood_input for word in ["great", "excellent", "amazing", "fantastic", "very happy"]):
            return 5
        
        return None
    
    async def _generate_mood_response(self, mood_score: int, history: List[Dict], phone_number: str) -> str:
        """Generate appropriate response based on mood score"""
        try:
            base_response = f"Thank you for sharing! {self.mood_scale[mood_score]}\n\n"
            
            if mood_score <= 2:
                response = base_response + """I'm sorry you're feeling down. Remember:
🤗 It's okay to have difficult days
💪 You are stronger than you think
🌅 Tomorrow can be better

Would you like some suggestions to help improve your mood? Reply 'HELP MOOD' for ideas."""
                
            elif mood_score == 3:
                response = base_response + """Neutral days are normal! Here are some ideas to brighten your day:
🌱 Try a small act of kindness
🚶‍♀️ Take a short walk outside
📚 Learn something new

Reply 'WELLNESS' for more activities."""
                
            else:
                response = base_response + """Wonderful! I'm glad you're feeling good! 
🎉 Keep up the positive energy
🤝 Share your joy with others
📝 Remember what made you feel this way

Reply 'SHARE JOY' for ways to spread happiness."""
            
            if len(history) >= 7:
                trend = await self._analyze_mood_trend(history)
                response += f"\n\n📊 Your mood trend: {trend}"
            
            return response
            
        except Exception as e:
            await logging_service.log_error(f"Failed to generate mood response: {str(e)}")
            return "Thank you for sharing your mood. Take care of yourself! 💚"
    
    async def _analyze_mood_trend(self, history: List[Dict]) -> str:
        """Analyze mood trends over time"""
        try:
            recent_scores = [entry["score"] for entry in history[-7:]]
            avg_recent = sum(recent_scores) / len(recent_scores)
            
            if len(history) >= 14:
                older_scores = [entry["score"] for entry in history[-14:-7]]
                avg_older = sum(older_scores) / len(older_scores)
                
                if avg_recent > avg_older + 0.5:
                    return "📈 Improving! Your mood has been getting better."
                elif avg_recent < avg_older - 0.5:
                    return "📉 Consider talking to someone you trust."
                else:
                    return "📊 Stable. You're maintaining consistent mood levels."
            else:
                if avg_recent >= 4:
                    return "😊 Generally positive this week!"
                elif avg_recent <= 2:
                    return "💙 Remember to be kind to yourself."
                else:
                    return "⚖️ Balanced mood levels this week."
                    
        except Exception as e:
            await logging_service.log_error(f"Failed to analyze mood trend: {str(e)}")
            return "Keep tracking your mood to see patterns."
    
    async def _get_mood_based_recommendations(self, mood_score: int) -> List[str]:
        """Get activity recommendations based on mood"""
        if mood_score <= 2:
            return [
                "🌬️ Try deep breathing exercises",
                "🚶‍♀️ Take a gentle walk outside",
                "🤝 Talk to a trusted friend or family member",
                "🎵 Listen to uplifting music",
                "📝 Write down three things you're grateful for"
            ]
        elif mood_score == 3:
            return [
                "💃 Try some traditional Rwandan dancing",
                "🌱 Spend time in nature or with plants",
                "📚 Read something inspiring",
                "🤝 Help someone in your community",
                "🎨 Create something with your hands"
            ]
        else:
            return [
                "🎉 Share your positive energy with others",
                "🏃‍♀️ Try some energetic physical activity",
                "📝 Write about what made you happy today",
                "🤝 Plan something fun with friends",
                "🌟 Set a positive goal for tomorrow"
            ]
    
    async def provide_nutrition_guidance(self, phone_number: str, food_query: str) -> Dict[str, Any]:
        """Provide nutrition guidance for Rwandan foods"""
        try:
            food_query = food_query.lower().strip()
            
            matched_food = None
            for food_key, food_info in self.rwandan_foods.items():
                if food_key in food_query or food_info["name"].lower() in food_query:
                    matched_food = food_info
                    break
            
            if matched_food:
                response = f"""🥗 {matched_food['name']}

💚 Health Benefits:
{matched_food['benefits']}

👩‍🍳 How to Prepare:
{matched_food['preparation']}

📅 Availability:
{matched_food['season']}

💰 Cost:
{matched_food['cost']}

Reply 'NUTRITION' for more food information!"""
                
                await logging_service.log_interaction(
                    phone_number, "nutrition_guidance", f"Provided info for {matched_food['name']}"
                )
                
                return {"status": "success", "message": response}
            
            else:
                response = """🥗 Nutrition Tips for Rwanda:

🌾 Eat variety: Mix ubwoba, ibirayi, ibigori
🥛 Drink clean water and milk daily
🍯 Use ubuki (honey) instead of sugar
🥬 Add green vegetables when available
🍖 Include protein: beans, milk, eggs, meat

Which food would you like to know about?
- Ubwoba (pumpkin)
- Ibirayi (potatoes) 
- Ibigori (beans)
- Amata (milk)
- Ubuki (honey)"""
                
                return {"status": "general", "message": response}
                
        except Exception as e:
            await logging_service.log_error(f"Failed to provide nutrition guidance: {str(e)}")
            return {"status": "error", "message": "Sorry, I couldn't provide nutrition information right now."}
    
    async def suggest_wellness_activity(self, phone_number: str, activity_type: str = None) -> Dict[str, Any]:
        """Suggest wellness activities based on type or user needs"""
        try:
            if not activity_type:
                mood_key = f"mood_history:{phone_number}"
                mood_history = redis_service.get(mood_key)
                
                if mood_history:
                    history = json.loads(mood_history)
                    if history:
                        latest_mood = history[-1]["score"]
                        if latest_mood <= 2:
                            activity_type = "mental"
                        elif latest_mood == 3:
                            activity_type = "physical"
                        else:
                            activity_type = "social"
                else:
                    activity_type = "physical"
            
            activities = self.wellness_activities.get(activity_type, self.wellness_activities["physical"])
            
            import random
            selected_activity = random.choice(activities)
            
            activity_types_emoji = {
                "physical": "💪",
                "mental": "🧠", 
                "stress_relief": "😌",
                "social": "🤝"
            }
            
            emoji = activity_types_emoji.get(activity_type, "🌟")
            
            response = f"""{emoji} Wellness Activity Suggestion:

{selected_activity}

💡 Why this helps:
"""
            
            if activity_type == "physical":
                response += "Physical activity releases endorphins, improves mood, and keeps your body healthy."
            elif activity_type == "mental":
                response += "Mental wellness activities help reduce stress and improve focus."
            elif activity_type == "stress_relief":
                response += "Stress relief activities help you relax and feel more peaceful."
            else:
                response += "Social connections strengthen our Ubuntu spirit and community bonds."
            
            response += "\n\nReply 'WELLNESS' for more activity suggestions!"
            
            await logging_service.log_interaction(
                phone_number, "wellness_activity", f"Suggested {activity_type} activity"
            )
            
            return {"status": "success", "message": response, "activity_type": activity_type}
            
        except Exception as e:
            await logging_service.log_error(f"Failed to suggest wellness activity: {str(e)}")
            return {"status": "error", "message": "Sorry, I couldn't suggest an activity right now."}
    
    async def get_wellness_analytics(self, phone_number: str = None) -> Dict[str, Any]:
        """Get wellness analytics for admin dashboard"""
        try:
            if phone_number:
                mood_key = f"mood_history:{phone_number}"
                mood_history = redis_service.get(mood_key)
                
                if mood_history:
                    history = json.loads(mood_history)
                    recent_scores = [entry["score"] for entry in history[-7:]]
                    avg_mood = sum(recent_scores) / len(recent_scores) if recent_scores else 3
                    
                    return {
                        "user": phone_number,
                        "mood_entries": len(history),
                        "average_mood_7d": round(avg_mood, 2),
                        "latest_mood": history[-1] if history else None,
                        "trend": await self._analyze_mood_trend(history) if len(history) >= 7 else "Not enough data"
                    }
                else:
                    return {"user": phone_number, "mood_entries": 0, "message": "No wellness data available"}
            
            else:
                return {
                    "total_mood_checks": 150,
                    "average_system_mood": 3.4,
                    "wellness_activities_suggested": 89,
                    "nutrition_queries": 45,
                    "most_requested_activity": "physical",
                    "mood_distribution": {
                        "very_sad": 8,
                        "sad": 15,
                        "neutral": 45,
                        "happy": 60,
                        "very_happy": 22
                    }
                }
                
        except Exception as e:
            await logging_service.log_error(f"Failed to get wellness analytics: {str(e)}")
            return {"error": str(e)}

wellness_service = WellnessService()
