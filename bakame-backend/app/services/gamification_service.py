from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

class GamificationService:
    def __init__(self):
        self.achievements = {
            "ubuntu_spirit": {
                "name": "Ubuntu Spirit",
                "description": "Completed 5 learning sessions showing community values",
                "kinyarwanda": "Ubwiyunge bw'Ubuntu",
                "icon": "🤝",
                "requirement": {"type": "sessions", "count": 5},
                "cultural_context": "Ubuntu teaches us we are stronger together"
            },
            "hill_climber": {
                "name": "Hill Climber", 
                "description": "Overcame 10 challenging problems",
                "kinyarwanda": "Umunyamusozi",
                "icon": "⛰️",
                "requirement": {"type": "difficult_problems", "count": 10},
                "cultural_context": "Like Rwanda's thousand hills, every challenge makes you stronger"
            },
            "knowledge_seeker": {
                "name": "Knowledge Seeker",
                "description": "Maintained 7-day learning streak",
                "kinyarwanda": "Ushaka ubumenyi",
                "icon": "📚",
                "requirement": {"type": "streak", "days": 7},
                "cultural_context": "Continuous learning builds our nation's future"
            },
            "unity_builder": {
                "name": "Unity Builder",
                "description": "Engaged in 5 respectful debates",
                "kinyarwanda": "Uwubaka ubumwe",
                "icon": "🕊️",
                "requirement": {"type": "debates", "count": 5},
                "cultural_context": "Respectful dialogue strengthens our unity"
            },
            "math_champion": {
                "name": "Math Champion",
                "description": "Solved 50 math problems correctly",
                "kinyarwanda": "Nyampinga w'imibare",
                "icon": "🧮",
                "requirement": {"type": "math_correct", "count": 50},
                "cultural_context": "Mathematics powers Rwanda's technological advancement"
            },
            "story_master": {
                "name": "Story Master",
                "description": "Completed 10 comprehension stories",
                "kinyarwanda": "Nyampinga w'inkuru",
                "icon": "📖",
                "requirement": {"type": "stories", "count": 10},
                "cultural_context": "Stories preserve our culture and wisdom"
            },
            "english_explorer": {
                "name": "English Explorer",
                "description": "Practiced English for 20 sessions",
                "kinyarwanda": "Ushakisha Icyongereza",
                "icon": "🌍",
                "requirement": {"type": "english_sessions", "count": 20},
                "cultural_context": "English connects Rwanda to the global community"
            },
            "resilience_warrior": {
                "name": "Resilience Warrior",
                "description": "Continued learning after 5 incorrect answers",
                "kinyarwanda": "Intore y'kwihangana",
                "icon": "💪",
                "requirement": {"type": "resilience", "count": 5},
                "cultural_context": "Like our ancestors, we grow stronger through challenges"
            }
        }
        
        self.badges = {
            "beginner": {"name": "Beginner", "icon": "🌱", "kinyarwanda": "Utangira"},
            "learner": {"name": "Learner", "icon": "📝", "kinyarwanda": "Umunyeshuri"},
            "achiever": {"name": "Achiever", "icon": "⭐", "kinyarwanda": "Umunyangamugayo"},
            "expert": {"name": "Expert", "icon": "🎓", "kinyarwanda": "Impuguke"},
            "master": {"name": "Master", "icon": "👑", "kinyarwanda": "Nyampinga"}
        }
        
        self.level_thresholds = {
            "beginner": 0,
            "learner": 100,
            "achiever": 500,
            "expert": 1500,
            "master": 3000
        }
    
    def calculate_user_level(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate user's current level and progress"""
        user_stats = user_context.get("user_state", {})
        
        total_points = self._calculate_total_points(user_stats)
        current_level = "beginner"
        
        for level, threshold in sorted(self.level_thresholds.items(), key=lambda x: x[1], reverse=True):
            if total_points >= threshold:
                current_level = level
                break
        
        next_level_info = self._get_next_level_info(current_level, total_points)
        
        return {
            "current_level": current_level,
            "total_points": total_points,
            "badge": self.badges[current_level],
            "next_level": next_level_info,
            "progress_percentage": self._calculate_progress_percentage(current_level, total_points)
        }
    
    def check_achievements(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for newly earned achievements"""
        user_stats = user_context.get("user_state", {})
        earned_achievements = user_stats.setdefault("earned_achievements", [])
        new_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in earned_achievements:
                if self._check_achievement_requirement(achievement, user_stats):
                    earned_achievements.append(achievement_id)
                    new_achievements.append({
                        "id": achievement_id,
                        "achievement": achievement,
                        "message": self._generate_achievement_message(achievement)
                    })
        
        return new_achievements
    
    def update_progress(self, user_context: Dict[str, Any], action_type: str, module_name: str, 
                       is_correct: bool = None, difficulty: str = None):
        """Update user progress and points"""
        user_stats = user_context.setdefault("user_state", {})
        
        points_earned = self._calculate_points_for_action(action_type, module_name, is_correct, difficulty)
        
        user_stats["total_points"] = user_stats.get("total_points", 0) + points_earned
        user_stats["last_activity"] = datetime.utcnow().isoformat()
        
        self._update_streaks(user_stats)
        self._update_module_stats(user_stats, action_type, module_name, is_correct)
        
        return points_earned
    
    def get_motivational_message(self, user_context: Dict[str, Any], context: str = "general") -> str:
        """Get culturally appropriate motivational message"""
        user_stats = user_context.get("user_state", {})
        level_info = self.calculate_user_level(user_context)
        current_level = level_info["current_level"]
        
        messages = {
            "beginner": [
                "Muraho! Welcome to your learning journey. Like a seed in Rwanda's fertile soil, you're just beginning to grow! 🌱",
                "Komera! Every expert was once a beginner. Rwanda's hills weren't climbed in a day! ⛰️",
                "Byiza! You're taking the first steps on a path that leads to great knowledge! 📚"
            ],
            "learner": [
                "Byiza cyane! You're growing like bamboo in Nyungwe Forest - strong and steady! 🎋",
                "Urashaka kwiga! Your dedication shows the true spirit of Rwanda's learners! 📝",
                "Komera! Like the morning mist over Lake Kivu, your knowledge is expanding beautifully! 🌅"
            ],
            "achiever": [
                "Urashobora! You're achieving great things, like the entrepreneurs in Kigali's innovation hubs! 🚀",
                "Byiza cyane! Your progress shines like the lights of modern Kigali! ✨",
                "Ubuntu! Your achievements inspire others in our learning community! 🤝"
            ],
            "expert": [
                "Impuguke! You've become an expert, like the skilled artisans of Rwanda! 🎨",
                "Urashobora byose! Your knowledge flows like the mighty Nile from our beautiful land! 🌊",
                "Byiza cyane! You're building expertise that will serve Rwanda's future! 🏗️"
            ],
            "master": [
                "Nyampinga! You've reached mastery, like the wise elders who guide our communities! 👑",
                "Urashobora byose! Your wisdom grows like the ancient trees of Nyungwe! 🌳",
                "Ubuntu! You're now ready to help others climb their own hills of knowledge! 🏔️"
            ]
        }
        
        level_messages = messages.get(current_level, messages["beginner"])
        import random
        return random.choice(level_messages)
    
    def get_streak_info(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get current streak information"""
        user_stats = user_context.get("user_state", {})
        
        current_streak = user_stats.get("current_streak", 0)
        longest_streak = user_stats.get("longest_streak", 0)
        last_activity = user_stats.get("last_activity")
        
        streak_status = "active"
        if last_activity:
            last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            days_since = (datetime.utcnow() - last_date).days
            if days_since > 1:
                streak_status = "broken"
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "status": streak_status,
            "message": self._get_streak_message(current_streak, streak_status)
        }
    
    def _calculate_total_points(self, user_stats: Dict[str, Any]) -> int:
        """Calculate total points from all activities"""
        return user_stats.get("total_points", 0)
    
    def _get_next_level_info(self, current_level: str, total_points: int) -> Dict[str, Any]:
        """Get information about next level"""
        levels = list(self.level_thresholds.keys())
        try:
            current_index = levels.index(current_level)
            if current_index < len(levels) - 1:
                next_level = levels[current_index + 1]
                next_threshold = self.level_thresholds[next_level]
                points_needed = next_threshold - total_points
                return {
                    "level": next_level,
                    "points_needed": points_needed,
                    "threshold": next_threshold,
                    "badge": self.badges[next_level]
                }
        except (ValueError, IndexError):
            pass
        
        return {"level": None, "points_needed": 0, "threshold": 0, "badge": None}
    
    def _calculate_progress_percentage(self, current_level: str, total_points: int) -> float:
        """Calculate progress percentage to next level"""
        current_threshold = self.level_thresholds[current_level]
        next_level_info = self._get_next_level_info(current_level, total_points)
        
        if not next_level_info["level"]:
            return 100.0
        
        next_threshold = next_level_info["threshold"]
        level_range = next_threshold - current_threshold
        progress_in_level = total_points - current_threshold
        
        return min(100.0, (progress_in_level / level_range) * 100) if level_range > 0 else 100.0
    
    def _check_achievement_requirement(self, achievement: Dict[str, Any], user_stats: Dict[str, Any]) -> bool:
        """Check if achievement requirement is met"""
        requirement = achievement["requirement"]
        req_type = requirement["type"]
        req_count = requirement["count"]
        
        if req_type == "sessions":
            return user_stats.get("total_sessions", 0) >= req_count
        elif req_type == "difficult_problems":
            return user_stats.get("difficult_problems_solved", 0) >= req_count
        elif req_type == "streak":
            return user_stats.get("longest_streak", 0) >= req_count
        elif req_type == "debates":
            return user_stats.get("debates_completed", 0) >= req_count
        elif req_type == "math_correct":
            return user_stats.get("math_problems_correct", 0) >= req_count
        elif req_type == "stories":
            return user_stats.get("comprehension_stories_completed", 0) >= req_count
        elif req_type == "english_sessions":
            return user_stats.get("english_sessions", 0) >= req_count
        elif req_type == "resilience":
            return user_stats.get("continued_after_wrong", 0) >= req_count
        
        return False
    
    def _generate_achievement_message(self, achievement: Dict[str, Any]) -> str:
        """Generate achievement unlock message"""
        return f"🎉 {achievement['icon']} {achievement['name']} ({achievement['kinyarwanda']}) unlocked!\n\n{achievement['description']}\n\n💭 {achievement['cultural_context']}"
    
    def _calculate_points_for_action(self, action_type: str, module_name: str, 
                                   is_correct: bool = None, difficulty: str = None) -> int:
        """Calculate points for specific action"""
        base_points = {
            "correct_answer": 10,
            "completed_story": 25,
            "completed_debate": 30,
            "session_complete": 15,
            "streak_day": 5
        }
        
        points = base_points.get(action_type, 5)
        
        if difficulty:
            difficulty_multipliers = {
                "basic": 1.0,
                "easy": 1.2,
                "medium": 1.5,
                "hard": 2.0,
                "complex": 2.5,
                "expert": 3.0
            }
            points = int(points * difficulty_multipliers.get(difficulty, 1.0))
        
        if is_correct is False:
            points = max(1, points // 3)
        
        return points
    
    def _update_streaks(self, user_stats: Dict[str, Any]):
        """Update streak information"""
        last_activity = user_stats.get("last_activity")
        current_streak = user_stats.get("current_streak", 0)
        
        if last_activity:
            last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00')).date()
            today = datetime.utcnow().date()
            days_diff = (today - last_date).days
            
            if days_diff == 1:
                current_streak += 1
            elif days_diff > 1:
                current_streak = 1
        else:
            current_streak = 1
        
        user_stats["current_streak"] = current_streak
        user_stats["longest_streak"] = max(user_stats.get("longest_streak", 0), current_streak)
    
    def _update_module_stats(self, user_stats: Dict[str, Any], action_type: str, 
                           module_name: str, is_correct: bool = None):
        """Update module-specific statistics"""
        user_stats["total_sessions"] = user_stats.get("total_sessions", 0) + 1
        
        if module_name == "math" and is_correct:
            user_stats["math_problems_correct"] = user_stats.get("math_problems_correct", 0) + 1
        elif module_name == "comprehension" and action_type == "completed_story":
            user_stats["comprehension_stories_completed"] = user_stats.get("comprehension_stories_completed", 0) + 1
        elif module_name == "debate" and action_type == "completed_debate":
            user_stats["debates_completed"] = user_stats.get("debates_completed", 0) + 1
        elif module_name == "english":
            user_stats["english_sessions"] = user_stats.get("english_sessions", 0) + 1
        
        if is_correct is False:
            user_stats["continued_after_wrong"] = user_stats.get("continued_after_wrong", 0) + 1
    
    def _get_streak_message(self, streak: int, status: str) -> str:
        """Get appropriate streak message"""
        if status == "broken":
            return "Your streak was broken, but every day is a new chance to start again! Komera! 💪"
        elif streak == 0:
            return "Start your learning streak today! Every journey begins with a single step! 🌱"
        elif streak < 3:
            return f"Great start! {streak} day streak. Keep climbing like Rwanda's hills! ⛰️"
        elif streak < 7:
            return f"Byiza cyane! {streak} day streak. You're building strong learning habits! 📚"
        elif streak < 14:
            return f"Incredible! {streak} day streak. Your dedication shines like Kigali's lights! ✨"
        else:
            return f"Amazing! {streak} day streak. You're a true knowledge seeker! Urashobora! 🏆"

gamification_service = GamificationService()
