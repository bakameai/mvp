import redis
import json
from typing import Dict, Any, Optional
from datetime import datetime
from app.config import settings

class RedisService:
    def __init__(self):
        try:
            self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            self.redis_client.ping()
            self.redis_available = True
            print("Redis connection successful")
        except Exception as e:
            print(f"Redis connection failed: {e}. Using in-memory fallback.")
            self.redis_client = None
            self.redis_available = False
            self.memory_store = {}
    
    def get_user_context(self, phone_number: str) -> Dict[str, Any]:
        """Get user conversation context from Redis or memory fallback"""
        default_context = {
            "current_module": None,
            "conversation_history": [],
            "user_state": {},
            "session_start": None
        }
        
        if self.redis_available:
            try:
                context_key = f"user_context:{phone_number}"
                context_data = self.redis_client.get(context_key)
                if context_data:
                    return json.loads(context_data)
                return default_context
            except Exception as e:
                print(f"Redis error getting user context: {e}")
                return default_context
        else:
            return self.memory_store.get(f"user_context:{phone_number}", default_context)
    
    def set_user_context(self, phone_number: str, context: Dict[str, Any], ttl: int = 3600):
        """Set user conversation context in Redis or memory fallback with TTL (default 1 hour)"""
        if self.redis_available:
            try:
                context_key = f"user_context:{phone_number}"
                self.redis_client.setex(context_key, ttl, json.dumps(context))
            except Exception as e:
                print(f"Redis error setting user context: {e}")
        else:
            self.memory_store[f"user_context:{phone_number}"] = context
    
    def add_to_conversation_history(self, phone_number: str, user_input: str, ai_response: str):
        """Add interaction to conversation history - disabled for fresh sessions"""
        pass
    
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
        if self.redis_available:
            try:
                context_key = f"user_context:{phone_number}"
                self.redis_client.delete(context_key)
            except Exception as e:
                print(f"Redis error clearing user context: {e}")
        else:
            context_key = f"user_context:{phone_number}"
            if context_key in self.memory_store:
                del self.memory_store[context_key]

redis_service = RedisService()
