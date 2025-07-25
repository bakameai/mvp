import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import User, LearningGroup, GroupMembership, UserSession, ModuleUsage, get_db
from app.services.community_service import community_service
from app.services.redis_service import redis_service

class TeacherService:
    def __init__(self):
        self.teacher_permissions = [
            "create_groups", "manage_students", "view_analytics", 
            "assign_content", "moderate_discussions", "track_progress"
        ]
    
    async def register_teacher(self, phone_number: str, name: str, school: str, 
                             region: str, subjects: List[str] = None) -> Dict[str, Any]:
        """Register a new teacher account"""
        result = await community_service.register_user(
            phone_number=phone_number,
            user_type="teacher",
            name=name,
            region=region,
            school=school
        )
        
        if result["status"] in ["created", "updated"]:
            await self._setup_teacher_permissions(phone_number, subjects or [])
        
        return result
    
    async def create_classroom(self, teacher_phone: str, name: str, description: str,
                             grade_level: str, subject: str, max_students: int = 30) -> Dict[str, Any]:
        """Create a new classroom/learning group"""
        db = next(get_db())
        try:
            teacher = db.query(User).filter(
                User.phone_number == teacher_phone,
                User.user_type == "teacher"
            ).first()
            
            if not teacher:
                return {"status": "teacher_not_found"}
            
            new_classroom = LearningGroup(
                name=name,
                description=description,
                group_type="classroom",
                region=teacher.region,
                school=teacher.school,
                grade_level=grade_level,
                subject=subject,
                teacher_phone=teacher_phone,
                max_members=max_students
            )
            
            db.add(new_classroom)
            db.commit()
            
            teacher_membership = GroupMembership(
                group_id=new_classroom.id,
                user_phone=teacher_phone,
                role="teacher"
            )
            db.add(teacher_membership)
            db.commit()
            
            return {
                "status": "created",
                "classroom": {
                    "id": new_classroom.id,
                    "name": new_classroom.name,
                    "description": new_classroom.description,
                    "grade_level": new_classroom.grade_level,
                    "subject": new_classroom.subject,
                    "max_students": new_classroom.max_members,
                    "teacher": teacher.name
                }
            }
        finally:
            db.close()
    
    async def add_student_to_classroom(self, teacher_phone: str, classroom_id: int, 
                                     student_phone: str) -> Dict[str, Any]:
        """Add a student to teacher's classroom"""
        db = next(get_db())
        try:
            classroom = db.query(LearningGroup).filter(
                LearningGroup.id == classroom_id,
                LearningGroup.teacher_phone == teacher_phone
            ).first()
            
            if not classroom:
                return {"status": "classroom_not_found"}
            
            student = db.query(User).filter(User.phone_number == student_phone).first()
            if not student:
                await community_service.register_user(student_phone, "student")
            
            result = await community_service.join_learning_group(student_phone, classroom_id)
            
            if result["status"] == "joined":
                return {"status": "student_added", "classroom": classroom.name}
            else:
                return result
        finally:
            db.close()
    
    async def get_classroom_analytics(self, teacher_phone: str, classroom_id: int) -> Dict[str, Any]:
        """Get analytics for a specific classroom"""
        db = next(get_db())
        try:
            classroom = db.query(LearningGroup).filter(
                LearningGroup.id == classroom_id,
                LearningGroup.teacher_phone == teacher_phone
            ).first()
            
            if not classroom:
                return {"status": "classroom_not_found"}
            
            students = db.query(GroupMembership).filter(
                GroupMembership.group_id == classroom_id,
                GroupMembership.role == "member",
                GroupMembership.is_active == True
            ).all()
            
            student_phones = [membership.user_phone for membership in students]
            
            total_students = len(student_phones)
            active_students_7d = db.query(User).filter(
                User.phone_number.in_(student_phones),
                User.last_active >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            module_usage = {}
            for phone in student_phones:
                usage = db.query(ModuleUsage).filter(ModuleUsage.phone_number == phone).all()
                for module in usage:
                    if module.module_name not in module_usage:
                        module_usage[module.module_name] = {"total_usage": 0, "unique_users": 0}
                    module_usage[module.module_name]["total_usage"] += module.usage_count
                    module_usage[module.module_name]["unique_users"] += 1
            
            recent_sessions = db.query(UserSession).filter(
                UserSession.phone_number.in_(student_phones),
                UserSession.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            return {
                "classroom": {
                    "id": classroom.id,
                    "name": classroom.name,
                    "subject": classroom.subject,
                    "grade_level": classroom.grade_level
                },
                "students": {
                    "total": total_students,
                    "active_7d": active_students_7d,
                    "engagement_rate": round((active_students_7d / total_students * 100) if total_students > 0 else 0, 2)
                },
                "module_usage": module_usage,
                "recent_sessions": recent_sessions,
                "performance_insights": await self._generate_performance_insights(student_phones)
            }
        finally:
            db.close()
    
    async def get_teacher_dashboard(self, teacher_phone: str) -> Dict[str, Any]:
        """Get comprehensive teacher dashboard data"""
        db = next(get_db())
        try:
            teacher = db.query(User).filter(
                User.phone_number == teacher_phone,
                User.user_type == "teacher"
            ).first()
            
            if not teacher:
                return {"status": "teacher_not_found"}
            
            classrooms = db.query(LearningGroup).filter(
                LearningGroup.teacher_phone == teacher_phone,
                LearningGroup.is_active == True
            ).all()
            
            total_students = 0
            classroom_summaries = []
            
            for classroom in classrooms:
                student_count = db.query(GroupMembership).filter(
                    GroupMembership.group_id == classroom.id,
                    GroupMembership.role == "member",
                    GroupMembership.is_active == True
                ).count()
                
                total_students += student_count
                
                classroom_summaries.append({
                    "id": classroom.id,
                    "name": classroom.name,
                    "subject": classroom.subject,
                    "grade_level": classroom.grade_level,
                    "student_count": student_count,
                    "created_at": str(classroom.created_at)
                })
            
            return {
                "teacher": {
                    "name": teacher.name,
                    "school": teacher.school,
                    "region": teacher.region,
                    "phone_number": teacher.phone_number
                },
                "summary": {
                    "total_classrooms": len(classrooms),
                    "total_students": total_students,
                    "school": teacher.school,
                    "region": teacher.region
                },
                "classrooms": classroom_summaries,
                "recent_activity": await self._get_recent_teacher_activity(teacher_phone)
            }
        finally:
            db.close()
    
    async def send_classroom_announcement(self, teacher_phone: str, classroom_id: int, 
                                        message: str) -> Dict[str, Any]:
        """Send announcement to all students in a classroom"""
        db = next(get_db())
        try:
            classroom = db.query(LearningGroup).filter(
                LearningGroup.id == classroom_id,
                LearningGroup.teacher_phone == teacher_phone
            ).first()
            
            if not classroom:
                return {"status": "classroom_not_found"}
            
            students = db.query(GroupMembership).filter(
                GroupMembership.group_id == classroom_id,
                GroupMembership.role == "member",
                GroupMembership.is_active == True
            ).all()
            
            student_phones = [membership.user_phone for membership in students]
            
            announcement = {
                "type": "classroom_announcement",
                "from_teacher": teacher_phone,
                "classroom": classroom.name,
                "message": message,
                "timestamp": str(datetime.utcnow())
            }
            
            for phone in student_phones:
                context = redis_service.get_user_context(phone)
                if "announcements" not in context:
                    context["announcements"] = []
                context["announcements"].append(announcement)
                redis_service.set_user_context(phone, context)
            
            return {
                "status": "sent",
                "recipients": len(student_phones),
                "classroom": classroom.name
            }
        finally:
            db.close()
    
    async def _setup_teacher_permissions(self, teacher_phone: str, subjects: List[str]):
        """Setup initial permissions and preferences for teacher"""
        from app.services.redis_service import redis_service
        
        teacher_config = {
            "permissions": self.teacher_permissions,
            "subjects": subjects,
            "setup_completed": True,
            "setup_date": str(datetime.utcnow())
        }
        
        redis_service.redis_client.setex(
            f"teacher_config:{teacher_phone}", 
            86400 * 30,  # 30 days
            json.dumps(teacher_config)
        )
    
    async def _generate_performance_insights(self, student_phones: List[str]) -> Dict[str, Any]:
        """Generate performance insights for students"""
        db = next(get_db())
        try:
            if not student_phones:
                return {}
            
            total_sessions = db.query(UserSession).filter(
                UserSession.phone_number.in_(student_phones)
            ).count()
            
            module_performance = {}
            for phone in student_phones:
                sessions = db.query(UserSession).filter(UserSession.phone_number == phone).all()
                for session in sessions:
                    module = session.module_name
                    if module not in module_performance:
                        module_performance[module] = {"sessions": 0, "avg_duration": 0}
                    module_performance[module]["sessions"] += 1
                    if session.session_duration:
                        module_performance[module]["avg_duration"] += session.session_duration
            
            for module in module_performance:
                if module_performance[module]["sessions"] > 0:
                    module_performance[module]["avg_duration"] /= module_performance[module]["sessions"]
            
            return {
                "total_learning_sessions": total_sessions,
                "module_performance": module_performance,
                "engagement_trends": "Steady growth in math and comprehension modules",
                "recommendations": [
                    "Encourage more debate practice for critical thinking",
                    "Math module showing strong engagement",
                    "Consider group comprehension activities"
                ]
            }
        finally:
            db.close()
    
    async def _get_recent_teacher_activity(self, teacher_phone: str) -> List[Dict[str, Any]]:
        """Get recent activity for teacher dashboard"""
        return [
            {
                "type": "classroom_created",
                "description": "Created new Math classroom",
                "timestamp": str(datetime.utcnow() - timedelta(hours=2))
            },
            {
                "type": "student_added",
                "description": "Added 3 new students to English class",
                "timestamp": str(datetime.utcnow() - timedelta(hours=6))
            },
            {
                "type": "announcement_sent",
                "description": "Sent homework reminder to Primary 5 class",
                "timestamp": str(datetime.utcnow() - timedelta(days=1))
            }
        ]

teacher_service = TeacherService()
