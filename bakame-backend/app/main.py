from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import webhooks, telnyx_webhooks
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bakame_telnyx.log')
    ]
)

app = FastAPI(
    title="BAKAME Learning Assistant API",
    description="Voice-based educational platform for feature phones - Telnyx Integration",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook routes
# Keep old Twilio routes for backward compatibility during migration
app.include_router(webhooks.router, prefix="/webhook", tags=["webhooks-legacy"])

# New Telnyx routes
app.include_router(telnyx_webhooks.router, prefix="/telnyx", tags=["telnyx"])

@app.get("/")
async def root():
    return {
        "message": "BAKAME Learning Assistant API - Telnyx Call Control",
        "voice_provider": "Telnyx",
        "api_version": "v2",
        "endpoints": {
            "telnyx_webhook": "/telnyx/incoming",
            "legacy_twilio": "/webhook/call (deprecated)"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "voice_provider": "telnyx", "call_control_api": "v2"}