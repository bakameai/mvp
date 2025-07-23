import random
from typing import Dict, Any
from app.services.openai_service import openai_service

class ComprehensionModule:
    def __init__(self):
        self.module_name = "comprehension"
        self.sample_stories = [
            {
                "title": "The Helpful Neighbor",
                "content": "Maria lived next to an elderly man named Mr. Johnson. Every morning, she noticed he struggled to carry his groceries up the stairs. One day, Maria decided to help him. She carried his bags and even helped him organize his kitchen. Mr. Johnson was so grateful that he baked her favorite cookies as a thank you gift.",
                "questions": [
                    "Who did Maria help?",
                    "What did Maria help Mr. Johnson with?",
                    "How did Mr. Johnson show his gratitude?"
                ],
                "answers": [
                    "Mr. Johnson (or the elderly man)",
                    "Carrying groceries and organizing his kitchen",
                    "He baked her favorite cookies"
                ]
            },
            {
                "title": "The Lost Wallet",
                "content": "Tom found a wallet on the street with $200 and an ID card inside. He could have kept the money, but instead he looked up the owner's address and returned it. The owner, Mrs. Chen, was so happy because the wallet contained her late husband's photo. She offered Tom a reward, but he politely declined.",
                "questions": [
                    "How much money was in the wallet?",
                    "Why was the wallet especially important to Mrs. Chen?",
                    "Did Tom accept a reward?"
                ],
                "answers": [
                    "$200",
                    "It contained her late husband's photo",
                    "No, he politely declined"
                ]
            }
        ]
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process comprehension learning input"""
        
        user_input_lower = user_input.lower()
        current_story = user_context.get("user_state", {}).get("current_story")
        current_question_index = user_context.get("user_state", {}).get("current_question_index", 0)
        
        if any(word in user_input_lower for word in ["new", "another", "next", "story"]):
            return self._start_new_story(user_context)
        
        if current_story and current_question_index < len(current_story.get("questions", [])):
            return await self._check_comprehension_answer(user_input, current_story, current_question_index, user_context)
        
        return self._start_new_story(user_context)
    
    def _start_new_story(self, user_context: Dict[str, Any]) -> str:
        """Start a new comprehension story"""
        
        story = random.choice(self.sample_stories)
        
        user_context.setdefault("user_state", {})["current_story"] = story
        user_context["user_state"]["current_question_index"] = 0
        user_context["user_state"]["comprehension_score"] = 0
        
        return f"Here's a short story for you:\n\n{story['title']}\n\n{story['content']}\n\nNow I'll ask you some questions about the story. Ready? {story['questions'][0]}"
    
    async def _check_comprehension_answer(self, user_input: str, current_story: Dict, question_index: int, user_context: Dict[str, Any]) -> str:
        """Check comprehension answer and provide feedback"""
        
        correct_answer = current_story["answers"][question_index]
        question = current_story["questions"][question_index]
        
        messages = [
            {"role": "user", "content": f"Question: {question}\nCorrect answer: {correct_answer}\nUser's answer: {user_input}\n\nIs the user's answer correct? Consider variations in wording. Respond with 'CORRECT' or 'INCORRECT' followed by brief feedback."}
        ]
        
        evaluation = await openai_service.generate_response(messages, self.module_name)
        is_correct = "CORRECT" in evaluation.upper()
        
        user_stats = user_context.get("user_state", {})
        
        if is_correct:
            user_stats["comprehension_score"] = user_stats.get("comprehension_score", 0) + 1
            feedback = "Correct! " + evaluation.replace("CORRECT", "").strip()
        else:
            feedback = "Not quite. " + evaluation.replace("INCORRECT", "").strip()
        
        next_question_index = question_index + 1
        
        if next_question_index < len(current_story["questions"]):
            user_stats["current_question_index"] = next_question_index
            next_question = current_story["questions"][next_question_index]
            return f"{feedback}\n\nNext question: {next_question}"
        else:
            total_questions = len(current_story["questions"])
            score = user_stats.get("comprehension_score", 0)
            
            user_stats["current_story"] = None
            user_stats["current_question_index"] = 0
            
            user_stats["comprehension_stories_completed"] = user_stats.get("comprehension_stories_completed", 0) + 1
            user_stats["comprehension_total_score"] = user_stats.get("comprehension_total_score", 0) + score
            
            return f"{feedback}\n\nStory completed! You got {score} out of {total_questions} questions correct. Would you like to try another story?"
    
    def get_welcome_message(self) -> str:
        """Get welcome message for Comprehension module"""
        return "Welcome to Reading Comprehension! I'll share short stories with you and then ask questions to test your understanding. Say 'new story' to get started!"

comprehension_module = ComprehensionModule()
