import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import User, PeerConnection, LearningGroup, GroupMembership, PeerLearningSession, get_db
from app.services.redis_service import redis_service

class CommunityService:
    def __init__(self):
        self.rwanda_regions = ["Kigali", "Northern", "Southern", "Eastern", "Western"]
        self.grade_levels = ["Primary 1-3", "Primary 4-6", "Secondary 1-3", "Secondary 4-6", "Adult Learning"]
    
    async def register_user(self, phone_number: str, user_type: str = "student", 
                          name: str = None, region: str = None, school: str = None, 
                          grade_level: str = None) -> Dict[str, Any]:
        """Register a new user or update existing user profile"""
        db = next(get_db())
        try:
            existing_user = db.query(User).filter(User.phone_number == phone_number).first()
            
            if existing_user:
                if name:
                    existing_user.name = name
                if region and region in self.rwanda_regions:
                    existing_user.region = region
                if school:
                    existing_user.school = school
                if grade_level and grade_level in self.grade_levels:
                    existing_user.grade_level = grade_level
                existing_user.last_active = datetime.utcnow()
                db.commit()
                return {"status": "updated", "user": self._user_to_dict(existing_user)}
            else:
                new_user = User(
                    phone_number=phone_number,
                    user_type=user_type,
                    name=name,
                    region=region if region in self.rwanda_regions else None,
                    school=school,
                    grade_level=grade_level if grade_level in self.grade_levels else None
                )
                db.add(new_user)
                db.commit()
                
                await self._auto_assign_to_regional_groups(phone_number, region)
                
                return {"status": "created", "user": self._user_to_dict(new_user)}
        finally:
            db.close()
    
    async def find_study_buddies(self, phone_number: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find potential study buddies based on region, grade level, and activity"""
        db = next(get_db())
        try:
            user = db.query(User).filter(User.phone_number == phone_number).first()
            if not user:
                return []
            
            potential_buddies = db.query(User).filter(
                User.phone_number != phone_number,
                User.user_type == "student",
                User.is_active == True
            )
            
            if user.region:
                potential_buddies = potential_buddies.filter(User.region == user.region)
            
            if user.grade_level:
                potential_buddies = potential_buddies.filter(User.grade_level == user.grade_level)
            
            buddies = potential_buddies.order_by(User.last_active.desc()).limit(limit).all()
            
            return [self._user_to_dict(buddy) for buddy in buddies]
        finally:
            db.close()
    
    async def create_peer_connection(self, user1_phone: str, user2_phone: str, 
                                   connection_type: str = "study_buddy") -> Dict[str, Any]:
        """Create a peer connection between two users"""
        db = next(get_db())
        try:
            existing_connection = db.query(PeerConnection).filter(
                ((PeerConnection.user1_phone == user1_phone) & (PeerConnection.user2_phone == user2_phone)) |
                ((PeerConnection.user1_phone == user2_phone) & (PeerConnection.user2_phone == user1_phone))
            ).first()
            
            if existing_connection:
                return {"status": "exists", "connection": self._connection_to_dict(existing_connection)}
            
            new_connection = PeerConnection(
                user1_phone=user1_phone,
                user2_phone=user2_phone,
                connection_type=connection_type
            )
            db.add(new_connection)
            db.commit()
            
            return {"status": "created", "connection": self._connection_to_dict(new_connection)}
        finally:
            db.close()
    
    async def get_regional_learning_groups(self, region: str) -> List[Dict[str, Any]]:
        """Get learning groups for a specific Rwanda region"""
        db = next(get_db())
        try:
            groups = db.query(LearningGroup).filter(
                LearningGroup.region == region,
                LearningGroup.is_active == True
            ).all()
            
            return [self._group_to_dict(group) for group in groups]
        finally:
            db.close()
    
    async def join_learning_group(self, phone_number: str, group_id: int) -> Dict[str, Any]:
        """Join a user to a learning group"""
        db = next(get_db())
        try:
            existing_membership = db.query(GroupMembership).filter(
                GroupMembership.group_id == group_id,
                GroupMembership.user_phone == phone_number,
                GroupMembership.is_active == True
            ).first()
            
            if existing_membership:
                return {"status": "already_member", "membership": self._membership_to_dict(existing_membership)}
            
            group = db.query(LearningGroup).filter(LearningGroup.id == group_id).first()
            if not group or not group.is_active:
                return {"status": "group_not_found"}
            
            current_members = db.query(GroupMembership).filter(
                GroupMembership.group_id == group_id,
                GroupMembership.is_active == True
            ).count()
            
            if current_members >= group.max_members:
                return {"status": "group_full"}
            
            new_membership = GroupMembership(
                group_id=group_id,
                user_phone=phone_number
            )
            db.add(new_membership)
            db.commit()
            
            return {"status": "joined", "membership": self._membership_to_dict(new_membership)}
        finally:
            db.close()
    
    async def start_peer_learning_session(self, participants: List[str], module_name: str, 
                                        topic: str, group_id: int = None) -> Dict[str, Any]:
        """Start a collaborative learning session"""
        session_id = f"peer_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(participants)}"
        
        db = next(get_db())
        try:
            new_session = PeerLearningSession(
                session_id=session_id,
                group_id=group_id,
                module_name=module_name,
                topic=topic,
                participants=json.dumps(participants)
            )
            db.add(new_session)
            db.commit()
            
            for phone in participants:
                context = redis_service.get_user_context(phone)
                context["peer_session"] = {
                    "session_id": session_id,
                    "participants": participants,
                    "module": module_name,
                    "topic": topic,
                    "started_at": str(datetime.utcnow())
                }
                redis_service.set_user_context(phone, context)
            
            return {"status": "started", "session_id": session_id, "participants": participants}
        finally:
            db.close()
    
    async def get_community_analytics(self) -> Dict[str, Any]:
        """Get community analytics for admin dashboard"""
        db = next(get_db())
        try:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(
                User.last_active >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            regional_distribution = {}
            for region in self.rwanda_regions:
                count = db.query(User).filter(User.region == region).count()
                regional_distribution[region] = count
            
            total_groups = db.query(LearningGroup).filter(LearningGroup.is_active == True).count()
            total_connections = db.query(PeerConnection).filter(PeerConnection.status == "active").count()
            
            recent_sessions = db.query(PeerLearningSession).filter(
                PeerLearningSession.started_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            return {
                "total_users": total_users,
                "active_users_7d": active_users,
                "regional_distribution": regional_distribution,
                "total_learning_groups": total_groups,
                "active_peer_connections": total_connections,
                "peer_sessions_7d": recent_sessions,
                "engagement_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 2)
            }
        finally:
            db.close()
    
    async def _auto_assign_to_regional_groups(self, phone_number: str, region: str):
        """Automatically assign new users to regional learning groups"""
        if not region or region not in self.rwanda_regions:
            return
        
        db = next(get_db())
        try:
            regional_group = db.query(LearningGroup).filter(
                LearningGroup.region == region,
                LearningGroup.group_type == "regional",
                LearningGroup.is_active == True
            ).first()
            
            if not regional_group:
                regional_group = LearningGroup(
                    name=f"{region} Regional Learning Community",
                    description=f"Learning community for students in {region} region of Rwanda",
                    group_type="regional",
                    region=region,
                    max_members=200
                )
                db.add(regional_group)
                db.commit()
            
            await self.join_learning_group(phone_number, regional_group.id)
        finally:
            db.close()
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert User object to dictionary"""
        return {
            "phone_number": user.phone_number,
            "user_type": user.user_type,
            "name": user.name,
            "region": user.region,
            "school": user.school,
            "grade_level": user.grade_level,
            "total_points": user.total_points,
            "current_level": user.current_level,
            "created_at": str(user.created_at),
            "last_active": str(user.last_active)
        }
    
    def _connection_to_dict(self, connection: PeerConnection) -> Dict[str, Any]:
        """Convert PeerConnection object to dictionary"""
        return {
            "id": connection.id,
            "user1_phone": connection.user1_phone,
            "user2_phone": connection.user2_phone,
            "connection_type": connection.connection_type,
            "status": connection.status,
            "created_at": str(connection.created_at)
        }
    
    def _group_to_dict(self, group: LearningGroup) -> Dict[str, Any]:
        """Convert LearningGroup object to dictionary"""
        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "group_type": group.group_type,
            "region": group.region,
            "school": group.school,
            "grade_level": group.grade_level,
            "subject": group.subject,
            "max_members": group.max_members,
            "created_at": str(group.created_at)
        }
    
    def _membership_to_dict(self, membership: GroupMembership) -> Dict[str, Any]:
        """Convert GroupMembership object to dictionary"""
        return {
            "id": membership.id,
            "group_id": membership.group_id,
            "user_phone": membership.user_phone,
            "role": membership.role,
            "joined_at": str(membership.joined_at)
        }

community_service = CommunityService()
