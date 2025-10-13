import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Telnyx Configuration (replacing Twilio)
    telnyx_api_key: str = os.getenv("TELNYX_API_KEY", "")
    telnyx_phone_number: str = os.getenv("TELNYX_PHONE_NUMBER", "")
    telnyx_public_key: Optional[str] = os.getenv("TELNYX_PUBLIC_KEY", "")  # For webhook verification
    telnyx_api_url: str = "https://api.telnyx.com/v2"
    # Only use OPENAIAPI environment variable
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
        extra = "ignore"  # Ignore extra fields from .env file

settings = Settings()