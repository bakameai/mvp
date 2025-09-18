from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    openai_api_key: str
    elevenlabs_agent_id: str = "agent_0301k3y6dwrve63sb37n6f4ffkrj"
    use_elevenlabs: bool = False
    use_deepgram_tts: bool = True
    use_google_tts: bool = False
    use_openai_realtime: bool = False
    google_cloud_project: str = "bakame-ai"
    newsapi_key: str
    deepgram_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    database_url: str
    app_env: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
