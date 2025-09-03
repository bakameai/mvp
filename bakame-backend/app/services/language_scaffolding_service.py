from typing import Tuple, Dict, Any
from app.services.llama_service import llama_service
from app.services.openai_service import openai_service
from app.config import settings

class LanguageScaffoldingService:
    def __init__(self):
        self.common_patterns = {
            "missing_articles": [
                (r"\b(go|went)\s+(school|market|home)\b", r"\1 to \2"),
                (r"\b(at|in)\s+(school|market|home)\b", r"\1 the \2"),
            ],
            
            "tense_corrections": [
                (r"\b(yesterday|last)\s+.*\b(go|come|see|eat|play)\b", "past_tense_needed"),
                (r"\b(tomorrow|will)\s+.*\b(went|came|saw|ate|played)\b", "future_tense_needed"),
            ],
            
            "regional_patterns": [
                (r"\bI am going home\b", "I am going home"),
                (r"\bI go home\b", "I am going home"),
                (r"\bI have went\b", "I have gone"),
            ]
        }
    
    async def process_with_scaffolding(self, user_input: str, focus_on_meaning: bool = True) -> Tuple[str, str, bool]:
        """
        Process user input with language scaffolding
        Returns: (corrected_text, feedback_message, needs_gentle_correction)
        """
        if not user_input or len(user_input.strip()) == 0:
            return user_input, "", False
        
        meaning_preserved, corrected_text = await self._extract_and_preserve_meaning(user_input)
        
        if not meaning_preserved:
            return user_input, "", False
        
        feedback = ""
        needs_correction = corrected_text != user_input.strip()
        
        if needs_correction and not focus_on_meaning:
            feedback = await self._generate_gentle_feedback(user_input, corrected_text)
        
        return corrected_text, feedback, needs_correction
    
    async def _extract_and_preserve_meaning(self, user_input: str) -> Tuple[bool, str]:
        """Extract meaning and gently correct while preserving intent"""
        try:
            correction_prompt = f"""
            A student learning English said: "{user_input}"
            
            This student is from Rwanda and may have different grammar patterns.
            Please:
            1. Understand what they meant to communicate
            2. Gently correct grammar while keeping their exact meaning
            3. Fill in missing words (like "to", "the", "a") if needed
            4. Fix verb tenses if clearly wrong
            5. Keep their vocabulary choices unless completely wrong
            
            If the meaning is clear, respond with:
            CORRECTED: [corrected version]
            MEANINGFUL: yes
            
            If you cannot understand what they meant, respond with:
            CORRECTED: [original text]
            MEANINGFUL: no
            
            Focus on communication success, not perfect grammar.
            """
            
            messages = [{"role": "user", "content": correction_prompt}]
            
            if settings.use_llama:
                response = await llama_service.generate_response(messages, "english", "normal")
            else:
                response = await openai_service.generate_response(messages, "english")
            
            lines = response.split('\n')
            corrected = user_input.strip()
            meaningful = False
            
            for line in lines:
                if line.startswith("CORRECTED:"):
                    corrected = line.replace("CORRECTED:", "").strip()
                elif line.startswith("MEANINGFUL:"):
                    meaningful = "yes" in line.lower()
            
            return meaningful, corrected
            
        except Exception as e:
            print(f"Error in meaning extraction: {e}")
            return True, user_input.strip()
    
    async def _generate_gentle_feedback(self, original: str, corrected: str) -> str:
        """Generate encouraging feedback about the correction"""
        if original.strip() == corrected.strip():
            return ""
        
        try:
            feedback_prompt = f"""
            A student said: "{original}"
            We gently corrected it to: "{corrected}"
            
            Generate a very brief, encouraging feedback (under 15 words) that:
            - Praises their effort
            - Mentions what was improved
            - Stays positive and supportive
            - Uses simple language
            
            Examples:
            "Good try! I added 'to' to make it clearer."
            "Nice! I helped with the verb tense."
            "Great idea! I filled in a missing word."
            
            Keep it short and encouraging:
            """
            
            messages = [{"role": "user", "content": feedback_prompt}]
            
            if settings.use_llama:
                response = await llama_service.generate_response(messages, "english", "normal")
            else:
                response = await openai_service.generate_response(messages, "english")
            
            return response.strip()
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return "Good try! I made a small improvement."
    
    def assess_communication_success(self, user_input: str, expected_meaning: str = None) -> Dict[str, Any]:
        """Assess if communication was successful regardless of grammar"""
        
        if not user_input:
            return {
                "communication_successful": False,
                "meaning_clarity": 0.0,
                "effort_level": 0.0,
                "needs_support": True
            }
        
        word_count = len(user_input.split())
        has_content = len(user_input.strip()) > 0
        has_structure = word_count > 1
        
        effort_score = 0.0
        if has_content:
            effort_score += 0.3
        if has_structure:
            effort_score += 0.3
        if word_count >= 3:
            effort_score += 0.2
        if any(word in user_input.lower() for word in ["i", "you", "we", "they", "my", "your"]):
            effort_score += 0.2
        
        meaning_score = 0.0
        if has_content:
            meaning_score += 0.4
        if has_structure:
            meaning_score += 0.3
        if word_count >= 4:
            meaning_score += 0.3
        
        communication_successful = effort_score >= 0.5 and meaning_score >= 0.4
        
        return {
            "communication_successful": communication_successful,
            "meaning_clarity": meaning_score,
            "effort_level": effort_score,
            "needs_support": effort_score < 0.3,
            "word_count": word_count,
            "has_structure": has_structure
        }
    
    def get_scaffolding_strategy(self, user_context: Dict[str, Any], current_errors: list) -> str:
        """Determine appropriate scaffolding strategy based on user history"""
        
        error_patterns = {}
        for error in current_errors[-5:]:
            error_type = error.get("type", "unknown")
            error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
        
        if error_patterns.get("grammar", 0) >= 3:
            return "focus_on_structure"
        elif error_patterns.get("vocabulary", 0) >= 3:
            return "focus_on_words"
        elif error_patterns.get("pronunciation", 0) >= 3:
            return "focus_on_clarity"
        else:
            return "focus_on_meaning"
    
    def should_interrupt_for_correction(self, error_severity: str, user_confidence: float) -> bool:
        """Decide whether to interrupt student for immediate correction"""
        
        if error_severity in ["minor", "pronunciation"]:
            return False
        
        if error_severity == "major" and user_confidence < 0.3:
            return True
        
        return False

language_scaffolding_service = LanguageScaffoldingService()
