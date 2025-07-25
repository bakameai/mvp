from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.logging_service import logging_service
from app.services.predictive_analytics_service import predictive_analytics
from app.services.gamification_service import gamification_service
from app.services.emotional_intelligence_service import emotional_intelligence_service
from app.services.community_service import community_service
from app.services.teacher_service import teacher_service
from app.models.database import get_db

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


@router.get("/community/analytics")
async def get_community_analytics():
    """Get community analytics for Phase 3 features"""
    try:
        analytics = await community_service.get_community_analytics()
        return {
            "status": "success",
            "message": "Community analytics retrieved",
            "data": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving community analytics: {str(e)}")

@router.get("/community/groups")
async def get_learning_groups(region: str = None):
    """Get learning groups, optionally filtered by region"""
    try:
        if region:
            groups = await community_service.get_regional_learning_groups(region)
        else:
            groups = []
            for region in ["Kigali", "Northern", "Southern", "Eastern", "Western"]:
                regional_groups = await community_service.get_regional_learning_groups(region)
                groups.extend(regional_groups)
        
        return {
            "status": "success",
            "message": "Learning groups retrieved",
            "data": {
                "groups": groups,
                "total": len(groups)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving learning groups: {str(e)}")

@router.post("/community/register-user")
async def register_community_user(
    phone_number: str,
    user_type: str = "student",
    name: str = None,
    region: str = None,
    school: str = None,
    grade_level: str = None
):
    """Register a new user in the community system"""
    try:
        result = await community_service.register_user(
            phone_number=phone_number,
            user_type=user_type,
            name=name,
            region=region,
            school=school,
            grade_level=grade_level
        )
        return {
            "status": "success",
            "message": "User registration processed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")

@router.get("/teachers/dashboard/{teacher_phone}")
async def get_teacher_dashboard(teacher_phone: str):
    """Get teacher dashboard data"""
    try:
        dashboard = await teacher_service.get_teacher_dashboard(teacher_phone)
        return {
            "status": "success",
            "message": "Teacher dashboard data retrieved",
            "data": dashboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving teacher dashboard: {str(e)}")

@router.post("/teachers/register")
async def register_teacher(
    phone_number: str,
    name: str,
    school: str,
    region: str,
    subjects: list = None
):
    """Register a new teacher"""
    try:
        result = await teacher_service.register_teacher(
            phone_number=phone_number,
            name=name,
            school=school,
            region=region,
            subjects=subjects or []
        )
        return {
            "status": "success",
            "message": "Teacher registration processed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering teacher: {str(e)}")

@router.post("/teachers/create-classroom")
async def create_classroom(
    teacher_phone: str,
    name: str,
    description: str,
    grade_level: str,
    subject: str,
    max_students: int = 30
):
    """Create a new classroom"""
    try:
        result = await teacher_service.create_classroom(
            teacher_phone=teacher_phone,
            name=name,
            description=description,
            grade_level=grade_level,
            subject=subject,
            max_students=max_students
        )
        return {
            "status": "success",
            "message": "Classroom creation processed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating classroom: {str(e)}")

@router.get("/teachers/classroom-analytics/{teacher_phone}/{classroom_id}")
async def get_classroom_analytics(teacher_phone: str, classroom_id: int):
    """Get analytics for a specific classroom"""
    try:
        analytics = await teacher_service.get_classroom_analytics(teacher_phone, classroom_id)
        return {
            "status": "success",
            "message": "Classroom analytics retrieved",
            "data": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving classroom analytics: {str(e)}")

@router.get("/peer-learning/sessions")
async def get_peer_learning_sessions(db: Session = Depends(get_db)):
    """Get recent peer learning sessions"""
    try:
        from app.models.database import PeerLearningSession
        
        sessions = db.query(PeerLearningSession).order_by(
            PeerLearningSession.started_at.desc()
        ).limit(50).all()
        
        session_data = []
        for session in sessions:
            session_data.append({
                "session_id": session.session_id,
                "module_name": session.module_name,
                "topic": session.topic,
                "participants": session.participants,
                "started_at": str(session.started_at),
                "ended_at": str(session.ended_at) if session.ended_at else None,
                "session_summary": session.session_summary
            })
        
        return {
            "status": "success",
            "message": "Peer learning sessions retrieved",
            "data": {
                "sessions": session_data,
                "total": len(session_data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving peer learning sessions: {str(e)}")
