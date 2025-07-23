import random
from typing import Dict, Any
from app.services.openai_service import openai_service

class MathModule:
    def __init__(self):
        self.module_name = "math"
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process mental math input"""
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["exit", "quit", "stop", "back", "menu", "hello", "hi"]):
            user_context.setdefault("user_state", {})["current_math_problem"] = None
            user_context["user_state"]["requested_module"] = "general"
            return "Returning to main menu. How can I help you today?"
        
        if any(word in user_input_lower for word in ["new", "another", "next", "problem", "question"]):
            return self._generate_math_problem(user_context)
        
        current_problem = user_context.get("user_state", {}).get("current_math_problem")
        if current_problem:
            return await self._check_math_answer(user_input, current_problem, user_context)
        
        return self._generate_math_problem(user_context)
    
    def _generate_math_problem(self, user_context: Dict[str, Any]) -> str:
        """Generate a new math problem"""
        
        level = user_context.get("user_state", {}).get("math_level", "easy")
        
        if level == "easy":
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            operation = random.choice(["+", "-"])
        elif level == "medium":
            num1 = random.randint(10, 100)
            num2 = random.randint(10, 100)
            operation = random.choice(["+", "-", "*"])
        else:  # hard
            num1 = random.randint(50, 500)
            num2 = random.randint(10, 50)
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
        
        try:
            user_answer = float(''.join(filter(lambda x: x.isdigit() or x == '.', user_input)))
            correct_answer = current_problem["answer"]
            
            is_correct = abs(user_answer - correct_answer) < 0.01
            
            user_stats = user_context.get("user_state", {})
            user_stats["math_problems_attempted"] = user_stats.get("math_problems_attempted", 0) + 1
            
            if is_correct:
                user_stats["math_problems_correct"] = user_stats.get("math_problems_correct", 0) + 1
                
                accuracy = user_stats["math_problems_correct"] / user_stats["math_problems_attempted"]
                if accuracy > 0.8 and user_stats["math_problems_attempted"] >= 5:
                    current_level = user_stats.get("math_level", "easy")
                    if current_level == "easy":
                        user_stats["math_level"] = "medium"
                        level_up_msg = " Great job! I'm moving you to medium level problems."
                    elif current_level == "medium":
                        user_stats["math_level"] = "hard"
                        level_up_msg = " Excellent! I'm moving you to hard level problems."
                    else:
                        level_up_msg = ""
                else:
                    level_up_msg = ""
                
                user_stats["current_math_problem"] = None
                
                return f"Correct! The answer is {correct_answer}.{level_up_msg} Would you like another problem?"
            
            else:
                messages = [
                    {"role": "user", "content": f"The user answered {user_answer} for the problem {current_problem['question']}, but the correct answer is {correct_answer}. Give them a helpful hint to solve it correctly."}
                ]
                
                hint = await openai_service.generate_response(messages, self.module_name)
                return f"Not quite right. {hint} Try again: What is {current_problem['question']}?"
        
        except ValueError:
            return f"I couldn't understand your answer. Please give me a number for: What is {current_problem['question']}?"
    
    def get_welcome_message(self) -> str:
        """Get welcome message for Math module"""
        return "Welcome to Mental Math! I'll give you arithmetic problems to solve. Say 'new problem' to get started, or just tell me you're ready!"

math_module = MathModule()
