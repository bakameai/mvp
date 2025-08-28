import re
from typing import Tuple, Optional
from app.services.llama_service import llama_service
from app.services.openai_service import openai_service
from app.config import settings

class NameExtractionService:
    def __init__(self):
        self.name_patterns = [
            r"my name is (\w+)",
            r"i am (\w+)",
            r"i'm (\w+)",
            r"it's (\w+)",
            r"call me (\w+)",
            r"(\w+) is my name",
            r"^(\w+)$"
        ]
        
        self.nato_alphabet = {
            "alpha": "a", "bravo": "b", "charlie": "c", "delta": "d", "echo": "e",
            "foxtrot": "f", "golf": "g", "hotel": "h", "india": "i", "juliet": "j",
            "kilo": "k", "lima": "l", "mike": "m", "november": "n", "oscar": "o",
            "papa": "p", "quebec": "q", "romeo": "r", "sierra": "s", "tango": "t",
            "uniform": "u", "victor": "v", "whiskey": "w", "xray": "x", "yankee": "y", "zulu": "z",
            "dee": "d", "bee": "b", "see": "c", "gee": "g", "jay": "j", "kay": "k",
            "pee": "p", "tee": "t", "you": "u", "why": "y", "zee": "z"
        }
    
    def extract_name(self, user_input: str) -> Tuple[Optional[str], float]:
        """Extract name from user input with confidence score"""
        if not user_input or len(user_input.strip()) == 0:
            return None, 0.0
        
        user_input_lower = user_input.lower().strip()
        
        for pattern in self.name_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                name = match.group(1).title()
                if len(name) >= 2 and name.isalpha():
                    return name, 0.9
        
        words = user_input.strip().split()
        if len(words) == 1 and words[0].isalpha() and len(words[0]) >= 2:
            return words[0].title(), 0.7
        
        for word in words:
            if word.isalpha() and len(word) >= 2:
                return word.title(), 0.6
        
        return None, 0.0
    
    def extract_spelling(self, user_input: str) -> str:
        """Extract name from spelled letters"""
        if not user_input:
            return ""
        
        letters = []
        words = user_input.lower().split()
        
        for word in words:
            word = word.strip(".,!?")
            if len(word) == 1 and word.isalpha():
                letters.append(word.upper())
            elif word in self.nato_alphabet:
                letters.append(self.nato_alphabet[word].upper())
        
        return "".join(letters).title() if letters else ""
    
    async def generate_intro_message(self) -> str:
        """Generate warm intro message with temperature 0.4"""
        intro_prompt = "Generate a warm, short greeting (≤7 seconds when spoken) for a kid-friendly AI tutor named Bakame. Include: 'Muraho neza!' greeting, mention you can help with English, math, stories, and debate, then ask for their name. Keep it under 25 words."
        
        messages = [{"role": "user", "content": intro_prompt}]
        
        try:
            if settings.use_llama:
                response = await llama_service.generate_response(messages, "general", "welcome")
            else:
                response = await openai_service.generate_response(messages, "general")
            
            return response.strip()
        except Exception as e:
            print(f"Error generating intro: {e}")
            return "Muraho neza! I'm your learning buddy from Bakame. I can practice English, math, debate, and stories with you. What's your name?"
    
    def generate_confirmation_message(self, name: str) -> str:
        """Generate name confirmation message"""
        return f"I heard {name} — is that right? Say yes or tell me your name again."
    
    def generate_spell_request(self) -> str:
        """Generate spelling request message"""
        return "Let's spell it. Say each letter slowly, one at a time."
    
    def is_confirmation(self, user_input: str) -> bool:
        """Check if user is confirming their name"""
        if not user_input:
            return False
        
        confirmation_words = ["yes", "yeah", "yep", "correct", "right", "that's right", "mhmm", "uh huh"]
        user_input_lower = user_input.lower().strip()
        
        return any(word in user_input_lower for word in confirmation_words)

name_extraction_service = NameExtractionService()
