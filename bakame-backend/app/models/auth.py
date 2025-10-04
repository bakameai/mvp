from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class WebUser(Base):
    __tablename__ = "web_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="creator")  # "creator", "admin", "super_admin", "government", "enterprise"
    organization = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)

class ContentPage(Base):
    __tablename__ = "content_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    page_name = Column(String, unique=True, index=True)  # "hero", "features", "pricing", etc.
    content_data = Column(Text)  # JSON string with page content
    last_updated = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, index=True)  # user_id who made the update
