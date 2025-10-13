# Redis service completely disabled - no context storage at all
class RedisService:
    def __init__(self):
        print("[Redis] All context storage disabled - every call is completely fresh")
    
    def get_user_context(self, phone_number: str):
        # Always return empty - no history
        return {}
    
    def set_user_context(self, phone_number: str, context: dict, ttl=None):
        # Don't store anything
        pass
    
    def update_user_context(self, phone_number: str, context: dict):
        # Don't update anything
        pass
    
    def clear_user_context(self, phone_number: str):
        # Nothing to clear
        pass
    
    def get_current_module(self, phone_number: str):
        # No module tracking
        return None
    
    def set_current_module(self, phone_number: str, module_name: str):
        # Don't track modules
        pass
    
    def add_to_conversation_history(self, phone_number: str, user_input: str, ai_response: str):
        # Don't store any history
        pass
    
    def get_conversation_context_for_ai(self, phone_number: str, limit: int = 0):
        # No context ever
        return []

redis_service = RedisService()