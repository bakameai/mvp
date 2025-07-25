import json
import base64
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from app.services.redis_service import redis_service
from app.services.logging_service import logging_service

class MultimodalService:
    """
    Phase 4: Multimodal Learning Service
    Supports audio, visual, and kinesthetic learning through SMS and voice
    """
    
    def __init__(self):
        self.learning_styles = ["visual", "auditory", "kinesthetic", "reading"]
        self.ascii_art_library = self._initialize_ascii_art()
        
    def _initialize_ascii_art(self) -> Dict[str, str]:
        """Initialize library of ASCII art for visual learning"""
        return {
            "triangle": """
    /\\
   /  \\
  /____\\
""",
            "square": """
  +----+
  |    |
  |    |
  +----+
""",
            "circle": """
   ***
  *   *
  *   *
   ***
""",
            "fraction_half": """
  1
  -
  2
""",
            "fraction_quarter": """
  1
  -
  4
""",
            "thermometer": """
  |===|
  | T |
  |   |
  |###|
  +---+
""",
            "plant_growth": """
Stage 1:  .
Stage 2:  |
Stage 3: \\|/
Stage 4: \\|/
         _|_
""",
            "water_cycle": """
☁️ Cloud
  ↓ Rain
🌊 Ocean → ☀️ Evaporation
""",
            "money": """
💰 Savings
+-----+
| 100 |
| RWF |
+-----+
"""
        }
    
    async def detect_learning_style(self, phone_number: str, interaction_history: List[Dict]) -> str:
        """Detect user's preferred learning style based on interaction patterns"""
        try:
            style_scores = {style: 0 for style in self.learning_styles}
            
            for interaction in interaction_history[-20:]:  # Last 20 interactions
                user_input = interaction.get("user_input", "").lower()
                response_time = interaction.get("response_time", 0)
                
                if any(word in user_input for word in ["show", "see", "picture", "draw", "visual"]):
                    style_scores["visual"] += 2
                
                if any(word in user_input for word in ["hear", "listen", "say", "sound", "voice"]):
                    style_scores["auditory"] += 2
                
                if any(word in user_input for word in ["do", "practice", "try", "hands", "move"]):
                    style_scores["kinesthetic"] += 2
                
                if any(word in user_input for word in ["read", "text", "write", "explain"]):
                    style_scores["reading"] += 2
                
                if response_time < 30:
                    style_scores["visual"] += 1
                    style_scores["kinesthetic"] += 1
                
                if response_time > 60:
                    style_scores["auditory"] += 1
                    style_scores["reading"] += 1
            
            dominant_style = max(style_scores, key=style_scores.get)
            
            style_key = f"learning_style:{phone_number}"
            redis_service.set(style_key, dominant_style)
            
            await logging_service.log_interaction(
                phone_number, "learning_style_detected", f"Detected style: {dominant_style}"
            )
            
            return dominant_style
            
        except Exception as e:
            await logging_service.log_error(f"Failed to detect learning style: {str(e)}")
            return "reading"  # Default fallback
    
    async def adapt_content_to_style(self, content: Dict[str, Any], learning_style: str, phone_number: str) -> Dict[str, Any]:
        """Adapt educational content to user's learning style"""
        try:
            adapted_content = content.copy()
            
            if learning_style == "visual":
                adapted_content = await self._adapt_for_visual_learner(adapted_content)
            elif learning_style == "auditory":
                adapted_content = await self._adapt_for_auditory_learner(adapted_content)
            elif learning_style == "kinesthetic":
                adapted_content = await self._adapt_for_kinesthetic_learner(adapted_content)
            elif learning_style == "reading":
                adapted_content = await self._adapt_for_reading_learner(adapted_content)
            
            await logging_service.log_interaction(
                phone_number, "content_adapted", f"Adapted for {learning_style} learning"
            )
            
            return adapted_content
            
        except Exception as e:
            await logging_service.log_error(f"Failed to adapt content: {str(e)}")
            return content
    
    async def _adapt_for_visual_learner(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content for visual learners using ASCII art and diagrams"""
        try:
            if content.get("type") == "math":
                topic = content.get("topic", "").lower()
                
                if "fraction" in topic:
                    if "half" in content.get("text", "").lower():
                        content["visual_aid"] = self.ascii_art_library["fraction_half"]
                    elif "quarter" in content.get("text", "").lower():
                        content["visual_aid"] = self.ascii_art_library["fraction_quarter"]
                
                elif "shape" in topic or "geometry" in topic:
                    if "triangle" in content.get("text", "").lower():
                        content["visual_aid"] = self.ascii_art_library["triangle"]
                    elif "square" in content.get("text", "").lower():
                        content["visual_aid"] = self.ascii_art_library["square"]
                    elif "circle" in content.get("text", "").lower():
                        content["visual_aid"] = self.ascii_art_library["circle"]
            
            elif content.get("type") == "science":
                topic = content.get("topic", "").lower()
                
                if "plant" in topic or "growth" in topic:
                    content["visual_aid"] = self.ascii_art_library["plant_growth"]
                elif "water" in topic or "cycle" in topic:
                    content["visual_aid"] = self.ascii_art_library["water_cycle"]
                elif "temperature" in topic:
                    content["visual_aid"] = self.ascii_art_library["thermometer"]
            
            elif content.get("type") == "economics":
                if "money" in content.get("text", "").lower() or "savings" in content.get("text", "").lower():
                    content["visual_aid"] = self.ascii_art_library["money"]
            
            content["presentation_style"] = "visual"
            content["instructions"] = "📊 Visual representation included below:"
            
            return content
            
        except Exception as e:
            await logging_service.log_error(f"Failed to adapt for visual learner: {str(e)}")
            return content
    
    async def _adapt_for_auditory_learner(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content for auditory learners with voice-friendly format"""
        try:
            if content.get("type") == "english":
                text = content.get("text", "")
                content["audio_hints"] = "🔊 Listen carefully to pronunciation when calling"
                content["voice_instructions"] = "Call +18554711896 to hear this lesson spoken aloud"
            
            if content.get("type") == "math":
                content["memory_aid"] = "🎵 Try saying the steps out loud to remember better"
            
            content["presentation_style"] = "auditory"
            content["voice_optimized"] = True
            content["instructions"] = "🎧 Best experienced through voice call"
            
            return content
            
        except Exception as e:
            await logging_service.log_error(f"Failed to adapt for auditory learner: {str(e)}")
            return content
    
    async def _adapt_for_kinesthetic_learner(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content for kinesthetic learners with hands-on activities"""
        try:
            if content.get("type") == "math":
                content["physical_activity"] = """
🤲 Try this with your hands:
- Count on your fingers
- Draw the problem in the air
- Walk while solving (1 step per number)
"""
            
            elif content.get("type") == "english":
                content["physical_activity"] = """
✋ Practice activities:
- Act out the words
- Write letters in the air
- Clap syllables in words
"""
            
            elif content.get("type") == "science":
                content["physical_activity"] = """
🔬 Hands-on experiment:
- Use objects around you
- Try the movements described
- Build a simple model
"""
            
            content["presentation_style"] = "kinesthetic"
            content["instructions"] = "🏃‍♂️ Get moving while learning!"
            
            return content
            
        except Exception as e:
            await logging_service.log_error(f"Failed to adapt for kinesthetic learner: {str(e)}")
            return content
    
    async def _adapt_for_reading_learner(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content for reading/writing learners with detailed text"""
        try:
            content["detailed_explanation"] = True
            content["reading_materials"] = "📚 Additional reading suggestions included"
            
            content["study_tips"] = """
📝 Study tips:
- Take notes while reading
- Summarize in your own words
- Create lists and outlines
"""
            
            content["presentation_style"] = "reading"
            content["instructions"] = "📖 Read carefully and take notes"
            
            return content
            
        except Exception as e:
            await logging_service.log_error(f"Failed to adapt for reading learner: {str(e)}")
            return content
    
    async def create_multimodal_lesson(self, topic: str, subject: str, phone_number: str) -> Dict[str, Any]:
        """Create a lesson that incorporates multiple learning modalities"""
        try:
            style_key = f"learning_style:{phone_number}"
            primary_style = redis_service.get(style_key) or "reading"
            
            lesson = {
                "topic": topic,
                "subject": subject,
                "primary_style": primary_style,
                "multimodal": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            lesson["visual_component"] = await self._create_visual_component(topic, subject)
            lesson["auditory_component"] = await self._create_auditory_component(topic, subject)
            lesson["kinesthetic_component"] = await self._create_kinesthetic_component(topic, subject)
            lesson["reading_component"] = await self._create_reading_component(topic, subject)
            
            lesson["presentation_order"] = self._determine_presentation_order(primary_style)
            
            await logging_service.log_interaction(
                phone_number, "multimodal_lesson_created", f"Created lesson for {topic}"
            )
            
            return lesson
            
        except Exception as e:
            await logging_service.log_error(f"Failed to create multimodal lesson: {str(e)}")
            return {"error": str(e)}
    
    async def _create_visual_component(self, topic: str, subject: str) -> Dict[str, Any]:
        """Create visual learning component"""
        return {
            "type": "visual",
            "ascii_art": self._get_relevant_ascii_art(topic),
            "diagrams": f"📊 Visual diagram for {topic}",
            "symbols": "Use symbols and charts to understand concepts",
            "colors": "🔴🟡🟢 Color-code different parts"
        }
    
    async def _create_auditory_component(self, topic: str, subject: str) -> Dict[str, Any]:
        """Create auditory learning component"""
        return {
            "type": "auditory",
            "voice_instructions": f"🎧 Call to hear {topic} explained",
            "rhythm": "🎵 Create a rhythm or song to remember",
            "discussion": "💬 Discuss with others",
            "repetition": "🔄 Repeat key points aloud"
        }
    
    async def _create_kinesthetic_component(self, topic: str, subject: str) -> Dict[str, Any]:
        """Create kinesthetic learning component"""
        return {
            "type": "kinesthetic",
            "hands_on": f"🤲 Practice {topic} with physical objects",
            "movement": "🚶‍♂️ Move while learning",
            "building": "🔨 Build or create something related",
            "experimentation": "🧪 Try different approaches"
        }
    
    async def _create_reading_component(self, topic: str, subject: str) -> Dict[str, Any]:
        """Create reading/writing learning component"""
        return {
            "type": "reading",
            "detailed_text": f"📚 Comprehensive explanation of {topic}",
            "note_taking": "📝 Take detailed notes",
            "summarizing": "📄 Write summaries",
            "research": "🔍 Read more about the topic"
        }
    
    def _get_relevant_ascii_art(self, topic: str) -> str:
        """Get ASCII art relevant to the topic"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ["triangle", "geometry", "shape"]):
            return self.ascii_art_library.get("triangle", "")
        elif any(word in topic_lower for word in ["square", "rectangle"]):
            return self.ascii_art_library.get("square", "")
        elif any(word in topic_lower for word in ["circle", "round"]):
            return self.ascii_art_library.get("circle", "")
        elif any(word in topic_lower for word in ["fraction", "half"]):
            return self.ascii_art_library.get("fraction_half", "")
        elif any(word in topic_lower for word in ["money", "savings", "economics"]):
            return self.ascii_art_library.get("money", "")
        elif any(word in topic_lower for word in ["plant", "growth", "biology"]):
            return self.ascii_art_library.get("plant_growth", "")
        
        return ""
    
    def _determine_presentation_order(self, primary_style: str) -> List[str]:
        """Determine the order to present different modalities"""
        orders = {
            "visual": ["visual", "kinesthetic", "reading", "auditory"],
            "auditory": ["auditory", "reading", "visual", "kinesthetic"],
            "kinesthetic": ["kinesthetic", "visual", "auditory", "reading"],
            "reading": ["reading", "visual", "auditory", "kinesthetic"]
        }
        
        return orders.get(primary_style, ["reading", "visual", "auditory", "kinesthetic"])

multimodal_service = MultimodalService()
