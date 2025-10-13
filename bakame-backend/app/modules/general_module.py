from typing import Dict, Any
from app.services.openai_service import openai_service

class GeneralModule:
    def __init__(self):
        self.module_name = "english_conversation"
    
    async def process(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Always call OpenAI for every input - no hardcoding, no history"""
        print(f"[Module] Processing: {user_input}")
        # Direct pass to OpenAI - no modifications, no history
        response = await openai_service.generate_response(user_input, {})
        print(f"[Module] Returning: {response[:100]}...")
        return response

general_module = GeneralModule()