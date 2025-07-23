from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
