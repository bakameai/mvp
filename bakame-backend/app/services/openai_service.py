import openai
import asyncio
from typing import List, Dict, Any
import io
from app.config import settings

openai.api_key = settings.openai_api_key

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav", max_retries: int = 3) -> str:
        """Transcribe audio using OpenAI Whisper with auth retry and backoff"""
        for attempt in range(max_retries):
            try:
                audio_file = io.BytesIO(audio_data)
                audio_file.name = f"audio.{audio_format}"
                
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
                
                return transcript.strip()
            except Exception as e:
                error_msg = str(e).lower()
                if "401" in error_msg or "invalid_api_key" in error_msg or "authentication" in error_msg:
                    print(f"[OpenAI STT] Authentication failed (attempt {attempt + 1}/{max_retries})", flush=True)
                    if attempt < max_retries - 1:
                        backoff_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        print(f"[OpenAI STT] Retrying in {backoff_time}s...", flush=True)
                        await asyncio.sleep(backoff_time)
                        continue
                    else:
                        print("[OpenAI STT] All authentication attempts failed", flush=True)
                        return ""
                elif "rate_limit" in error_msg or "429" in error_msg:
                    print(f"[OpenAI STT] Rate limit hit (attempt {attempt + 1}/{max_retries})", flush=True)
                    if attempt < max_retries - 1:
                        backoff_time = 5 * (2 ** attempt)  # Longer backoff for rate limits
                        await asyncio.sleep(backoff_time)
                        continue
                else:
                    print(f"[OpenAI STT] Transcription error occurred (attempt {attempt + 1}/{max_retries}): {error_msg}", flush=True)
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                
        return ""
    
    async def generate_response(self, messages: List[Dict[str, str]], module_name: str = "general") -> str:
        """Generate response using GPT-4 with conversational intelligence"""
        try:
            system_prompts = {
                "english": "You're a friendly, encouraging English conversation partner who understands Rwandan culture deeply. Help with grammar, pronunciation, and vocabulary while being culturally sensitive. Use examples from Rwandan daily life, incorporate Kinyarwanda phrases when helpful (like 'Muraho' for hello, 'Murakoze' for thank you), and adapt your tone to the user's mood. Reference Rwanda's beautiful hills, community values of Ubuntu, and local contexts. Think step-by-step about their needs and respond conversationally.",
                
                "comprehension": "You're an engaging storyteller who loves Rwandan culture and traditions. Share tales that reflect Rwandan values like Ubuntu, unity, and community support. Reference Rwanda's history of resilience, beautiful landscapes from Kigali to Volcanoes National Park, and daily life. Ask thoughtful questions that spark curiosity about both stories and Rwandan heritage. Use Kinyarwanda phrases naturally and be encouraging. Think through their understanding and respond like a supportive Rwandan elder sharing wisdom.",
                
                "math": "You're an enthusiastic math mentor who makes numbers fun using Rwandan contexts. Use examples with Rwandan francs (RWF), local measurements, and familiar scenarios from Rwandan life - like calculating distances between Kigali and Butare, or market transactions. Reference Rwanda's progress in technology and education. Explain concepts conversationally, celebrate successes with phrases like 'Byiza cyane!' (very good), and provide gentle encouragement. Think through problems step-by-step using culturally relevant examples.",
                
                "debate": "You're a thoughtful discussion partner who understands Rwandan society and values deeply. Engage in respectful debates that consider Rwandan perspectives, history, and current challenges like development goals and regional integration. Be curious about their viewpoints while incorporating understanding of Rwandan culture, Ubuntu philosophy, and community values. Reference Rwanda's journey of unity and reconciliation. Keep discussions engaging and intellectually stimulating while being culturally sensitive.",
                
                "general": "You're BAKAME, a warm and intelligent AI learning companion who understands Rwandan culture deeply. Chat naturally while being helpful and educational. Reference Rwandan traditions, values like Ubuntu and unity, and daily life when appropriate. Use Kinyarwanda greetings and phrases naturally (Muraho, Murakoze, Byiza, etc.). Be curious, encouraging, and adapt your personality to match the user's energy. Think through their questions carefully and respond like a knowledgeable Rwandan friend who genuinely cares about their learning journey."
            }
            
            system_prompt = system_prompts.get(module_name, system_prompts["general"])
            
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages,
                max_tokens=300,
                temperature=0.8,
                top_p=0.9,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again."

openai_service = OpenAIService()
