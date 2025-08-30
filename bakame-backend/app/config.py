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
    elevenlabs_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    database_url: str
    app_env: str = "development"
    debug: bool = True
    mcp_server_url: str = "http://localhost:8001"
    
    class Config:
        env_file = ".env"

settings = Settings()
