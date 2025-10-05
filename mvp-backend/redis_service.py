import redis
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class RedisService:
    def __init__(self):
        self.redis_available = False
        self.redis_client = None
        self.memory_store = {}
        
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.redis_available = True
            print("[REDIS] Connected successfully")
        except Exception as e:
            print(f"[REDIS] Not available, using memory fallback: {e}")
            self.redis_available = False
    
    def get_user_context(self, phone_number: str) -> Dict[str, Any]:
        """Get user conversation context from Redis or memory fallback"""
        default_context = {
            "conversation_history": [],
            "user_state": {},
            "session_start": None,
            "topics_discussed": []
        }
        
        if self.redis_available:
            try:
                context_key = f"user_context:{phone_number}"
                context_data = self.redis_client.get(context_key)
                if context_data:
                    return json.loads(context_data)
                return default_context
            except Exception as e:
                print(f"[REDIS ERROR] Getting user context: {e}")
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
                print(f"[REDIS ERROR] Setting user context: {e}")
        else:
            self.memory_store[f"user_context:{phone_number}"] = context
    
    def add_to_conversation_history(self, phone_number: str, user_input: str, ai_response: str):
        """Add interaction to user's conversation history"""
        context = self.get_user_context(phone_number)
        context["conversation_history"].append({
            "user": user_input,
            "ai": ai_response,
            "timestamp": str(datetime.utcnow())
        })
        
        # Keep last 20 interactions
        if len(context["conversation_history"]) > 20:
            context["conversation_history"] = context["conversation_history"][-20:]
        
        self.set_user_context(phone_number, context, ttl=86400)  # 24 hours
    
    def add_topic(self, phone_number: str, topic: str):
        """Track topics discussed by user"""
        context = self.get_user_context(phone_number)
        if topic not in context["topics_discussed"]:
            context["topics_discussed"].append(topic)
        self.set_user_context(phone_number, context, ttl=86400)
    
    def clear_user_context(self, phone_number: str):
        """Clear user context from Redis or memory"""
        if self.redis_available:
            try:
                context_key = f"user_context:{phone_number}"
                self.redis_client.delete(context_key)
            except Exception as e:
                print(f"[REDIS ERROR] Clearing user context: {e}")
        else:
            if f"user_context:{phone_number}" in self.memory_store:
                del self.memory_store[f"user_context:{phone_number}"]

redis_service = RedisService()
