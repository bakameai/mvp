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
        """Add interaction to user's conversation history with unlimited storage"""
        context = self.get_user_context(phone_number)
        context["conversation_history"].append({
            "user": user_input,
            "ai": ai_response,
            "timestamp": str(datetime.utcnow())
        })
        
        if len(context["conversation_history"]) > 100:
            recent_history = context["conversation_history"][-50:]
            older_history = context["conversation_history"][:-50]
            
            if not context.get("conversation_summary"):
                context["conversation_summary"] = self._create_conversation_summary(older_history)
            
            context["conversation_history"] = recent_history
        
        self.set_user_context(phone_number, context, ttl=86400)
    
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
    
    def _create_conversation_summary(self, interactions: list) -> str:
        """Create a summary of older conversation history"""
        if not interactions:
            return ""
        
        summary_points = []
        for interaction in interactions[-10:]:
            summary_points.append(f"User: {interaction['user'][:50]}... AI: {interaction['ai'][:50]}...")
        
        return f"Previous conversation summary ({len(interactions)} interactions): " + " | ".join(summary_points)
    
    def get_conversation_context_for_ai(self, phone_number: str, limit: int = 10) -> list:
        """Get conversation context optimized for AI processing"""
        context = self.get_user_context(phone_number)
        recent_history = context.get("conversation_history", [])[-limit:]
        
        if context.get("conversation_summary") and len(context.get("conversation_history", [])) >= 50:
            return [{"role": "system", "content": context["conversation_summary"]}] + [
                {"role": "user" if i % 2 == 0 else "assistant", 
                 "content": interaction["user"] if i % 2 == 0 else interaction["ai"]}
                for i, interaction in enumerate(recent_history)
                for _ in [0, 1]
            ]
        
        return recent_history
    
    def set_session_data(self, session_id: str, key: str, value: str, ttl: int = 300):
        """Set session-specific data with TTL (default 5 minutes)"""
        if self.redis_available:
            try:
                session_key = f"session:{session_id}:{key}"
                self.redis_client.setex(session_key, ttl, value)
            except Exception as e:
                print(f"Redis error setting session data: {e}")
        else:
            session_key = f"session:{session_id}:{key}"
            self.memory_store[session_key] = value
    
    def get_session_data(self, session_id: str, key: str) -> Optional[str]:
        """Get session-specific data"""
        if self.redis_available:
            try:
                session_key = f"session:{session_id}:{key}"
                return self.redis_client.get(session_key)
            except Exception as e:
                print(f"Redis error getting session data: {e}")
                return None
        else:
            session_key = f"session:{session_id}:{key}"
            return self.memory_store.get(session_key)
    
    def delete_session_data(self, session_id: str, key: str):
        """Delete session-specific data"""
        if self.redis_available:
            try:
                session_key = f"session:{session_id}:{key}"
                self.redis_client.delete(session_key)
            except Exception as e:
                print(f"Redis error deleting session data: {e}")
        else:
            session_key = f"session:{session_id}:{key}"
            if session_key in self.memory_store:
                del self.memory_store[session_key]

redis_service = RedisService()
