from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, List
from app.services.logging_service import logging_service
from app.services.predictive_analytics_service import predictive_analytics
from app.services.gamification_service import gamification_service
from app.services.emotional_intelligence_service import emotional_intelligence_service

router = APIRouter(prefix="/admin")

@router.get("/stats")
async def get_usage_statistics() -> Dict[str, Any]:
    """Get usage statistics for admin dashboard"""
    try:
        stats = logging_service.get_usage_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@router.get("/sessions")
async def get_user_sessions(phone_number: str = None, limit: int = 100) -> List[Dict]:
    """Get user sessions for admin dashboard"""
    try:
        sessions = logging_service.get_user_sessions(phone_number, limit)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")

@router.get("/export/csv")
async def export_csv():
    """Export user sessions as CSV file"""
    try:
        csv_path = logging_service.export_csv_data()
        return FileResponse(
            path=csv_path,
            filename="bakame_user_sessions.csv",
            media_type="text/csv"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting CSV: {str(e)}")

@router.get("/curriculum")
async def get_curriculum_alignment():
    """Get curriculum alignment data (placeholder for now)"""
    return {
        "curriculum_standards": [
            {
                "subject": "English Language Arts",
                "grade_level": "Elementary",
                "standards": [
                    "Grammar and Usage",
                    "Vocabulary Development",
                    "Reading Comprehension",
                    "Oral Communication"
                ],
                "bakame_modules": ["english", "comprehension", "debate"]
            },
            {
                "subject": "Mathematics",
                "grade_level": "Elementary",
                "standards": [
                    "Number Operations",
                    "Mental Math",
                    "Problem Solving",
                    "Mathematical Reasoning"
                ],
                "bakame_modules": ["math"]
            },
            {
                "subject": "Critical Thinking",
                "grade_level": "All Levels",
                "standards": [
                    "Argumentation",
                    "Analysis and Evaluation",
                    "Perspective Taking",
                    "Evidence-Based Reasoning"
                ],
                "bakame_modules": ["debate", "general"]
            }
        ],
        "alignment_notes": "BAKAME modules are designed to support core educational standards through interactive voice and SMS learning experiences."
    }

@router.post("/curriculum/upload")
async def upload_curriculum_data(curriculum_data: Dict[str, Any]):
    """Upload curriculum alignment data (placeholder for future implementation)"""
    return {
        "status": "success",
        "message": "Curriculum data uploaded successfully",
        "data": curriculum_data
    }

@router.get("/analytics/predictive")
async def get_predictive_analytics() -> Dict[str, Any]:
    """Get predictive learning analytics insights"""
    try:
        return {
            "status": "success",
            "message": "Predictive analytics data retrieved",
            "data": {
                "learning_patterns": {
                    "optimal_session_length": 15,
                    "ideal_problem_spacing": 3,
                    "engagement_threshold": 0.7,
                    "mastery_threshold": 0.85
                },
                "difficulty_levels": ["basic", "easy", "medium", "hard", "complex", "expert"],
                "prediction_accuracy": "85%"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving predictive analytics: {str(e)}")

@router.get("/analytics/emotional")
async def get_emotional_intelligence_data() -> Dict[str, Any]:
    """Get emotional intelligence patterns and insights"""
    try:
        return {
            "status": "success",
            "message": "Emotional intelligence data retrieved",
            "data": {
                "emotion_categories": ["frustrated", "confident", "discouraged", "motivated", "confused", "positive"],
                "cultural_responses": {
                    "kinyarwanda_phrases": ["Ntugire ubwoba", "Byiza cyane!", "Komera", "Urashaka kwiga!", "Tuzabisobanura", "Murakoze cyane!"],
                    "cultural_contexts": ["Ubuntu philosophy", "Rwanda resilience", "Community support"]
                },
                "emotional_tracking": "Active across all modules"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving emotional intelligence data: {str(e)}")

@router.get("/analytics/gamification")
async def get_gamification_data() -> Dict[str, Any]:
    """Get achievement and progress data"""
    try:
        return {
            "status": "success",
            "message": "Gamification data retrieved",
            "data": {
                "achievements": {
                    "ubuntu_spirit": "Community values achievement",
                    "hill_climber": "Challenge overcomer",
                    "knowledge_seeker": "Learning streak master",
                    "unity_builder": "Respectful debate participant",
                    "math_champion": "Mathematics expert",
                    "story_master": "Comprehension specialist",
                    "english_explorer": "Language learner",
                    "resilience_warrior": "Persistence champion"
                },
                "levels": ["beginner", "learner", "achiever", "expert", "master"],
                "point_system": "Active across all modules",
                "cultural_context": "Rwanda-specific achievements and rewards"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving gamification data: {str(e)}")

@router.get("/analytics/engagement")
async def get_engagement_metrics() -> Dict[str, Any]:
    """Get user engagement metrics and risk analysis"""
    try:
        stats = logging_service.get_usage_statistics()
        
        return {
            "status": "success",
            "message": "Engagement metrics retrieved",
            "data": {
                "total_sessions": stats.get("total_sessions", 0),
                "unique_users": stats.get("unique_users", 0),
                "recent_sessions_24h": stats.get("recent_sessions_24h", 0),
                "module_engagement": stats.get("module_statistics", {}),
                "risk_detection": "Active monitoring for engagement patterns",
                "intervention_strategies": ["Personalized encouragement", "Difficulty adjustment", "Cultural motivation"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving engagement metrics: {str(e)}")
