from enum import Enum
from typing import Dict, Any
from app.config import settings

class ProviderType(Enum):
    ASR = "asr"
    TTS = "tts"
    LLM = "llm"

class ProviderConfig:
    def __init__(self):
        self.providers = {
            ProviderType.ASR: {
                "primary": "whisper",
                "fallback": "whisper_local",
                "current": "whisper"
            },
            ProviderType.TTS: {
                "primary": "elevenlabs",
                "fallback": "twilio_say",
                "current": "elevenlabs"
            },
            ProviderType.LLM: {
                "primary": "llama",
                "fallback": "openai",
                "current": "llama"
            }
        }
        
        self._load_from_env()
    
    def _load_from_env(self):
        """Load provider configuration from environment variables"""
        asr_provider = getattr(settings, 'asr_provider', None)
        if asr_provider:
            self.providers[ProviderType.ASR]["current"] = asr_provider
        
        tts_provider = getattr(settings, 'tts_provider', None)
        if tts_provider:
            self.providers[ProviderType.TTS]["current"] = tts_provider
    
    def get_current_provider(self, provider_type: ProviderType) -> str:
        """Get current provider for given type"""
        return self.providers[provider_type]["current"]
    
    def switch_to_fallback(self, provider_type: ProviderType):
        """Switch to fallback provider for given type"""
        fallback = self.providers[provider_type]["fallback"]
        self.providers[provider_type]["current"] = fallback
        print(f"Switched {provider_type.value} to fallback provider: {fallback}")
    
    def switch_to_primary(self, provider_type: ProviderType):
        """Switch back to primary provider for given type"""
        primary = self.providers[provider_type]["primary"]
        self.providers[provider_type]["current"] = primary
        print(f"Switched {provider_type.value} back to primary provider: {primary}")
    
    def is_degraded_mode(self) -> bool:
        """Check if any provider is in degraded mode"""
        for provider_type, config in self.providers.items():
            if config["current"] == config["fallback"]:
                return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current provider status"""
        return {
            "degraded_mode": self.is_degraded_mode(),
            "providers": {
                ptype.value: {
                    "current": config["current"],
                    "primary": config["primary"],
                    "fallback": config["fallback"]
                }
                for ptype, config in self.providers.items()
            }
        }

provider_config = ProviderConfig()
