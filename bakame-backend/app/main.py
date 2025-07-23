from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import webhooks, admin
from app.models.database import create_tables
from app.config import settings

app = FastAPI(
    title="BAKAME MVP - AI Learning Assistant",
    description="Voice and SMS AI-powered learning assistant for feature phones",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(webhooks.router, prefix="/webhook", tags=["webhooks"])
app.include_router(admin.router, tags=["admin"])

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()

@app.get("/")
async def root():
    return {
        "message": "BAKAME MVP - AI Learning Assistant",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "voice_webhook": "/webhook/call",
            "sms_webhook": "/webhook/sms",
            "admin_stats": "/admin/stats",
            "health_check": "/webhook/health"
        }
    }

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "BAKAME MVP"}
