import random
from typing import Dict, Any
from app.services.openai_service import openai_service
from app.services.llama_service import llama_service
from app.services.emotional_intelligence_service import emotional_intelligence_service
from app.services.gamification_service import gamification_service
from app.services.multimodal_service import multimodal_service
from app.config import settings

class MathModule:
    def __init__(self):
        self.module_name = "math"
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process mental math input with multimodal adaptation"""
        
        phone_number = user_context.get("phone_number", "")
        learning_style = await multimodal_service.detect_learning_style(phone_number, user_context.get("conversation_history", []))
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["exit", "quit", "stop", "back", "menu", "hello", "hi"]):
            user_context.setdefault("user_state", {})["current_math_problem"] = None
            user_context["user_state"]["requested_module"] = "general"
            return "Returning to main menu. How can I help you today?"
        
        if any(word in user_input_lower for word in ["bye", "goodbye", "done"]):
            return f"Want to keep learning or stop for now? You did great today, {user_context.get('user_name', 'friend')}. I'll be here next time you call."
        
        if any(word in user_input_lower for word in ["new", "another", "next", "problem", "question"]):
            return await self._generate_math_problem(user_context)
        
        current_problem = user_context.get("user_state", {}).get("current_math_problem")
        if current_problem:
            return await self._check_math_answer(user_input, current_problem, user_context)
        
        return await self._evaluation_based_tutoring(user_input, user_context)
    
    async def _evaluation_based_tutoring(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Math tutoring using evaluation engine assessment"""
        
        from app.services.evaluation_engine import evaluation_engine
        phone_number = user_context.get("phone_number", "")
        current_stage = user_context.get("curriculum_stage", "remember")
        
        if not user_context.get("evaluation_prompt_given"):
            ivr_prompt = evaluation_engine.get_ivr_prompt("math", current_stage, user_context)
            user_context["evaluation_prompt_given"] = True
            return ivr_prompt
        
        evaluation = await evaluation_engine.evaluate_response(
            user_input, "math", current_stage, user_context
        )
        
        evaluation_engine.log_evaluation(phone_number, "math", current_stage, evaluation, user_input)
        advancement = evaluation_engine.check_advancement(phone_number, "math")
        
        response = evaluation["feedback"]
        if advancement:
            response += f"\n\nExcellent progress! You've advanced to {advancement} level! 🔢"
        
        user_context["evaluation_prompt_given"] = False
        return response
    
    async def _generate_math_problem(self, user_context: Dict[str, Any]) -> str:
        """Generate a new math problem - dynamic generation or static fallback"""
        
        user_stats = user_context.get("user_state", {})
        problems_completed = user_stats.get("math_problems_attempted", 0)
        
        if problems_completed >= 3:
            dynamic_problem = await self._generate_dynamic_problem(user_context)
            if dynamic_problem:
                user_context.setdefault("user_state", {})["current_math_problem"] = dynamic_problem
                return f"Here's a Rwanda-specific math problem: {dynamic_problem['question']} Please give me your answer."
        
        level = user_context.get("user_state", {}).get("math_level", "basic")
        
        if level == "basic":
            num1 = random.randint(1, 9)
            num2 = random.randint(1, 9)
            operation = random.choice(["+", "-"])
        elif level == "easy":
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            operation = random.choice(["+", "-"])
        elif level == "medium":
            num1 = random.randint(10, 100)
            num2 = random.randint(10, 100)
            operation = random.choice(["+", "-", "*"])
        elif level == "hard":
            num1 = random.randint(50, 500)
            num2 = random.randint(10, 50)
            operation = random.choice(["+", "-", "*", "/"])
        else:  # complex abacus
            num1 = random.randint(100, 1000)
            num2 = random.randint(50, 200)
            operation = random.choice(["+", "-", "*", "/"])
        
        if operation == "+":
            answer = num1 + num2
        elif operation == "-":
            answer = num1 - num2
        elif operation == "*":
            answer = num1 * num2
        else:  # division
            answer = round(num1 / num2, 2)
        
        problem = {
            "question": f"{num1} {operation} {num2}",
            "answer": answer,
            "num1": num1,
            "num2": num2,
            "operation": operation
        }
        
        user_context.setdefault("user_state", {})["current_math_problem"] = problem
        
        return f"Here's your math problem: What is {num1} {operation} {num2}? Please give me your answer."
    
    async def _check_math_answer(self, user_input: str, current_problem: Dict, user_context: Dict[str, Any]) -> str:
        """Check if the user's answer is correct"""
        
        emotion_data = await emotional_intelligence_service.detect_emotion(user_input)
        emotional_intelligence_service.track_emotional_journey(user_context, emotion_data)
        
        try:
            user_answer = float(''.join(filter(lambda x: x.isdigit() or x == '.', user_input)))
            correct_answer = current_problem["answer"]
            
            is_correct = abs(user_answer - correct_answer) < 0.01
            
            user_stats = user_context.get("user_state", {})
            user_stats["math_problems_attempted"] = user_stats.get("math_problems_attempted", 0) + 1
            
            current_level = user_stats.get("math_level", "basic")
            points_earned = gamification_service.update_progress(
                user_context, "correct_answer" if is_correct else "incorrect_answer", 
                self.module_name, is_correct, current_level
            )
            
            if is_correct:
                user_stats["math_problems_correct"] = user_stats.get("math_problems_correct", 0) + 1
                
                accuracy = user_stats["math_problems_correct"] / user_stats["math_problems_attempted"]
                if accuracy > 0.8 and user_stats["math_problems_attempted"] >= 5:
                    current_level = user_stats.get("math_level", "basic")
                    if current_level == "basic":
                        user_stats["math_level"] = "easy"
                        level_up_msg = " Great job! Moving to easy abacus level."
                    elif current_level == "easy":
                        user_stats["math_level"] = "medium"
                        level_up_msg = " Excellent! Moving to medium abacus level."
                    elif current_level == "medium":
                        user_stats["math_level"] = "hard"
                        level_up_msg = " Outstanding! Moving to hard abacus level."
                    elif current_level == "hard":
                        user_stats["math_level"] = "complex"
                        level_up_msg = " Amazing! Moving to complex abacus level."
                    else:
                        level_up_msg = ""
                else:
                    level_up_msg = ""
                
                user_stats["current_math_problem"] = None
                
                base_response = f"Correct! The answer is {correct_answer}.{level_up_msg}"
                
                new_achievements = gamification_service.check_achievements(user_context)
                if new_achievements:
                    achievement_msg = "\n\n" + "\n".join([ach["message"] for ach in new_achievements])
                    base_response += achievement_msg
                
                if points_earned > 0:
                    base_response += f"\n\n+{points_earned} points earned! 🌟"
                
                base_response += " Would you like another problem?"
                
                return await emotional_intelligence_service.generate_emotionally_aware_response(
                    user_input, base_response, emotion_data, self.module_name
                )
            
            else:
                messages = [
                    {"role": "user", "content": f"The user answered {user_answer} for the problem {current_problem['question']}, but the correct answer is {correct_answer}. Give them a helpful hint to solve it correctly."}
                ]
                
                if settings.use_llama:
                    hint = await llama_service.generate_response(
                        messages, self.module_name, "normal", user_context
                    )
                else:
                    hint = await openai_service.generate_response(messages, self.module_name)
                
                base_response = f"Not quite right. {hint} Try again: What is {current_problem['question']}?"
                
                return await emotional_intelligence_service.generate_emotionally_aware_response(
                    user_input, base_response, emotion_data, self.module_name
                )
        
        except ValueError:
            base_response = f"I couldn't understand your answer. Please give me a number for: What is {current_problem['question']}?"
            return await emotional_intelligence_service.generate_emotionally_aware_response(
                user_input, base_response, emotion_data, self.module_name
            )
    
    def get_welcome_message(self) -> str:
        """Get welcome message for Math module"""
        return "Muraho! 🧮✨ I'm excited to explore math together using Rwandan contexts! We'll work with Rwandan francs, calculate distances between our beautiful cities like Kigali and Butare, and solve problems that connect to daily life in Rwanda. Math helps build our nation's future in technology and development. Ready to strengthen those mental muscles? Byiza, let's start!"

    async def _generate_dynamic_problem(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new Rwanda-specific math problem using AI"""
        try:
            user_stats = user_context.get("user_state", {})
            problems_attempted = user_stats.get("math_problems_attempted", 0)
            problems_correct = user_stats.get("math_problems_correct", 0)
            
            if problems_attempted > 0:
                accuracy = problems_correct / problems_attempted
                if accuracy >= 0.8:
                    difficulty = "hard"
                elif accuracy >= 0.6:
                    difficulty = "medium"
                else:
                    difficulty = "easy"
            else:
                difficulty = "easy"
            
            problem_contexts = [
                "market transactions in Kigali using Rwandan francs (RWF)",
                "calculating distances between Rwandan cities (Kigali, Butare, Musanze, Gisenyi)",
                "agricultural calculations for coffee or tea farming",
                "construction projects for community buildings",
                "mobile money transactions and savings",
                "school supplies and educational costs",
                "transportation costs between provinces",
                "community development project budgets"
            ]
            
            context = random.choice(problem_contexts)
            
            messages = [
                {"role": "user", "content": f"Create a {difficulty}-level math problem about {context} in Rwanda. Include:\n\n1. A realistic scenario with Rwandan context\n2. A clear math question\n3. The correct numerical answer\n\nFormat as JSON: {{'question': 'A farmer in Musanze...', 'answer': 150, 'context': 'agricultural'}}"}
            ]
            
            if settings.use_llama:
                response = await llama_service.generate_response(
                    messages, self.module_name, "normal", user_context
                )
            else:
                response = await openai_service.generate_response(messages, self.module_name)
            
            import json
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response[start_idx:end_idx]
                    problem_data = json.loads(json_str)
                    
                    required_fields = ['question', 'answer']
                    if all(field in problem_data for field in required_fields):
                        return problem_data
                
            except json.JSONDecodeError:
                pass
            
            return None
            
        except Exception as e:
            print(f"Error generating dynamic math problem: {e}")
            return None

math_module = MathModule()
