from typing import Dict, Any
from app.services.openai_service import openai_service
from app.config import settings

class GeneralModule:
    def __init__(self):
        self.module_name = "english_conversation"
    
    async def process(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process all inputs as English conversation practice using OpenAI"""
        
        # Simply pass the user input to OpenAI for natural English teaching conversation
        # No modules, no hardcoded responses, just natural conversation
        return await openai_service.generate_response(user_input, user_context)

general_module = GeneralModule()