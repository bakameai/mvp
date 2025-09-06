from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    openai_api_key: str
    elevenlabs_agent_id: str = "agent_0301k3y6dwrve63sb37n6f4ffkrj"
    use_elevenlabs: bool = False
    llama_api_key: str
    use_llama: bool = True
    newsapi_key: str
    deepgram_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    database_url: str
    app_env: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
