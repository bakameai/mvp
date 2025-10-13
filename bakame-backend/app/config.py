import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    # Use OPENAIAPI instead of OPENAI_API_KEY
    openai_api_key: str = os.getenv("OPENAIAPI", "")
    llama_api_key: str = os.getenv("LLAMA_API_KEY", "")
    use_llama: bool = False  # Use OpenAI by default
    newsapi_key: str = os.getenv("NEWSAPI_KEY", "")
    deepgram_api_key: str = os.getenv("DEEPGRAM_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    database_url: str = os.getenv("DATABASE_URL", "")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()