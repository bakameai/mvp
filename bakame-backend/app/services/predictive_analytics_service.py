from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import statistics
from app.services.redis_service import redis_service

class PredictiveLearningAnalytics:
    def __init__(self):
        self.learning_patterns = {
            "optimal_session_length": 15,  # minutes
            "ideal_problem_spacing": 3,    # problems between difficulty increases
            "engagement_threshold": 0.7,   # minimum engagement score
            "mastery_threshold": 0.85      # accuracy needed for mastery
        }
    
    def predict_optimal_difficulty(self, user_context: Dict[str, Any], module_name: str) -> str:
        """Predict optimal difficulty level for next problem"""
        
        user_stats = user_context.get("user_state", {})
        performance_data = user_stats.get(f"{module_name}_performance", [])
        
        if len(performance_data) < 5:
            return "basic"
        
        recent_performance = performance_data[-10:]
        accuracy_trend = self._calculate_accuracy_trend(recent_performance)
        engagement_score = self._calculate_engagement_score(recent_performance)
        consistency_score = self._calculate_consistency_score(recent_performance)
        
        current_level = user_stats.get(f"{module_name}_level", "basic")
        
        if accuracy_trend >= 0.9 and engagement_score >= 0.8 and consistency_score >= 0.7:
            return self._increase_difficulty(current_level)
        elif accuracy_trend <= 0.5 or engagement_score <= 0.4:
            return self._decrease_difficulty(current_level)
        else:
            return current_level
    
    def predict_learning_path(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict personalized learning path for user"""
        
        user_stats = user_context.get("user_state", {})
        
        module_scores = {}
        for module in ["math", "english", "comprehension", "debate"]:
            performance = user_stats.get(f"{module}_performance", [])
            if performance:
                recent_accuracy = self._calculate_recent_accuracy(performance)
                engagement = self._calculate_engagement_score(performance)
                module_scores[module] = {
                    "accuracy": recent_accuracy,
                    "engagement": engagement,
                    "sessions": len(performance),
                    "strength_level": self._assess_strength_level(recent_accuracy, engagement)
                }
        
        strengths = []
        needs_work = []
        
        for module, scores in module_scores.items():
            if scores["strength_level"] >= 0.8:
                strengths.append(module)
            elif scores["strength_level"] <= 0.5:
                needs_work.append(module)
        
        recommendations = self._generate_learning_recommendations(module_scores, user_stats)
        
        return {
            "strengths": strengths,
            "areas_for_improvement": needs_work,
            "module_scores": module_scores,
            "recommendations": recommendations,
            "predicted_next_session": self._predict_next_session_focus(module_scores)
        }
    
    def predict_engagement_risk(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict if user is at risk of disengagement"""
        
        user_stats = user_context.get("user_state", {})
        conversation_history = user_context.get("conversation_history", [])
        
        recent_sessions = len(conversation_history)
        session_frequency = self._calculate_session_frequency(conversation_history)
        response_patterns = self._analyze_response_patterns(conversation_history)
        
        risk_factors = []
        risk_score = 0.0
        
        if session_frequency < 0.3:  # Less than 3 sessions per 10 days
            risk_factors.append("infrequent_sessions")
            risk_score += 0.3
        
        if response_patterns.get("avg_response_length", 0) < 5:
            risk_factors.append("short_responses")
            risk_score += 0.2
        
        overall_accuracy = self._calculate_overall_accuracy(user_stats)
        if overall_accuracy < 0.4:
            risk_factors.append("low_performance")
            risk_score += 0.3
        
        if risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        interventions = self._generate_intervention_strategies(risk_factors, user_stats)
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "interventions": interventions,
            "engagement_tips": self._get_engagement_tips(risk_level)
        }
    
    def _calculate_accuracy_trend(self, performance_data: List[Dict]) -> float:
        """Calculate accuracy trend from recent performance"""
        if len(performance_data) < 3:
            return 0.5
        
        accuracies = [1.0 if p.get("correct", False) else 0.0 for p in performance_data]
        
        n = len(accuracies)
        x_values = list(range(n))
        
        if n > 1:
            slope = (n * sum(i * acc for i, acc in enumerate(accuracies)) - 
                    sum(x_values) * sum(accuracies)) / (n * sum(x * x for x in x_values) - sum(x_values) ** 2)
            return max(0.0, min(1.0, statistics.mean(accuracies) + slope))
        
        return statistics.mean(accuracies)
    
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
                time_score = 0.7  # Too fast
            else:
                time_score = max(0.3, 1.0 - (avg_response_time - 30) / 60)
        else:
            time_score = 0.5
        
        return time_score
    
    def _calculate_consistency_score(self, performance_data: List[Dict]) -> float:
        """Calculate consistency in performance"""
        if len(performance_data) < 3:
            return 0.5
        
        accuracies = [1.0 if p.get("correct", False) else 0.0 for p in performance_data]
        
        if len(set(accuracies)) == 1:  # All same
            return 1.0
        
        variance = statistics.variance(accuracies)
        consistency = max(0.0, 1.0 - variance * 2)
        return consistency
    
    def _increase_difficulty(self, current_level: str) -> str:
        """Increase difficulty level"""
        levels = ["basic", "easy", "medium", "hard", "complex", "expert"]
        try:
            current_index = levels.index(current_level)
            return levels[min(current_index + 1, len(levels) - 1)]
        except ValueError:
            return "basic"
    
    def _decrease_difficulty(self, current_level: str) -> str:
        """Decrease difficulty level"""
        levels = ["basic", "easy", "medium", "hard", "complex", "expert"]
        try:
            current_index = levels.index(current_level)
            return levels[max(current_index - 1, 0)]
        except ValueError:
            return "basic"
    
    def _calculate_recent_accuracy(self, performance_data: List[Dict]) -> float:
        """Calculate recent accuracy score"""
        if not performance_data:
            return 0.0
        
        recent = performance_data[-5:]  # Last 5 interactions
        correct_count = sum(1 for p in recent if p.get("correct", False))
        return correct_count / len(recent)
    
    def _assess_strength_level(self, accuracy: float, engagement: float) -> float:
        """Assess overall strength level for a module"""
        return (accuracy * 0.7) + (engagement * 0.3)
    
    def _generate_learning_recommendations(self, module_scores: Dict, user_stats: Dict) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        if module_scores:
            weakest_module = min(module_scores.keys(), 
                               key=lambda m: module_scores[m]["strength_level"])
            recommendations.append(f"Focus on {weakest_module} - your accuracy is {module_scores[weakest_module]['accuracy']:.1%}")
        
        total_sessions = sum(scores.get("sessions", 0) for scores in module_scores.values())
        if total_sessions < 10:
            recommendations.append("Try to practice for 10-15 minutes daily for better retention")
        
        for module, scores in module_scores.items():
            if scores["accuracy"] < 0.6:
                if module == "math":
                    recommendations.append("For math: Start with basic arithmetic and gradually increase difficulty")
                elif module == "english":
                    recommendations.append("For English: Focus on grammar basics and vocabulary building")
                elif module == "comprehension":
                    recommendations.append("For reading: Practice with shorter stories first")
                elif module == "debate":
                    recommendations.append("For debate: Start with familiar topics from Rwanda")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _predict_next_session_focus(self, module_scores: Dict) -> str:
        """Predict what the user should focus on next session"""
        if not module_scores:
            return "general"
        
        best_candidate = None
        best_score = -1
        
        for module, scores in module_scores.items():
            need_score = 1.0 - scores["accuracy"]  # Higher need = lower accuracy
            engagement_factor = scores["engagement"]
            combined_score = need_score * engagement_factor
            
            if combined_score > best_score:
                best_score = combined_score
                best_candidate = module
        
        return best_candidate or "general"
    
    def _calculate_session_frequency(self, conversation_history: List[Dict]) -> float:
        """Calculate how frequently user has sessions"""
        if len(conversation_history) < 2:
            return 0.0
        
        recent_sessions = conversation_history[-10:]  # Last 10 interactions
        return len(recent_sessions) / 10.0  # Normalize to 0-1 scale
    
    def _analyze_response_patterns(self, conversation_history: List[Dict]) -> Dict:
        """Analyze user response patterns"""
        if not conversation_history:
            return {"avg_response_length": 0}
        
        response_lengths = []
        for interaction in conversation_history[-10:]:
            user_response = interaction.get("user", "")
            response_lengths.append(len(user_response.split()))
        
        return {
            "avg_response_length": statistics.mean(response_lengths) if response_lengths else 0,
            "total_interactions": len(conversation_history)
        }
    
    def _calculate_overall_accuracy(self, user_stats: Dict) -> float:
        """Calculate overall accuracy across all modules"""
        total_correct = 0
        total_attempts = 0
        
        for module in ["math", "english", "comprehension", "debate"]:
            performance = user_stats.get(f"{module}_performance", [])
            for p in performance:
                total_attempts += 1
                if p.get("correct", False):
                    total_correct += 1
        
        return total_correct / total_attempts if total_attempts > 0 else 0.0
    
    def _generate_intervention_strategies(self, risk_factors: List[str], user_stats: Dict) -> List[str]:
        """Generate intervention strategies based on risk factors"""
        interventions = []
        
        if "infrequent_sessions" in risk_factors:
            interventions.append("Send encouraging reminders about daily practice")
            interventions.append("Suggest shorter 5-minute practice sessions")
        
        if "short_responses" in risk_factors:
            interventions.append("Ask more engaging, open-ended questions")
            interventions.append("Use Rwanda-specific examples that relate to user's interests")
        
        if "low_performance" in risk_factors:
            interventions.append("Reduce difficulty level temporarily")
            interventions.append("Provide more positive reinforcement and encouragement")
            interventions.append("Focus on building confidence with easier problems")
        
        return interventions
    
    def _get_engagement_tips(self, risk_level: str) -> List[str]:
        """Get engagement tips based on risk level"""
        if risk_level == "high":
            return [
                "Take breaks between learning sessions",
                "Celebrate small wins and progress",
                "Connect learning to personal goals",
                "Try different modules to find what you enjoy most"
            ]
        elif risk_level == "medium":
            return [
                "Set small daily learning goals",
                "Track your progress to see improvement",
                "Mix different types of problems for variety"
            ]
        else:
            return [
                "Keep up the great work!",
                "Challenge yourself with harder problems",
                "Help others learn to reinforce your knowledge"
            ]

predictive_analytics = PredictiveLearningAnalytics()
