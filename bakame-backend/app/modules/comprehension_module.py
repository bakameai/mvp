import random
from typing import Dict, Any
from app.services.openai_service import openai_service
from app.services.llama_service import llama_service
from app.services.emotional_intelligence_service import emotional_intelligence_service
from app.services.gamification_service import gamification_service
from app.services.predictive_analytics_service import predictive_analytics
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
            return await self._start_new_story(user_context)
        
        if current_story and current_question_index < len(current_story.get("questions", [])):
            return await self._check_comprehension_answer(user_input, current_story, current_question_index, user_context)
        
        return await self._start_new_story(user_context)
    
    async def _start_new_story(self, user_context: Dict[str, Any]) -> str:
        """Start a new comprehension story - dynamic generation or static fallback"""
        
        user_stats = user_context.get("user_state", {})
        stories_completed = user_stats.get("comprehension_stories_completed", 0)
        
        if stories_completed >= 2:
            dynamic_story = await self._generate_dynamic_story(user_context)
            if dynamic_story:
                user_context.setdefault("user_state", {})["current_story"] = dynamic_story
                user_context["user_state"]["current_question_index"] = 0
                user_context["user_state"]["comprehension_score"] = 0
                
                return f"Here's a fresh story for you:\n\n{dynamic_story['title']}\n\n{dynamic_story['content']}\n\nNow I'll ask you some questions about the story. Ready? {dynamic_story['questions'][0]}"
        
        story = random.choice(self.sample_stories)
        
        user_context.setdefault("user_state", {})["current_story"] = story
        user_context["user_state"]["current_question_index"] = 0
        user_context["user_state"]["comprehension_score"] = 0
        
        return f"Here's a short story for you:\n\n{story['title']}\n\n{story['content']}\n\nNow I'll ask you some questions about the story. Ready? {story['questions'][0]}"
    
    async def _check_comprehension_answer(self, user_input: str, current_story: Dict, question_index: int, user_context: Dict[str, Any]) -> str:
        """Check comprehension answer and provide feedback"""
        
        emotion_data = await emotional_intelligence_service.detect_emotion(user_input)
        emotional_intelligence_service.track_emotional_journey(user_context, emotion_data)
        
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
        
        points_earned = gamification_service.update_progress(
            user_context, "correct_answer" if is_correct else "incorrect_answer", 
            self.module_name, is_correct
        )
        
        if is_correct:
            user_stats["comprehension_score"] = user_stats.get("comprehension_score", 0) + 1
            feedback = "Correct! " + evaluation.replace("CORRECT", "").strip()
        else:
            feedback = "Not quite. " + evaluation.replace("INCORRECT", "").strip()
        
        next_question_index = question_index + 1
        
        if next_question_index < len(current_story["questions"]):
            user_stats["current_question_index"] = next_question_index
            next_question = current_story["questions"][next_question_index]
            base_response = f"{feedback}\n\nNext question: {next_question}"
            
            return await emotional_intelligence_service.generate_emotionally_aware_response(
                user_input, base_response, emotion_data, self.module_name
            )
        else:
            total_questions = len(current_story["questions"])
            score = user_stats.get("comprehension_score", 0)
            
            user_stats["current_story"] = None
            user_stats["current_question_index"] = 0
            
            user_stats["comprehension_stories_completed"] = user_stats.get("comprehension_stories_completed", 0) + 1
            user_stats["comprehension_total_score"] = user_stats.get("comprehension_total_score", 0) + score
            
            gamification_service.update_progress(user_context, "completed_story", self.module_name)
            
            base_response = f"{feedback}\n\nStory completed! You got {score} out of {total_questions} questions correct."
            
            new_achievements = gamification_service.check_achievements(user_context)
            if new_achievements:
                achievement_msg = "\n\n" + "\n".join([ach["message"] for ach in new_achievements])
                base_response += achievement_msg
            
            if points_earned > 0:
                base_response += f"\n\n+{points_earned} points earned! 🌟"
            
            base_response += " Would you like to try another story?"
            
            return await emotional_intelligence_service.generate_emotionally_aware_response(
                user_input, base_response, emotion_data, self.module_name
            )
    
    async def _generate_dynamic_story(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new Rwanda-specific story using AI"""
        try:
            user_stats = user_context.get("user_state", {})
            stories_completed = user_stats.get("comprehension_stories_completed", 0)
            total_score = user_stats.get("comprehension_total_score", 0)
            
            if stories_completed > 0:
                avg_score = total_score / stories_completed
                if avg_score >= 0.8:
                    difficulty = "advanced"
                elif avg_score >= 0.6:
                    difficulty = "intermediate"
                else:
                    difficulty = "basic"
            else:
                difficulty = "basic"
            
            story_themes = [
                "community cooperation and Ubuntu philosophy",
                "innovation and technology in modern Rwanda",
                "environmental conservation in the Land of a Thousand Hills",
                "education and youth empowerment",
                "cultural traditions meeting modern life",
                "entrepreneurship and economic development",
                "unity and reconciliation",
                "agricultural innovation and food security"
            ]
            
            theme = random.choice(story_themes)
            
            messages = [
                {"role": "user", "content": f"Create a {difficulty}-level comprehension story about {theme} set in Rwanda. Include:\n\n1. A compelling title\n2. A 150-200 word story featuring Rwandan characters, places (like Kigali, Butare, Musanze), and cultural elements\n3. Exactly 3 comprehension questions that test understanding\n4. Clear answers for each question\n\nFormat as JSON: {{'title': 'Story Title', 'content': 'Story text...', 'questions': ['Q1', 'Q2', 'Q3'], 'answers': ['A1', 'A2', 'A3']}}"}
            ]
            
            if settings.use_llama:
                response = await llama_service.generate_response(messages, self.module_name)
            else:
                response = await openai_service.generate_response(messages, self.module_name)
            
            import json
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response[start_idx:end_idx]
                    story_data = json.loads(json_str)
                    
                    required_fields = ['title', 'content', 'questions', 'answers']
                    if all(field in story_data for field in required_fields):
                        if len(story_data['questions']) == 3 and len(story_data['answers']) == 3:
                            return story_data
                
            except json.JSONDecodeError:
                pass
            
            return None
            
        except Exception as e:
            print(f"Error generating dynamic story: {e}")
            return None
    
    def get_welcome_message(self) -> str:
        """Get welcome message for Comprehension module"""
        return "Muraho, fellow story lover! 📚✨ I'm excited to share wonderful tales that reflect our beautiful Rwandan culture and values like Ubuntu, unity, and community support. Stories teach us about life, wisdom, and our rich heritage from the hills of Rwanda to our modern cities. Ready to explore some tales together? Just say 'new story' and we'll begin our literary adventure!"

comprehension_module = ComprehensionModule()
