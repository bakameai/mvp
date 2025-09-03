import os
import yaml
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from app.services.llama_service import llama_service
from app.services.openai_service import openai_service
from app.services.redis_service import redis_service
from app.services.mcp_client import mcp_client
from app.config import settings

class EvaluationEngine:
    def __init__(self):
        self.modules = ["grammar", "composition", "math", "debate", "comprehension"]
        self.bloom_stages = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        self.evaluation_schemas = self._load_evaluation_schemas()
        
    def _load_evaluation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load YAML evaluation schemas from curriculum folders"""
        schemas = {}
        
        for module in self.modules:
            schemas[module] = {}
            for stage in self.bloom_stages:
                yaml_path = f"/home/ubuntu/repos/mvp/bakame-backend/docs/curriculum/{module}/{stage}.yaml"
                if os.path.exists(yaml_path):
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        schemas[module][stage] = yaml.safe_load(f)
                else:
                    schemas[module][stage] = self._get_default_schema(module, stage)
        
        return schemas
    
    def _get_default_schema(self, module: str, stage: str) -> Dict[str, Any]:
        """Generate default evaluation schema for missing YAML files"""
        return {
            "stage": stage,
            "module": module,
            "goal": f"Practice {module} skills at {stage} level",
            "ivr_prompt": f"Let's practice {module} at the {stage} level. Please respond with your thoughts.",
            "expected_structure": ["≥1 complete response", "engagement with topic"],
            "llm_scoring_criteria": {
                "temperature": 0.2,
                "rules": ["shows understanding", "demonstrates effort"]
            },
            "keywords": {
                "positive": ["yes", "good", "understand"],
                "negative": ["no", "don't know", "confused"]
            },
            "feedback_templates": {
                "pass": "Good work! You're making progress.",
                "fail_hint": "Let's try thinking about this differently.",
                "fail_repeat": "Good effort! Let's practice this again.",
                "encouragement": "Learning takes time. You're doing well!"
            },
            "emotional_responses": {
                "hesitation": "Take your time to think about it.",
                "confusion": "Let me help you understand this better.",
                "frustration": "Don't worry, this is challenging for everyone."
            },
            "advancement_criteria": {
                "pass_threshold": 0.6,
                "advancement_rule": "3 passes out of 5 attempts",
                "demotion_rule": "3 consecutive failures"
            },
            "assessment_weights": {
                "keyword_match": 0.4,
                "sentence_structure": 0.3,
                "llm_evaluation": 0.3
            }
        }
    
    def get_ivr_prompt(self, module: str, stage: str, user_context: Dict[str, Any]) -> str:
        """Get IVR-ready prompt for current module and stage"""
        schema = self.evaluation_schemas.get(module, {}).get(stage, {})
        user_name = user_context.get("user_name", "friend")
        
        prompt = schema.get("ivr_prompt", f"Let's practice {module} at {stage} level.")
        
        if user_name and user_name != "friend":
            prompt = f"Hello {user_name}! " + prompt
        
        return prompt
    
    async def evaluate_response(self, user_input: str, module: str, stage: str, 
                              user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive multi-stage evaluation of student response"""
        
        schema = self.evaluation_schemas.get(module, {}).get(stage, {})
        
        if not schema:
            return self._get_default_evaluation(user_input)
        
        keyword_score = self._evaluate_keywords(user_input, schema)
        structure_score = self._evaluate_structure(user_input, schema)
        llm_score = await self._evaluate_with_llm(user_input, schema)
        
        weights = schema.get("assessment_weights", {
            "keyword_match": 0.4,
            "sentence_structure": 0.3,
            "llm_evaluation": 0.3
        })
        
        final_score = (
            keyword_score * weights.get("keyword_match", 0.4) +
            structure_score * weights.get("sentence_structure", 0.3) +
            llm_score * weights.get("llm_evaluation", 0.3)
        )
        
        pass_threshold = schema.get("advancement_criteria", {}).get("pass_threshold", 0.6)
        is_pass = final_score >= pass_threshold
        
        emotional_state = await self._detect_emotional_state(user_input, user_context)
        feedback = self._select_feedback(is_pass, emotional_state, schema)
        
        return {
            "overall_score": final_score,
            "is_pass": is_pass,
            "keyword_score": keyword_score,
            "structure_score": structure_score,
            "llm_score": llm_score,
            "emotional_state": emotional_state,
            "feedback": feedback,
            "next_action": "continue" if is_pass else "retry",
            "schema_used": f"{module}_{stage}"
        }
    
    def _evaluate_keywords(self, user_input: str, schema: Dict[str, Any]) -> float:
        """Evaluate response based on positive/negative keywords"""
        if not user_input:
            return 0.0
        
        user_input_lower = user_input.lower()
        keywords = schema.get("keywords", {})
        positive_keywords = keywords.get("positive", [])
        negative_keywords = keywords.get("negative", [])
        
        positive_matches = sum(1 for keyword in positive_keywords if keyword in user_input_lower)
        negative_matches = sum(1 for keyword in negative_keywords if keyword in user_input_lower)
        
        if not positive_keywords and not negative_keywords:
            return 0.5
        
        total_possible = len(positive_keywords) + len(negative_keywords)
        if total_possible == 0:
            return 0.5
        
        score = (positive_matches - negative_matches) / max(1, len(positive_keywords))
        return max(0.0, min(1.0, score + 0.5))
    
    def _evaluate_structure(self, user_input: str, schema: Dict[str, Any]) -> float:
        """Evaluate response structure against expected criteria"""
        if not user_input:
            return 0.0
        
        expected_structure = schema.get("expected_structure", [])
        score = 0.0
        
        sentences = user_input.split('.')
        sentence_count = len([s for s in sentences if s.strip()])
        word_count = len(user_input.split())
        
        for criterion in expected_structure:
            if "≥2 complete sentences" in criterion and sentence_count >= 2:
                score += 0.3
            elif "≥1 complete response" in criterion and word_count >= 3:
                score += 0.2
            elif "clear narrative flow" in criterion and sentence_count >= 2:
                score += 0.2
            elif "recognition of error" in criterion and any(word in user_input.lower() 
                for word in ["wrong", "incorrect", "mistake", "error"]):
                score += 0.3
        
        if word_count >= 5:
            score += 0.2
        
        return min(1.0, score)
    
    async def _evaluate_with_llm(self, user_input: str, schema: Dict[str, Any]) -> float:
        """Use LLM to evaluate response quality with schema-specific criteria"""
        try:
            criteria = schema.get("llm_scoring_criteria", {})
            rules = criteria.get("rules", [])
            temperature = criteria.get("temperature", 0.2)
            
            assessment_prompt = f"""
            Evaluate this student response for a {schema.get('module')} {schema.get('stage')} task:
            
            Student Response: "{user_input}"
            
            Goal: {schema.get('goal', '')}
            
            Evaluation Rules:
            {chr(10).join(f"- {rule}" for rule in rules)}
            
            Rate the response on a scale of 0.0 to 1.0 based on:
            - How well it meets the specific rules above
            - Effort and engagement shown
            - Appropriateness for the learning stage
            - Cultural sensitivity and context awareness
            
            Be encouraging and focus on meaning over perfect grammar.
            Respond with just a number between 0.0 and 1.0.
            """
            
            messages = [{"role": "user", "content": assessment_prompt}]
            
            if settings.use_llama:
                response = await llama_service.generate_response(
                    messages, "evaluation", "assessment"
                )
            else:
                response = await openai_service.generate_response(messages, "evaluation")
            
            try:
                score = float(response.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.5
                
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return 0.5
    
    async def _detect_emotional_state(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Detect student emotional state from input and context"""
        if not user_input:
            return "neutral"
        
        user_input_lower = user_input.lower()
        
        hesitation_markers = ["um", "uh", "hmm", "well", "i think", "maybe", "not sure"]
        confusion_markers = ["don't understand", "confused", "what", "huh", "don't know"]
        frustration_markers = ["hard", "difficult", "can't", "impossible", "give up", "tired"]
        
        if any(marker in user_input_lower for marker in frustration_markers):
            return "frustration"
        elif any(marker in user_input_lower for marker in confusion_markers):
            return "confusion"
        elif any(marker in user_input_lower for marker in hesitation_markers):
            return "hesitation"
        else:
            return "neutral"
    
    def _select_feedback(self, is_pass: bool, emotional_state: str, schema: Dict[str, Any]) -> str:
        """Select appropriate feedback based on performance and emotional state"""
        feedback_templates = schema.get("feedback_templates", {})
        emotional_responses = schema.get("emotional_responses", {})
        
        if emotional_state != "neutral" and emotional_state in emotional_responses:
            return emotional_responses[emotional_state]
        
        if is_pass:
            return feedback_templates.get("pass", "Good work! You're making progress.")
        else:
            if emotional_state == "frustration":
                return feedback_templates.get("encouragement", "Learning takes time. You're doing well!")
            elif emotional_state == "confusion":
                return feedback_templates.get("fail_hint", "Let's try thinking about this differently.")
            else:
                return feedback_templates.get("fail_repeat", "Good effort! Let's practice this again.")
    
    def _get_default_evaluation(self, user_input: str) -> Dict[str, Any]:
        """Fallback evaluation when no schema is available"""
        return {
            "overall_score": 0.5,
            "is_pass": False,
            "keyword_score": 0.5,
            "structure_score": 0.5,
            "llm_score": 0.5,
            "emotional_state": "neutral",
            "feedback": "Thank you for your response. Let's continue learning together.",
            "next_action": "continue",
            "schema_used": "default"
        }
    
    def log_evaluation(self, phone_number: str, module: str, stage: str, 
                      evaluation_result: Dict[str, Any], user_input: str):
        """Log detailed evaluation result for tracking and analytics"""
        context = redis_service.get_user_context(phone_number)
        evaluation_history = context.setdefault("evaluation_history", {})
        module_history = evaluation_history.setdefault(module, [])
        
        evaluation_record = {
            "timestamp": str(datetime.utcnow()),
            "stage": stage,
            "user_input": user_input[:200],  # Truncate for storage
            "overall_score": evaluation_result["overall_score"],
            "is_pass": evaluation_result["is_pass"],
            "emotional_state": evaluation_result["emotional_state"],
            "feedback": evaluation_result["feedback"],
            "schema_used": evaluation_result["schema_used"],
            "component_scores": {
                "keyword": evaluation_result["keyword_score"],
                "structure": evaluation_result["structure_score"],
                "llm": evaluation_result["llm_score"]
            }
        }
        
        module_history.append(evaluation_record)
        
        if len(module_history) > 50:
            module_history[:] = module_history[-50:]
        
        redis_service.set_user_context(phone_number, context)
        
        import asyncio
        asyncio.create_task(mcp_client.log_evaluation(
            phone_number=phone_number,
            module=module,
            stage=stage,
            user_input=user_input,
            overall_score=evaluation_result["overall_score"],
            is_pass=evaluation_result["is_pass"],
            emotional_state=evaluation_result["emotional_state"],
            feedback=evaluation_result["feedback"]
        ))
    
    def check_advancement(self, phone_number: str, module: str) -> Optional[str]:
        """Check if student should advance based on evaluation history"""
        context = redis_service.get_user_context(phone_number)
        evaluation_history = context.get("evaluation_history", {})
        module_history = evaluation_history.get(module, [])
        
        if len(module_history) < 3:
            return None
        
        recent_attempts = module_history[-5:]
        passes = sum(1 for attempt in recent_attempts if attempt.get("is_pass", False))
        
        current_stage = self._get_current_stage(phone_number, module)
        current_index = self.bloom_stages.index(current_stage)
        
        if passes >= 3 and current_index < len(self.bloom_stages) - 1:
            next_stage = self.bloom_stages[current_index + 1]
            self._set_current_stage(phone_number, module, next_stage)
            return next_stage
        
        if len(recent_attempts) >= 3:
            recent_failures = all(not attempt.get("is_pass", True) for attempt in recent_attempts[-3:])
            if recent_failures and current_index > 0:
                prev_stage = self.bloom_stages[current_index - 1]
                self._set_current_stage(phone_number, module, prev_stage)
                return prev_stage
        
        return None
    
    def _get_current_stage(self, phone_number: str, module: str) -> str:
        """Get current stage for user in specific module"""
        context = redis_service.get_user_context(phone_number)
        curriculum_stages = context.get("curriculum_stages", {})
        return curriculum_stages.get(module, "remember")
    
    def _set_current_stage(self, phone_number: str, module: str, stage: str):
        """Set current stage for user in specific module"""
        context = redis_service.get_user_context(phone_number)
        curriculum_stages = context.setdefault("curriculum_stages", {})
        curriculum_stages[module] = stage
        redis_service.set_user_context(phone_number, context)

evaluation_engine = EvaluationEngine()
