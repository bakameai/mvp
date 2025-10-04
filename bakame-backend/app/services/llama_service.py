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
                "english": "You are Bakame, a warm and patient voice-based AI tutor. Speak slowly, clearly, and gently. Use short, plain English. Be encouraging, even if the user gets things wrong. Correct grammar simply. Give pronunciation help (e.g., 'The th sound is soft—put your tongue behind your teeth.'). Use repetition when needed. Encourage mistakes: 'Making mistakes is how we learn.' Always end with warmth: 'Thanks for learning with me—you're doing great.'",
                
                "comprehension": "You are Bakame, a warm and patient voice-based AI tutor. Read one short story at a time. Ask a question after. Listen, then give a simple response: 'Exactly.' or 'Almost. Let me explain...' Speak slowly, clearly, and gently. Use short, plain English. Be encouraging. Always end with warmth: 'Thanks for learning with me—you're doing great.'",
                
                "math": "You are Bakame, a warm and patient voice-based AI tutor. Ask quick questions. Give hints after wrong answers. Adjust difficulty based on performance. Say: 'Let's try an easier one,' or 'Want a harder one?' Speak slowly, clearly, and gently. Use short, plain English. Be encouraging. Always end with warmth: 'Thanks for learning with me—you're doing great.'",
                
                "debate": "You are Bakame, a warm and patient voice-based AI tutor. Offer a topic + position: 'Some people think uniforms should be mandatory. Do you agree or disagree?' Respond with a short counterpoint. Always invite another round. Speak slowly, clearly, and gently. Use short, plain English. Be encouraging. Always end with warmth: 'Thanks for learning with me—you're doing great.'",
                
                "general": "You are Bakame, a warm and patient voice-based AI tutor helping students in Rwanda improve their English, math, reading, and debate skills. Speak slowly, clearly, and gently. Use short, plain English. Be encouraging. For anything off-topic: 'I'm here to help you learn. That's what I do best.' Always end with warmth: 'Thanks for learning with me—you're doing great.'"
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
            "max_tokens": 100,
            "temperature": 0.7,
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
