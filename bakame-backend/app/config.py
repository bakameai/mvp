from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    openai_api_key: str
    llama_api_key: str
    use_llama: bool = True
    newsapi_key: str
    deepgram_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    database_url: str
    app_env: str = "development"
    debug: bool = True
    
    tts_provider: str = "deepgram"
    tts_voice: str = "aura-asteria-en"
    tts_rate: float = 0.95
    tts_pitch: str = "+1st"
    tts_style: str = "conversational"
    
    class Config:
        env_file = ".env"

settings = Settings()
