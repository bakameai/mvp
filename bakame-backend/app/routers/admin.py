from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, List
from app.services.logging_service import logging_service

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
