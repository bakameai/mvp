from typing import Dict, Any, List
from datetime import datetime, timedelta
import statistics

class AdaptiveLearningService:
    def __init__(self):
        self.performance_weights = {
            "accuracy": 0.4,
            "response_time": 0.2,
            "engagement": 0.2,
            "consistency": 0.2
        }
    
    def calculate_adaptive_difficulty(self, user_context: Dict[str, Any], module_name: str) -> str:
        """Calculate optimal difficulty level based on comprehensive performance analysis"""
        
        user_stats = user_context.get("user_state", {})
        performance_data = user_stats.get(f"{module_name}_performance", [])
        
        if len(performance_data) < 3:
            return "basic"
        
        recent_performance = performance_data[-10:]
        
        accuracy_score = self._calculate_accuracy_score(recent_performance)
        engagement_score = self._calculate_engagement_score(recent_performance)
        consistency_score = self._calculate_consistency_score(recent_performance)
        
        overall_score = (
            accuracy_score * self.performance_weights["accuracy"] +
            engagement_score * self.performance_weights["engagement"] +
            consistency_score * self.performance_weights["consistency"]
        )
        
        if overall_score >= 0.85:
            return self._get_next_level(user_stats.get(f"{module_name}_level", "basic"))
        elif overall_score >= 0.7:
            return user_stats.get(f"{module_name}_level", "basic")
        else:
            return self._get_previous_level(user_stats.get(f"{module_name}_level", "basic"))
    
    def record_interaction(self, user_context: Dict[str, Any], module_name: str, 
                         is_correct: bool, response_time: float = None, engagement_indicators: Dict = None):
        """Record interaction data for adaptive learning"""
        
        user_stats = user_context.setdefault("user_state", {})
        performance_key = f"{module_name}_performance"
        
        if performance_key not in user_stats:
            user_stats[performance_key] = []
        
        interaction_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "correct": is_correct,
            "response_time": response_time,
            "engagement": engagement_indicators or {}
        }
        
        user_stats[performance_key].append(interaction_data)
        
        if len(user_stats[performance_key]) > 50:
            user_stats[performance_key] = user_stats[performance_key][-50:]
    
    def _calculate_accuracy_score(self, performance_data: List[Dict]) -> float:
        """Calculate accuracy score from recent performance"""
        if not performance_data:
            return 0.5
        
        correct_count = sum(1 for p in performance_data if p.get("correct", False))
        return correct_count / len(performance_data)
    
    def _calculate_engagement_score(self, performance_data: List[Dict]) -> float:
        """Calculate engagement score based on response patterns"""
        if not performance_data:
            return 0.5
        
        response_times = [p.get("response_time", 30) for p in performance_data if p.get("response_time")]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            if 10 <= avg_response_time <= 30:
                time_score = 1.0
            elif avg_response_time < 10:
                time_score = 0.7
            else:
                time_score = max(0.3, 1.0 - (avg_response_time - 30) / 60)
        else:
            time_score = 0.5
        
        return time_score
    
    def _calculate_consistency_score(self, performance_data: List[Dict]) -> float:
        """Calculate consistency score based on performance stability"""
        if len(performance_data) < 5:
            return 0.5
        
        accuracies = [p.get("correct", False) for p in performance_data]
        
        window_size = min(5, len(accuracies))
        window_accuracies = []
        
        for i in range(len(accuracies) - window_size + 1):
            window = accuracies[i:i + window_size]
            window_accuracy = sum(window) / len(window)
            window_accuracies.append(window_accuracy)
        
        if len(window_accuracies) > 1:
            variance = statistics.variance(window_accuracies)
            consistency = max(0, 1 - variance * 2)
        else:
            consistency = 0.5
        
        return consistency
    
    def _get_next_level(self, current_level: str) -> str:
        """Get next difficulty level"""
        levels = ["basic", "easy", "medium", "hard", "complex", "expert"]
        try:
            current_index = levels.index(current_level)
            return levels[min(current_index + 1, len(levels) - 1)]
        except ValueError:
            return "basic"
    
    def _get_previous_level(self, current_level: str) -> str:
        """Get previous difficulty level"""
        levels = ["basic", "easy", "medium", "hard", "complex", "expert"]
        try:
            current_index = levels.index(current_level)
            return levels[max(current_index - 1, 0)]
        except ValueError:
            return "basic"

adaptive_learning_service = AdaptiveLearningService()
