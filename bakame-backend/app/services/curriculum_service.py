import os
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from app.services.llama_service import llama_service
from app.services.openai_service import openai_service
from app.services.redis_service import redis_service
from app.config import settings

class CurriculumService:
    def __init__(self):
        self.modules = ["english", "math", "debate", "comprehension"]
        self.bloom_stages = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        
        self.curriculum_data = self._load_curriculum_data()
        
        self.scoring_weights = {
            "keyword_match": 0.4,
            "sentence_structure": 0.3,
            "llm_evaluation": 0.3
        }
    
    def _load_curriculum_data(self) -> Dict[str, Dict[str, Any]]:
        """Load curriculum stage data from markdown files"""
        curriculum = {}
        
        for module in self.modules:
            curriculum[module] = {}
            for stage in self.bloom_stages:
                file_path = f"/home/ubuntu/repos/mvp/bakame-backend/docs/curriculum/{module}_{stage}.md"
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        curriculum[module][stage] = self._parse_curriculum_file(content)
                else:
                    curriculum[module][stage] = self._get_default_stage_data(module, stage)
        
        return curriculum
    
    def _parse_curriculum_file(self, content: str) -> Dict[str, Any]:
        """Parse curriculum markdown file into structured data"""
        lines = content.split('\n')
        data = {
            "goal": "",
            "skills": [],
            "prompts": [],
            "expected_responses": [],
            "pass_criteria": "",
            "fail_criteria": "",
            "advancement_rules": ""
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("## 🎯 Learning Goal"):
                current_section = "goal"
            elif line.startswith("## 🧩 Key Skills"):
                current_section = "skills"
            elif line.startswith("## 🗣️ Voice Prompts"):
                current_section = "prompts"
            elif line.startswith("## 🎤 Expected Student Responses"):
                current_section = "expected_responses"
            elif line.startswith("**PASS Requirements:**"):
                current_section = "pass_criteria"
            elif line.startswith("**FAIL Indicators:**"):
                current_section = "fail_criteria"
            elif line.startswith("## 📊 Advancement Rules"):
                current_section = "advancement_rules"
            elif line and not line.startswith("#") and current_section:
                if current_section in ["skills", "prompts", "expected_responses"]:
                    if line.startswith("-") or line.startswith("1."):
                        data[current_section].append(line.lstrip("- 1234567890.").strip())
                else:
                    data[current_section] += line + " "
        
        return data
    
    def _get_default_stage_data(self, module: str, stage: str) -> Dict[str, Any]:
        """Get default curriculum data for missing files"""
        return {
            "goal": f"Practice {module} skills at {stage} level",
            "skills": [f"Basic {module} {stage} skills"],
            "prompts": [f"Let's practice {module} at {stage} level"],
            "expected_responses": ["Student engagement with the topic"],
            "pass_criteria": "Shows understanding and engagement",
            "fail_criteria": "No response or confusion",
            "advancement_rules": "3 passes out of 5 attempts"
        }
    
    def get_user_stage(self, phone_number: str, module: str) -> str:
        """Get current curriculum stage for user in specific module"""
        context = redis_service.get_user_context(phone_number)
        user_stages = context.get("curriculum_stages", {})
        return user_stages.get(module, "remember")
    
    def set_user_stage(self, phone_number: str, module: str, stage: str):
        """Set curriculum stage for user in specific module"""
        context = redis_service.get_user_context(phone_number)
        curriculum_stages = context.setdefault("curriculum_stages", {})
        curriculum_stages[module] = stage
        redis_service.set_user_context(phone_number, context)
    
    def get_curriculum_prompt(self, module: str, stage: str, user_context: Dict[str, Any]) -> str:
        """Generate curriculum-aware system prompt for LLM"""
        curriculum = self.curriculum_data.get(module, {}).get(stage, {})
        user_name = user_context.get("user_name", "friend")
        
        prompt = f"""
Module: {module.title()}
Stage: {stage.title()} (Bloom's Taxonomy)
Student: {user_name}
Goal: {curriculum.get('goal', '')}

Key Skills to Practice:
{chr(10).join(f"- {skill}" for skill in curriculum.get('skills', []))}

Teaching Approach:
- Use warm, encouraging tone with African cultural context
- Keep responses under 2 sentences for phone interaction
- Focus on meaning over perfect grammar
- Provide gentle corrections when needed
- Use Rwandan examples and cultural references
- Encourage effort and progress

Assessment Focus:
- {curriculum.get('pass_criteria', 'Understanding and engagement')}

Temperature Setting: Based on conversation state (intro=0.4, normal=0.9, assessment=0.2, facts=1.6)
"""
        return prompt
    
    async def assess_student_response(self, user_input: str, module: str, stage: str, 
                                    expected_type: str = "general") -> Dict[str, Any]:
        """Comprehensive assessment of student response"""
        
        curriculum = self.curriculum_data.get(module, {}).get(stage, {})
        
        keyword_score = self._assess_keywords(user_input, curriculum, expected_type)
        
        structure_score = self._assess_sentence_structure(user_input)
        
        llm_score = await self._assess_with_llm(user_input, curriculum, expected_type)
        
        final_score = (
            keyword_score * self.scoring_weights["keyword_match"] +
            structure_score * self.scoring_weights["sentence_structure"] +
            llm_score * self.scoring_weights["llm_evaluation"]
        )
        
        pass_threshold = 0.6
        is_pass = final_score >= pass_threshold
        
        return {
            "overall_score": final_score,
            "is_pass": is_pass,
            "keyword_score": keyword_score,
            "structure_score": structure_score,
            "llm_score": llm_score,
            "feedback": self._generate_feedback(final_score, is_pass, curriculum),
            "next_action": self._determine_next_action(is_pass, stage)
        }
    
    def _assess_keywords(self, user_input: str, curriculum: Dict[str, Any], expected_type: str) -> float:
        """Assess response based on keyword matching"""
        if not user_input:
            return 0.0
        
        user_input_lower = user_input.lower()
        expected_responses = curriculum.get("expected_responses", [])
        
        if not expected_responses:
            return 0.5
        
        total_keywords = 0
        matched_keywords = 0
        
        for expected in expected_responses:
            words = expected.lower().split()
            for word in words:
                if len(word) > 3:
                    total_keywords += 1
                    if word in user_input_lower:
                        matched_keywords += 1
        
        if total_keywords == 0:
            return 0.5
        
        return min(1.0, matched_keywords / total_keywords * 2)
    
    def _assess_sentence_structure(self, user_input: str) -> float:
        """Assess basic sentence structure and completeness"""
        if not user_input:
            return 0.0
        
        user_input = user_input.strip()
        
        score = 0.0
        
        if len(user_input) > 0:
            score += 0.2
        
        if len(user_input.split()) > 1:
            score += 0.3
        
        if 3 <= len(user_input.split()) <= 20:
            score += 0.2
        
        if any(word in user_input.lower() for word in ["i", "you", "we", "they", "is", "are", "was", "were"]):
            score += 0.2
        
        if user_input.endswith(('.', '!', '?')) or len(user_input.split()) >= 4:
            score += 0.1
        
        return min(1.0, score)
    
    async def _assess_with_llm(self, user_input: str, curriculum: Dict[str, Any], expected_type: str) -> float:
        """Use LLM to assess response quality and appropriateness"""
        try:
            assessment_prompt = f"""
            Assess this student response for a {expected_type} task:
            
            Student Response: "{user_input}"
            
            Expected Skills: {', '.join(curriculum.get('skills', []))}
            Pass Criteria: {curriculum.get('pass_criteria', '')}
            
            Rate the response on a scale of 0.0 to 1.0 based on:
            - Relevance to the task
            - Demonstration of expected skills
            - Effort and engagement shown
            - Appropriateness for the learning stage
            
            Be encouraging and focus on meaning over perfect grammar.
            Respond with just a number between 0.0 and 1.0.
            """
            
            messages = [{"role": "user", "content": assessment_prompt}]
            
            if settings.use_llama:
                response = await llama_service.generate_response(messages, "assessment", "assessment")
            else:
                response = await openai_service.generate_response(messages, "assessment")
            
            try:
                score = float(response.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.5
                
        except Exception as e:
            print(f"Error in LLM assessment: {e}")
            return 0.5
    
    def _generate_feedback(self, score: float, is_pass: bool, curriculum: Dict[str, Any]) -> str:
        """Generate encouraging feedback based on assessment"""
        if is_pass:
            if score >= 0.9:
                return "Excellent work! You're mastering this level beautifully."
            elif score >= 0.8:
                return "Great job! You're showing strong understanding."
            else:
                return "Good effort! You're making solid progress."
        else:
            if score >= 0.4:
                return "You're on the right track. Let's try once more together."
            else:
                return "No worries! Let's break this down step by step."
    
    def _determine_next_action(self, is_pass: bool, current_stage: str) -> str:
        """Determine next action based on assessment result"""
        if is_pass:
            return "continue"
        else:
            return "retry"
    
    def check_stage_advancement(self, phone_number: str, module: str) -> Optional[str]:
        """Check if student should advance to next stage"""
        context = redis_service.get_user_context(phone_number)
        assessment_history = context.get("assessment_history", {})
        module_history = assessment_history.get(module, [])
        
        if len(module_history) < 3:
            return None
        
        recent_attempts = module_history[-5:]
        passes = sum(1 for attempt in recent_attempts if attempt.get("is_pass", False))
        
        current_stage = self.get_user_stage(phone_number, module)
        current_index = self.bloom_stages.index(current_stage)
        
        if passes >= 3 and current_index < len(self.bloom_stages) - 1:
            next_stage = self.bloom_stages[current_index + 1]
            self.set_user_stage(phone_number, module, next_stage)
            return next_stage
        
        if len(recent_attempts) >= 3:
            recent_failures = all(not attempt.get("is_pass", True) for attempt in recent_attempts[-3:])
            if recent_failures and current_index > 0:
                prev_stage = self.bloom_stages[current_index - 1]
                self.set_user_stage(phone_number, module, prev_stage)
                return prev_stage
        
        return None
    
    def log_assessment(self, phone_number: str, module: str, stage: str, assessment_result: Dict[str, Any]):
        """Log assessment result for tracking progress"""
        context = redis_service.get_user_context(phone_number)
        assessment_history = context.setdefault("assessment_history", {})
        module_history = assessment_history.setdefault(module, [])
        
        assessment_record = {
            "timestamp": str(datetime.utcnow()),
            "stage": stage,
            "score": assessment_result["overall_score"],
            "is_pass": assessment_result["is_pass"],
            "feedback": assessment_result["feedback"]
        }
        
        module_history.append(assessment_record)
        
        if len(module_history) > 20:
            module_history[:] = module_history[-20:]
        
        redis_service.set_user_context(phone_number, context)

curriculum_service = CurriculumService()
