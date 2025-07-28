import requests
import json
from typing import List, Dict, Any, Optional
from app.config import settings

class LlamaService:
    def __init__(self):
        self.api_key = settings.llama_api_key
        self.base_urls = [
            "https://api.llama.com/v1/chat/completions"
        ]
        self.working_url = None
        
    async def generate_response(self, messages: List[Dict[str, str]], module_name: str = "general") -> str:
        """Generate response using Llama API with Rwandan cultural context"""
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
            
            response = await self._call_llama_api(full_messages, module_name)
            return response.strip()
            
        except Exception as e:
            print(f"Error in Llama generation: {e}")
            return "Ndabwira ko nfite ikibazo gito. (I'm having a small issue.) Please try again, and I'll do my best to help you learn!"
    
    async def _call_llama_api(self, messages: List[Dict[str, str]], module_name: str = "general") -> str:
        """Call Llama API with multiple endpoint fallback, then OpenAI with Rwanda context"""
        
        if self.working_url:
            urls_to_try = [self.working_url] + [url for url in self.base_urls if url != self.working_url]
        else:
            urls_to_try = self.base_urls
        
        headers_variants = [
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            {"X-API-Key": self.api_key, "Content-Type": "application/json"},
            {"llama-api-key": self.api_key, "Content-Type": "application/json"}
        ]
        
        payload = {
            "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.8,
            "top_p": 0.9
        }
        
        for url in urls_to_try:
            for headers in headers_variants:
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'completion_message' in data and 'content' in data['completion_message']:
                            self.working_url = url
                            return data['completion_message']['content']['text']
                    
                except Exception as e:
                    print(f"Llama API error with {url}: {e}")
                    continue
        
        print("Llama API failed, falling back to OpenAI with Rwanda context")
        try:
            from app.services.openai_service import openai_service
            return await openai_service.generate_response(messages, module_name)
        except Exception as e:
            print(f"OpenAI fallback error: {e}")
            return "Ndabwira ko nfite ikibazo. (I have an issue.) Let me try to help you another way."
    
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav") -> str:
        """Keep using OpenAI Whisper for transcription"""
        from app.services.openai_service import openai_service
        return await openai_service.transcribe_audio(audio_data, audio_format)

llama_service = LlamaService()
