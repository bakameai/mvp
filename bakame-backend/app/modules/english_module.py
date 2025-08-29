from typing import Dict, Any
from app.services.openai_service import openai_service
from app.services.llama_service import llama_service
from app.services.emotional_intelligence_service import emotional_intelligence_service
from app.services.gamification_service import gamification_service
from app.services.multimodal_service import multimodal_service
from app.config import settings

class EnglishModule:
    def __init__(self):
        self.module_name = "english"
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process English learning input"""
        
        emotion_data = await emotional_intelligence_service.detect_emotion(user_input)
        emotional_intelligence_service.track_emotional_journey(user_context, emotion_data)
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["exit", "quit", "stop", "back", "menu", "hello", "hi"]):
            user_context.setdefault("user_state", {})["requested_module"] = "general"
            return "Returning to main menu. How can I help you today?"
        
        if any(word in user_input_lower for word in ["bye", "goodbye", "done"]):
            return f"Want to keep learning or stop for now? You did great today, {user_context.get('user_name', 'friend')}. I'll be here next time you call."
        
        gamification_service.update_progress(user_context, "session_complete", self.module_name)
        
        if any(word in user_input_lower for word in ["grammar", "correct", "fix", "tense", "verb"]):
            base_response = await self._grammar_tutoring(user_input, user_context, "grammar")
        elif any(word in user_input_lower for word in ["story", "write", "create", "composition", "essay"]):
            base_response = await self._composition_tutoring_evaluation(user_input, user_context, "composition")
        elif any(word in user_input_lower for word in ["repeat", "practice", "pronunciation"]):
            base_response = await self._repeat_practice(user_input, user_context)
        elif any(word in user_input_lower for word in ["help", "learn", "teach"]):
            base_response = await self._english_tutoring(user_input, user_context)
        else:
            base_response = await self._english_tutoring(user_input, user_context)
        
        new_achievements = gamification_service.check_achievements(user_context)
        if new_achievements:
            achievement_msg = "\n\n" + "\n".join([ach["message"] for ach in new_achievements])
            base_response += achievement_msg
        
        return await emotional_intelligence_service.generate_emotionally_aware_response(
            user_input, base_response, emotion_data, self.module_name
        )
    
    async def _grammar_correction(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Provide grammar correction and feedback"""
        messages = [
            {"role": "user", "content": f"Please correct any grammar mistakes in this sentence and explain the corrections: '{user_input}'"}
        ]
        
        for interaction in user_context.get("conversation_history", [])[-4:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        if settings.use_llama:
            response = await llama_service.generate_response(
                messages, self.module_name, "normal", user_context
            )
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        return response
    
    async def _repeat_practice(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Provide pronunciation and repetition practice"""
        messages = [
            {"role": "user", "content": f"Help me practice pronunciation. Give me feedback on how I said: '{user_input}' and provide a similar sentence to practice."}
        ]
        
        if settings.use_llama:
            response = await llama_service.generate_response(
                messages, self.module_name, "normal", user_context
            )
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        return response
    
    async def _english_tutoring(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """General English tutoring with curriculum-aware assessment"""
        
        from app.services.language_scaffolding_service import language_scaffolding_service
        corrected_input, correction_feedback, needs_correction = await language_scaffolding_service.process_with_scaffolding(user_input)
        
        from app.services.curriculum_service import curriculum_service
        phone_number = user_context.get("phone_number", "")
        current_stage = curriculum_service.get_user_stage(phone_number, "grammar")
        
        assessment = await curriculum_service.assess_student_response(
            corrected_input, "grammar", current_stage, "tutoring"
        )
        
        curriculum_service.log_assessment(phone_number, "grammar", current_stage, assessment)
        
        stage_change = curriculum_service.check_stage_advancement(phone_number, "grammar")
        
        user_level = user_context.get("english_level", "A1")
        recent_errors = user_context.get("recent_errors", [])
        
        exercise_guidance = self._get_next_exercise(user_level, recent_errors)
        
        messages = [
            {"role": "system", "content": exercise_guidance},
            {"role": "user", "content": corrected_input}
        ]
        
        for interaction in user_context.get("conversation_history", [])[-4:]:
            messages.insert(-1, {"role": "user", "content": interaction["user"]})
            messages.insert(-1, {"role": "assistant", "content": interaction["ai"]})
        
        if settings.use_llama:
            response = await llama_service.generate_response(
                messages, self.module_name, "normal", user_context
            )
        else:
            response = await openai_service.generate_response(messages, self.module_name)
        
        if correction_feedback:
            response = f"{correction_feedback} {response}"
        
        if stage_change:
            if stage_change in ["understand", "apply", "analyze", "evaluate", "create"]:
                response += f"\n\nExcellent progress! You've advanced to {stage_change} level! 🌟"
            else:
                response += f"\n\nLet's practice more at {stage_change} level together. 💪"
        
        self._track_learning_progress(user_input, response, user_context)
        
        return response
    
    def _get_next_exercise(self, level: str, recent_errors: list) -> str:
        """Get level-appropriate exercise with targeted correction"""
        
        level_prompts = {
            "A1": "Focus on basic vocabulary and simple present tense. Use very simple words. Give short, encouraging responses (≤2 sentences). End with a direct question about daily life.",
            
            "A2": "Practice past tense and basic conversations. Use simple past and present. Keep responses short (≤2 sentences). Ask about experiences or preferences.",
            
            "B1": "Work on future tense and expressing opinions. Use varied tenses but keep language clear. Responses should be ≤2 sentences. Ask for opinions or plans.",
            
            "B2": "Practice complex sentences and nuanced expression. Use more sophisticated vocabulary. Keep responses ≤2 sentences. Ask thought-provoking questions."
        }
        
        base_prompt = level_prompts.get(level, level_prompts["A1"])
        
        if recent_errors:
            error_types = [error.get("type") for error in recent_errors[-2:]]
            if "grammar" in error_types:
                base_prompt += " Pay special attention to grammar corrections."
            if "pronunciation" in error_types:
                base_prompt += " Give pronunciation tips when needed."
            if "vocabulary" in error_types:
                base_prompt += " Suggest simpler word choices."
        
        return base_prompt
    
    def _track_learning_progress(self, user_input: str, ai_response: str, user_context: Dict[str, Any]):
        """Track learning progress and identify error patterns"""
        
        errors = []
        response_lower = ai_response.lower()
        
        if any(word in response_lower for word in ["correct", "should be", "try saying"]):
            if "grammar" in response_lower or "tense" in response_lower:
                errors.append({"type": "grammar", "input": user_input[:50]})
            elif "pronunciation" in response_lower or "sound" in response_lower:
                errors.append({"type": "pronunciation", "input": user_input[:50]})
            elif "word" in response_lower or "vocabulary" in response_lower:
                errors.append({"type": "vocabulary", "input": user_input[:50]})
        
        if errors:
            recent_errors = user_context.get("recent_errors", [])
            recent_errors.extend(errors)
            user_context["recent_errors"] = recent_errors[-5:]  # Keep last 5 errors
            
            self._update_user_level(user_context)
    
    def _update_user_level(self, user_context: Dict[str, Any]):
        """Update user level based on error patterns and progress"""
        recent_errors = user_context.get("recent_errors", [])
        current_level = user_context.get("english_level", "A1")
        
        if len(recent_errors) < 2:
            level_progression = {"A1": "A2", "A2": "B1", "B1": "B2", "B2": "B2"}
            user_context["english_level"] = level_progression.get(current_level, current_level)
        elif len(recent_errors) > 4:
            level_regression = {"B2": "B1", "B1": "A2", "A2": "A1", "A1": "A1"}
            user_context["english_level"] = level_regression.get(current_level, current_level)
    
    def get_welcome_message(self) -> str:
        """Get welcome message for English module"""
        return "Muraho! 🌟 I'm so excited to practice English with you! English opens many doors in Rwanda and connects us to the global community while we maintain our beautiful Kinyarwanda heritage. Whether you want to improve grammar, pronunciation, or just have great conversations - I'm here to help. What aspect of English would you like to explore together?"

    async def recover_and_feedback(self, user_input: str) -> tuple[str, str]:
        """Fill missing/unclear words and provide gentle feedback"""
        try:
            correction_prompt = f"""
            Please correct this English sentence by filling in missing words and fixing grammar, but keep the original meaning:
            "{user_input}"
            
            Respond in this format:
            CORRECTED: [corrected sentence]
            FEEDBACK: [brief, encouraging explanation of what was filled in, or "No changes needed" if perfect]
            """
            
            messages = [{"role": "user", "content": correction_prompt}]
            
            if settings.use_llama:
                response = await llama_service.generate_response(messages, "english")
            else:
                response = await openai_service.generate_response(messages, "english")
            
            lines = response.split('\n')
            corrected = user_input
            feedback = ""
            
            for line in lines:
                if line.startswith("CORRECTED:"):
                    corrected = line.replace("CORRECTED:", "").strip()
                elif line.startswith("FEEDBACK:"):
                    feedback = line.replace("FEEDBACK:", "").strip()
            
            if corrected != user_input and feedback != "No changes needed":
                feedback = f"Good try! I filled in: {feedback}"
            else:
                feedback = ""
                
            return corrected, feedback
            
        except Exception as e:
            print(f"Error in accent recovery: {e}")
            return user_input, ""

    async def _grammar_tutoring(self, user_input: str, user_context: Dict[str, Any], module: str) -> str:
        """Grammar-focused tutoring with curriculum assessment"""
        
        from app.services.language_scaffolding_service import language_scaffolding_service
        corrected_input, correction_feedback, needs_correction = await language_scaffolding_service.process_with_scaffolding(user_input)
        
        from app.services.curriculum_service import curriculum_service
        phone_number = user_context.get("phone_number", "")
        current_stage = curriculum_service.get_user_stage(phone_number, module)
        
        assessment = await curriculum_service.assess_student_response(
            corrected_input, module, current_stage, "grammar"
        )
        
        curriculum_service.log_assessment(phone_number, module, current_stage, assessment)
        stage_change = curriculum_service.check_stage_advancement(phone_number, module)
        
        messages = [
            {"role": "system", "content": "Focus on grammar instruction, error correction, and tense usage. Keep responses under 2 sentences."},
            {"role": "user", "content": corrected_input}
        ]
        
        if settings.use_llama:
            response = await llama_service.generate_response(messages, module, "normal", user_context)
        else:
            response = await openai_service.generate_response(messages, module)
        
        if correction_feedback:
            response = f"{correction_feedback} {response}"
        
        if stage_change:
            response += f"\n\nGreat progress in grammar! You've advanced to {stage_change} level! 📚"
        
        return response

    async def _composition_tutoring(self, user_input: str, user_context: Dict[str, Any], module: str) -> str:
        """Composition-focused tutoring with creative writing assessment"""
        
        from app.services.curriculum_service import curriculum_service
        phone_number = user_context.get("phone_number", "")
        current_stage = curriculum_service.get_user_stage(phone_number, module)
        
        assessment = await curriculum_service.assess_student_response(
            user_input, module, current_stage, "composition"
        )
        
        curriculum_service.log_assessment(phone_number, module, current_stage, assessment)
        stage_change = curriculum_service.check_stage_advancement(phone_number, module)
        
        messages = [
            {"role": "system", "content": "Focus on creative writing, storytelling, and expression. Encourage creativity and cultural storytelling. Keep responses under 2 sentences."},
            {"role": "user", "content": user_input}
        ]
        
        if settings.use_llama:
            response = await llama_service.generate_response(messages, module, "normal", user_context)
        else:
            response = await openai_service.generate_response(messages, module)
        
        if stage_change:
            response += f"\n\nYour storytelling is improving! You've advanced to {stage_change} level! ✨"
        
        return response
    
    async def _composition_tutoring_evaluation(self, user_input: str, user_context: Dict[str, Any], module: str) -> str:
        """Composition-focused tutoring with evaluation engine assessment"""
        
        from app.services.evaluation_engine import evaluation_engine
        phone_number = user_context.get("phone_number", "")
        current_stage = user_context.get("curriculum_stage", "remember")
        
        if not user_context.get("evaluation_prompt_given"):
            ivr_prompt = evaluation_engine.get_ivr_prompt("composition", current_stage, user_context)
            user_context["evaluation_prompt_given"] = True
            return ivr_prompt
        
        evaluation = await evaluation_engine.evaluate_response(
            user_input, "composition", current_stage, user_context
        )
        
        evaluation_engine.log_evaluation(phone_number, "composition", current_stage, evaluation, user_input)
        advancement = evaluation_engine.check_advancement(phone_number, "composition")
        
        response = evaluation["feedback"]
        if advancement:
            response += f"\n\nExcellent progress! You've advanced to {advancement} level! 📚"
        
        user_context["evaluation_prompt_given"] = False
        return response

english_module = EnglishModule()
