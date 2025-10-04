from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import settings

Base = declarative_base()

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    session_id = Column(String, index=True)
    module_name = Column(String)
    interaction_type = Column(String)  # "voice" or "sms"
    user_input = Column(Text)
    ai_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_duration = Column(Float, nullable=True)

class ModuleUsage(Base):
    __tablename__ = "module_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    module_name = Column(String)
    usage_count = Column(Integer, default=1)
    last_used = Column(DateTime, default=datetime.utcnow)
    total_duration = Column(Float, default=0.0)

<<<<<<< HEAD
if "sqlite" in settings.database_url:
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.database_url,
        connect_args={"sslmode": "require"},
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=30,
        max_overflow=0
    )
=======
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    user_type = Column(String, default="student")  # "student", "teacher", "admin"
    name = Column(String, nullable=True)
    region = Column(String, nullable=True)  # Rwanda regions: Kigali, Northern, Southern, Eastern, Western
    school = Column(String, nullable=True)
    grade_level = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    total_points = Column(Integer, default=0)
    current_level = Column(String, default="beginner")

class PeerConnection(Base):
    __tablename__ = "peer_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user1_phone = Column(String, ForeignKey("users.phone_number"), index=True)
    user2_phone = Column(String, ForeignKey("users.phone_number"), index=True)
    connection_type = Column(String)  # "study_buddy", "mentor_mentee", "regional_peer"
    status = Column(String, default="active")  # "active", "paused", "ended"
    created_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)

class LearningGroup(Base):
    __tablename__ = "learning_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    group_type = Column(String)  # "regional", "school", "grade_level", "subject"
    region = Column(String, nullable=True)
    school = Column(String, nullable=True)
    grade_level = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    teacher_phone = Column(String, ForeignKey("users.phone_number"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    max_members = Column(Integer, default=50)

class GroupMembership(Base):
    __tablename__ = "group_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("learning_groups.id"))
    user_phone = Column(String, ForeignKey("users.phone_number"))
    role = Column(String, default="member")  # "member", "moderator", "teacher"
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class PeerLearningSession(Base):
    __tablename__ = "peer_learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    group_id = Column(Integer, ForeignKey("learning_groups.id"), nullable=True)
    connection_id = Column(Integer, ForeignKey("peer_connections.id"), nullable=True)
    module_name = Column(String)
    topic = Column(String)
    participants = Column(Text)  # JSON list of phone numbers
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    session_summary = Column(Text, nullable=True)

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
>>>>>>> bakame-mvp-implementation
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)
    from app.models.auth import Base as AuthBase
    AuthBase.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
