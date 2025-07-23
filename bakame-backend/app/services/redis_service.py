import redis
import json
from typing import Dict, Any, Optional
from datetime import datetime
from app.config import settings

class RedisService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    def get_user_context(self, phone_number: str) -> Dict[str, Any]:
        """Get user conversation context from Redis"""
        context_key = f"user_context:{phone_number}"
        context_data = self.redis_client.get(context_key)
        
        if context_data:
            return json.loads(context_data)
        
        return {
            "current_module": None,
            "conversation_history": [],
            "user_state": {},
            "session_start": None
        }
    
    def set_user_context(self, phone_number: str, context: Dict[str, Any], ttl: int = 3600):
        """Set user conversation context in Redis with TTL (default 1 hour)"""
        context_key = f"user_context:{phone_number}"
        self.redis_client.setex(context_key, ttl, json.dumps(context))
    
    def add_to_conversation_history(self, phone_number: str, user_input: str, ai_response: str):
        """Add interaction to user's conversation history"""
        context = self.get_user_context(phone_number)
        context["conversation_history"].append({
            "user": user_input,
            "ai": ai_response,
            "timestamp": str(datetime.utcnow())
        })
        
        if len(context["conversation_history"]) > 10:
            context["conversation_history"] = context["conversation_history"][-10:]
        
        self.set_user_context(phone_number, context)
    
    def set_current_module(self, phone_number: str, module_name: str):
        """Set the current active module for a user"""
        context = self.get_user_context(phone_number)
        context["current_module"] = module_name
        self.set_user_context(phone_number, context)
    
    def get_current_module(self, phone_number: str) -> Optional[str]:
        """Get the current active module for a user"""
        context = self.get_user_context(phone_number)
        return context.get("current_module")
    
    def clear_user_context(self, phone_number: str):
        """Clear user context (for session end)"""
        context_key = f"user_context:{phone_number}"
        self.redis_client.delete(context_key)

redis_service = RedisService()
