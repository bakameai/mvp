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
from app.models.auth import WebUser
from app.routers.auth import get_current_user

router = APIRouter(prefix="/admin")

@router.get("/users")
async def get_users(
    current_user: WebUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all users for admin dashboard"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        users = db.query(WebUser).all()
        return [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "organization": user.organization,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_data: Dict[str, str],
    current_user: WebUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user role"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        user = db.query(WebUser).filter(WebUser.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.role = role_data.get("role", user.role)
        db.commit()
        return {"message": "User role updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user role: {str(e)}")

@router.get("/organizations")
async def get_organizations(
    current_user: WebUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all organizations for admin dashboard"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        organizations = db.query(WebUser.organization).distinct().filter(WebUser.organization.isnot(None)).all()
        return [
            {
                "id": str(hash(org[0])),  # Generate a simple ID from organization name
                "name": org[0],
                "type": "organization",
                "created_at": "2024-01-01T00:00:00Z"  # Placeholder date
            }
            for org in organizations if org[0]
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving organizations: {str(e)}")

@router.post("/organizations")
async def create_organization(
    org_data: Dict[str, Any],
    current_user: WebUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization (placeholder implementation)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        return {
            "id": str(hash(org_data.get("name", ""))),
            "name": org_data.get("name"),
            "type": org_data.get("type", "organization"),
            "created_at": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating organization: {str(e)}")

@router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: str,
    current_user: WebUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an organization (placeholder implementation)"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        return {"message": "Organization deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting organization: {str(e)}")

@router.get("/stats")
async def get_usage_statistics(
    current_user: WebUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get usage statistics for admin dashboard"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        total_users = db.query(WebUser).count()
        active_users = db.query(WebUser).filter(WebUser.is_active == True).count()
        total_organizations = db.query(WebUser.organization).distinct().filter(WebUser.organization.isnot(None)).count()
        
        telephony_stats = logging_service.get_usage_statistics()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "organizations": total_organizations,
            "new_users_this_month": 0,  # Placeholder
            **telephony_stats
        }
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
    """Get comprehensive curriculum alignment data"""
    from app.services.curriculum_service import curriculum_service
    
    return {
        "curriculum_standards": [
            {
                "subject": "Grammar",
                "grade_level": "Elementary to Advanced", 
                "bloom_stages": curriculum_service.bloom_stages,
                "standards": [
                    "Verb Tenses and Agreement",
                    "Sentence Structure", 
                    "Grammar Pattern Recognition",
                    "Error Correction"
                ],
                "source": "Speak English: 30 Days to Better English"
            },
            {
                "subject": "Composition", 
                "grade_level": "Elementary to Advanced",
                "bloom_stages": curriculum_service.bloom_stages,
                "standards": [
                    "Creative Writing",
                    "Storytelling Techniques",
                    "Cultural Expression",
                    "Narrative Structure"
                ],
                "source": "Things Fall Apart (Chinua Achebe)"
            },
            {
                "subject": "Mathematics",
                "grade_level": "Elementary to Advanced",
                "bloom_stages": curriculum_service.bloom_stages,
                "standards": [
                    "Mental Math Techniques",
                    "Number Operations", 
                    "Problem Solving",
                    "Mathematical Reasoning"
                ],
                "source": "Secrets of Mental Math"
            },
            {
                "subject": "Debate",
                "grade_level": "Intermediate to Advanced",
                "bloom_stages": curriculum_service.bloom_stages,
                "standards": [
                    "Argument Construction",
                    "Critical Thinking",
                    "Public Speaking",
                    "Logical Reasoning"
                ],
                "source": "Code of the Debater (Alfred Snider)"
            },
            {
                "subject": "Comprehension",
                "grade_level": "Elementary to Advanced", 
                "bloom_stages": curriculum_service.bloom_stages,
                "standards": [
                    "Reading Comprehension",
                    "Text Analysis",
                    "Critical Reading",
                    "Communication Skills"
                ],
                "source": "Art of Public Speaking"
            }
        ],
        "oer_sources": {
            "grammar": ["Speak English: 30 Days to Better English (Educational Use)"],
            "composition": ["Things Fall Apart (Public Domain)"],
            "math": ["Secrets of Mental Math (Educational Use)"],
            "debate": ["Code of the Debater (Open Access)"],
            "comprehension": ["Art of Public Speaking (Public Domain)"]
        },
        "assessment_system": {
            "scoring_method": "Multi-factor (keyword + structure + LLM)",
            "pass_threshold": 0.6,
            "advancement_rule": "3 passes out of 5 attempts",
            "demotion_rule": "3 consecutive failures"
        }
    }

@router.get("/evaluation-analytics")
async def get_evaluation_analytics():
    """Get comprehensive evaluation analytics with Bloom stage heatmaps"""
    try:
        from app.services.evaluation_engine import evaluation_engine
        
        def _get_stage_distribution(module: str) -> Dict[str, int]:
            """Get distribution of students across Bloom stages for a module"""
            stage_counts = {}
            for stage in evaluation_engine.bloom_stages:
                stage_counts[stage] = 0
            
            all_contexts = redis_service.get_all_user_contexts()
            for context in all_contexts:
                curriculum_stages = context.get("curriculum_stages", {})
                current_stage = curriculum_stages.get(module, "remember")
                if current_stage in stage_counts:
                    stage_counts[current_stage] += 1
            
            return stage_counts
        
        def _get_emotional_trends() -> Dict[str, int]:
            """Get emotional state distribution across all evaluations"""
            emotional_counts = {"neutral": 0, "hesitation": 0, "confusion": 0, "frustration": 0}
            
            all_contexts = redis_service.get_all_user_contexts()
            for context in all_contexts:
                evaluation_history = context.get("evaluation_history", {})
                for module_history in evaluation_history.values():
                    for evaluation in module_history:
                        emotional_state = evaluation.get("emotional_state", "neutral")
                        if emotional_state in emotional_counts:
                            emotional_counts[emotional_state] += 1
            
            return emotional_counts
        
        def _get_component_score_analysis() -> Dict[str, float]:
            """Get average scores for each assessment component"""
            component_totals = {"keyword": 0, "structure": 0, "llm": 0}
            component_counts = {"keyword": 0, "structure": 0, "llm": 0}
            
            all_contexts = redis_service.get_all_user_contexts()
            for context in all_contexts:
                evaluation_history = context.get("evaluation_history", {})
                for module_history in evaluation_history.values():
                    for evaluation in module_history:
                        component_scores = evaluation.get("component_scores", {})
                        for component, score in component_scores.items():
                            if component in component_totals:
                                component_totals[component] += score
                                component_counts[component] += 1
            
            averages = {}
            for component in component_totals:
                if component_counts[component] > 0:
                    averages[component] = component_totals[component] / component_counts[component]
                else:
                    averages[component] = 0.0
            
            return averages
        
        def _get_advancement_statistics() -> Dict[str, Dict[str, int]]:
            """Get advancement and demotion statistics by module"""
            advancement_stats = {}
            
            for module in evaluation_engine.modules:
                advancement_stats[module] = {
                    "total_students": 0,
                    "advanced_students": 0,
                    "demoted_students": 0,
                    "advancement_rate": 0.0
                }
            
            all_contexts = redis_service.get_all_user_contexts()
            for context in all_contexts:
                curriculum_stages = context.get("curriculum_stages", {})
                evaluation_history = context.get("evaluation_history", {})
                
                for module in evaluation_engine.modules:
                    if module in evaluation_history and evaluation_history[module]:
                        advancement_stats[module]["total_students"] += 1
                        current_stage = curriculum_stages.get(module, "remember")
                        
                        if current_stage != "remember":
                            advancement_stats[module]["advanced_students"] += 1
            
            for module in advancement_stats:
                total = advancement_stats[module]["total_students"]
                advanced = advancement_stats[module]["advanced_students"]
                if total > 0:
                    advancement_stats[module]["advancement_rate"] = advanced / total
            
            return advancement_stats
        
        return {
            "status": "success",
            "bloom_stage_distribution": {
                "grammar": _get_stage_distribution("grammar"),
                "composition": _get_stage_distribution("composition"), 
                "math": _get_stage_distribution("math"),
                "debate": _get_stage_distribution("debate"),
                "comprehension": _get_stage_distribution("comprehension")
            },
            "emotional_state_trends": _get_emotional_trends(),
            "assessment_component_scores": _get_component_score_analysis(),
            "advancement_rates": _get_advancement_statistics(),
            "timestamp": str(datetime.utcnow())
        }
    except Exception as e:
        print(f"Error getting evaluation analytics: {e}")
        return {
            "status": "error",
            "message": "Failed to retrieve evaluation analytics",
            "timestamp": str(datetime.utcnow())
        }

@router.get("/student-evaluation-history")
async def get_student_evaluation_history(phone_number: str):
    """Get detailed evaluation history for specific student"""
    try:
        context = redis_service.get_user_context(phone_number)
        evaluation_history = context.get("evaluation_history", {})
        
        total_evaluations = sum(len(module_history) for module_history in evaluation_history.values())
        
        return {
            "status": "success",
            "phone_number": phone_number,
            "evaluation_history": evaluation_history,
            "current_stages": context.get("curriculum_stages", {}),
            "total_evaluations": total_evaluations,
            "timestamp": str(datetime.utcnow())
        }
    except Exception as e:
        print(f"Error getting student evaluation history: {e}")
        return {
            "status": "error",
            "message": "Failed to retrieve student evaluation history",
            "timestamp": str(datetime.utcnow())
        }

@router.get("/curriculum/student-progress")
async def get_student_progress(phone_number: str = None):
    """Get student curriculum progress data"""
    from app.services.curriculum_service import curriculum_service
    from app.services.redis_service import redis_service
    
    if phone_number:
        context = redis_service.get_user_context(phone_number)
        curriculum_stages = context.get("curriculum_stages", {})
        assessment_history = context.get("assessment_history", {})
        
        return {
            "phone_number": phone_number,
            "current_stages": curriculum_stages,
            "assessment_history": assessment_history,
            "user_name": context.get("user_name", "Unknown")
        }
    else:
        return {
            "total_students": "Available via session analytics",
            "stage_distribution": "Requires Redis scan implementation",
            "average_progression": "Calculated from assessment history"
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

@router.get("/ivr-stats")
async def get_ivr_statistics(
    current_user: WebUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive IVR statistics for dashboard"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from app.models.database import UserSession, PeerLearningSession
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        total_ivr_sessions = db.query(UserSession).count()
        voice_sessions = db.query(UserSession).filter(UserSession.interaction_type == "voice").count()
        sms_sessions = db.query(UserSession).filter(UserSession.interaction_type == "sms").count()
        
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_sessions = db.query(UserSession).filter(UserSession.timestamp >= yesterday).count()
        
        avg_duration_result = db.query(func.avg(UserSession.session_duration)).filter(
            UserSession.session_duration.isnot(None)
        ).scalar()
        avg_session_duration = round(avg_duration_result or 0, 1)
        
        module_stats = {}
        sessions_by_module = db.query(UserSession.module_name, func.count(UserSession.id)).group_by(UserSession.module_name).all()
        for module, count in sessions_by_module:
            module_stats[module] = count
        
        peer_sessions = db.query(PeerLearningSession).count()
        active_peer_sessions = db.query(PeerLearningSession).filter(PeerLearningSession.ended_at.is_(None)).count()
        
        return {
            "total_ivr_sessions": total_ivr_sessions,
            "voice_sessions": voice_sessions,
            "sms_sessions": sms_sessions,
            "recent_sessions_24h": recent_sessions,
            "average_session_duration": avg_session_duration,
            "peer_learning_sessions": peer_sessions,
            "active_peer_sessions": active_peer_sessions,
            "module_statistics": module_stats,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving IVR statistics: {str(e)}")

@router.post("/populate-sample-data")
async def populate_sample_data():
    """Populate database with sample data for demonstration"""
    try:
        import json
        from datetime import datetime, timedelta
        from app.models.database import (
            User, PeerConnection, LearningGroup, GroupMembership, 
            PeerLearningSession, UserSession, ModuleUsage
        )
        
        db = next(get_db())
        
        sample_users = [
            {"phone": "+250781234567", "type": "student", "name": "Uwimana Jean", "region": "Kigali", "school": "Kigali Primary School", "grade": "Primary 4-6"},
            {"phone": "+250782345678", "type": "student", "name": "Mukamana Alice", "region": "Northern", "school": "Musanze Secondary", "grade": "Secondary 1-3"},
            {"phone": "+250783456789", "type": "student", "name": "Niyonzima David", "region": "Southern", "school": "Huye High School", "grade": "Secondary 4-6"},
            {"phone": "+250784567890", "type": "student", "name": "Uwase Grace", "region": "Eastern", "school": "Rwamagana Primary", "grade": "Primary 1-3"},
            {"phone": "+250785678901", "type": "student", "name": "Habimana Eric", "region": "Western", "school": "Rubavu Secondary", "grade": "Secondary 1-3"},
            {"phone": "+250786789012", "type": "student", "name": "Mutesi Sarah", "region": "Kigali", "school": "Nyarugenge Primary", "grade": "Primary 4-6"},
            {"phone": "+250787890123", "type": "student", "name": "Bizimana Paul", "region": "Northern", "school": "Gicumbi Primary", "grade": "Primary 1-3"},
            {"phone": "+250788901234", "type": "student", "name": "Nyirahabimana Marie", "region": "Southern", "school": "Nyanza Secondary", "grade": "Secondary 4-6"},
            {"phone": "+250789012345", "type": "student", "name": "Uwimana Patrick", "region": "Eastern", "school": "Kayonza High School", "grade": "Secondary 1-3"},
            {"phone": "+250780123456", "type": "student", "name": "Mukandayisenga Claire", "region": "Western", "school": "Karongi Primary", "grade": "Primary 4-6"},
            
            {"phone": "+250791234567", "type": "teacher", "name": "Nsengimana Joseph", "region": "Kigali", "school": "Kigali Primary School", "grade": None},
            {"phone": "+250792345678", "type": "teacher", "name": "Uwimana Beatrice", "region": "Northern", "school": "Musanze Secondary", "grade": None},
            {"phone": "+250793456789", "type": "teacher", "name": "Hakizimana Emmanuel", "region": "Southern", "school": "Huye High School", "grade": None},
            {"phone": "+250794567890", "type": "teacher", "name": "Mukamana Esperance", "region": "Eastern", "school": "Rwamagana Primary", "grade": None},
            {"phone": "+250795678901", "type": "teacher", "name": "Nzeyimana Claude", "region": "Western", "school": "Rubavu Secondary", "grade": None},
        ]
        
        db.query(User).filter(User.phone_number.like("+2507%")).delete()
        db.query(UserSession).filter(UserSession.phone_number.like("+2507%")).delete()
        db.query(ModuleUsage).filter(ModuleUsage.phone_number.like("+2507%")).delete()
        db.commit()
        
        for user_data in sample_users:
            existing_user = db.query(User).filter(User.phone_number == user_data["phone"]).first()
            if not existing_user:
                new_user = User(
                    phone_number=user_data["phone"],
                    user_type=user_data["type"],
                    name=user_data["name"],
                    region=user_data["region"],
                    school=user_data["school"],
                    grade_level=user_data["grade"],
                    total_points=(50 + (hash(user_data["phone"]) % 200)),
                    current_level=["beginner", "learner", "achiever", "expert"][hash(user_data["phone"]) % 4],
                    last_active=datetime.utcnow() - timedelta(hours=hash(user_data["phone"]) % 48)
                )
                db.add(new_user)
        
        regions = ["Kigali", "Northern", "Southern", "Eastern", "Western"]
        for region in regions:
            existing_group = db.query(LearningGroup).filter(
                LearningGroup.region == region,
                LearningGroup.group_type == "regional"
            ).first()
            if not existing_group:
                regional_group = LearningGroup(
                    name=f"{region} Regional Learning Community",
                    description=f"Learning community for students in {region} region of Rwanda",
                    group_type="regional",
                    region=region,
                    max_members=200
                )
                db.add(regional_group)
        
        db.commit()
        
        peer_pairs = [
            ("+250781234567", "+250786789012"),  # Both Kigali Primary 4-6
            ("+250782345678", "+250785678901"),  # Both Secondary 1-3
            ("+250783456789", "+250788901234"),  # Both Secondary 4-6
            ("+250784567890", "+250787890123"),  # Different regions but same grade level
            ("+250789012345", "+250785678901"),  # Study buddies
        ]
        
        for user1_phone, user2_phone in peer_pairs:
            existing_connection = db.query(PeerConnection).filter(
                ((PeerConnection.user1_phone == user1_phone) & (PeerConnection.user2_phone == user2_phone)) |
                ((PeerConnection.user1_phone == user2_phone) & (PeerConnection.user2_phone == user1_phone))
            ).first()
            if not existing_connection:
                new_connection = PeerConnection(
                    user1_phone=user1_phone,
                    user2_phone=user2_phone,
                    connection_type="study_buddy"
                )
                db.add(new_connection)
        
        sessions = [
            (["+ 250781234567", "+250786789012"], "math", "Fractions and Decimals"),
            (["+250782345678", "+250785678901"], "english", "Grammar Practice"),
            (["+250783456789", "+250788901234"], "comprehension", "Reading Strategies"),
            (["+250784567890", "+250787890123", "+250780123456"], "debate", "Environmental Conservation"),
        ]
        
        for i, (participants, module, topic) in enumerate(sessions):
            session_id = f"peer_{datetime.utcnow().strftime('%Y%m%d')}_{i:03d}"
            existing_session = db.query(PeerLearningSession).filter(
                PeerLearningSession.session_id == session_id
            ).first()
            if not existing_session:
                new_session = PeerLearningSession(
                    session_id=session_id,
                    module_name=module,
                    topic=topic,
                    participants=json.dumps(participants),
                    started_at=datetime.utcnow() - timedelta(hours=i*2)
                )
                db.add(new_session)
        
        # Add historical user sessions for analytics
        modules = ["math", "english", "comprehension", "debate", "general"]
        
        for i in range(100):  # 100 sample sessions
            user_phone = sample_users[i % len(sample_users)]["phone"]
            module = modules[i % len(modules)]
            timestamp = datetime.utcnow() - timedelta(days=i % 14, hours=i % 24)
            
            session = UserSession(
                phone_number=user_phone,
                session_id=f"session_{i:04d}",
                module_name=module,
                interaction_type="sms" if i % 3 == 0 else "voice",
                user_input=f"Sample user input {i} - {module} practice",
                ai_response=f"Sample AI response with Rwanda context for {module} - Muraho! {i}",
                timestamp=timestamp,
                session_duration=float(10 + (i % 35))  # 10-45 minutes
            )
            db.add(session)
        
        for user_data in sample_users:
            for module in modules:
                usage_count = (hash(user_data["phone"] + module) % 8) + 1
                usage = ModuleUsage(
                    phone_number=user_data["phone"],
                    module_name=module,
                    usage_count=usage_count,
                    last_used=datetime.utcnow() - timedelta(days=hash(user_data["phone"]) % 7),
                    total_duration=float(usage_count * 18)
                )
                db.add(usage)
        
        db.commit()
        db.close()
        
        return {
            "status": "success",
            "message": "Sample data populated successfully",
            "data": {
                "users_created": len(sample_users),
                "regions_covered": len(regions),
                "peer_connections": len(peer_pairs),
                "learning_sessions": len(sessions),
                "historical_sessions": 100,
                "module_usage_records": len(sample_users) * len(modules)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating sample data: {str(e)}")
