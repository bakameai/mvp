import random
from typing import Dict, Any
from app.services.openai_service import openai_service
from app.services.llama_service import llama_service
from app.config import settings

class ComprehensionModule:
    def __init__(self):
        self.module_name = "comprehension"
        self.sample_stories = [
            {
                "title": "The Community Garden in Kigali",
                "content": "Uwimana lived in a neighborhood in Kigali where many families struggled to afford fresh vegetables. She noticed an empty plot of land near her home and had an idea. She spoke to her neighbors about starting a community garden where everyone could grow vegetables together. At first, only a few families joined, but as the garden flourished with tomatoes, beans, and cabbage, more neighbors wanted to participate. They shared the harvest equally, and no family went without fresh food. The garden became a place where children learned about farming and neighbors strengthened their bonds through Ubuntu - the spirit of togetherness.",
                "questions": [
                    "What problem did Uwimana notice in her neighborhood?",
                    "What solution did she propose?",
                    "How did the community garden help beyond just providing food?"
                ],
                "answers": [
                    "Many families struggled to afford fresh vegetables",
                    "Starting a community garden where everyone could grow vegetables together",
                    "It became a place where children learned farming and neighbors strengthened bonds through Ubuntu"
                ]
            },
            {
                "title": "The Mobile Money Innovation",
                "content": "Jean-Baptiste was a young entrepreneur in Butare who noticed that many people in rural areas had difficulty accessing banking services. He developed a mobile money system that allowed people to send and receive money using their basic phones. His innovation helped farmers sell their crops to buyers in Kigali without traveling long distances, and families could support each other across the country. The system became so successful that it was adopted throughout Rwanda and even in neighboring countries. Jean-Baptiste's solution showed how technology could bridge gaps and connect communities.",
                "questions": [
                    "What challenge did Jean-Baptiste identify?",
                    "How did his mobile money system help farmers?",
                    "What does this story show about technology's role?"
                ],
                "answers": [
                    "People in rural areas had difficulty accessing banking services",
                    "It allowed farmers to sell crops to buyers in Kigali without traveling long distances",
                    "Technology can bridge gaps and connect communities"
                ]
            },
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
            }
        ]
    
    async def process_input(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """Process comprehension learning input"""
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["exit", "quit", "stop", "back", "menu", "hello", "hi"]):
            user_context.setdefault("user_state", {})["current_story"] = None
            user_context["user_state"]["current_question_index"] = 0
            user_context["user_state"]["requested_module"] = "general"
            return "Returning to main menu. How can I help you today?"
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
        
        if settings.use_llama:
            evaluation = await llama_service.generate_response(messages, self.module_name)
        else:
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
        return "Muraho, fellow story lover! 📚✨ I'm excited to share wonderful tales that reflect our beautiful Rwandan culture and values like Ubuntu, unity, and community support. Stories teach us about life, wisdom, and our rich heritage from the hills of Rwanda to our modern cities. Ready to explore some tales together? Just say 'new story' and we'll begin our literary adventure!"

comprehension_module = ComprehensionModule()
