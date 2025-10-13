from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import webhooks

app = FastAPI(
    title="BAKAME Learning Assistant API",
    description="Voice-based educational platform for feature phones",
    version="1.0.0"
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
app.include_router(webhooks.router, prefix="/webhook", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "BAKAME Learning Assistant API - Using Twilio Say for voice"}

@app.get("/health")
async def health():
    return {"status": "healthy", "voice": "twilio-say"}