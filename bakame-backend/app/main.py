from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import webhooks, admin, auth, content, newsletter, analytics, admin_extended, media_stream
from app.routers.auth import create_admin_user_if_not_exists
from app.models.database import create_tables
from app.config import settings
import os
import asyncio
import glob
from datetime import datetime, timedelta

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
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(content.router, prefix="/api", tags=["content"])
app.include_router(newsletter.router, tags=["newsletter"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(admin_extended.router, tags=["admin_extended"])
app.include_router(media_stream.router, prefix="/webhook", tags=["media_stream"])

@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve temporary audio files for Twilio"""
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        if filename.endswith('.wav'):
            media_type = "audio/wav"
        elif filename.endswith('.mp3'):
            media_type = "audio/mpeg"
        else:
            media_type = "audio/wav"
            
        return FileResponse(
            file_path,
            media_type=media_type,
            headers={"Cache-Control": "no-cache"}
        )
    return {"error": "File not found"}

async def cleanup_old_audio_files():
    """Clean up audio files older than 1 hour"""
    while True:
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
            audio_patterns = ["/tmp/*.mp3", "/tmp/*.wav", "/tmp/*_telephony.wav"]
            
            for pattern in audio_patterns:
                audio_files = glob.glob(pattern)
                for file_path in audio_files:
                    if os.path.getctime(file_path) < cutoff_time.timestamp():
                        os.unlink(file_path)
                        
        except Exception as e:
            print(f"Error cleaning up audio files: {e}")
        
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables and validate environment on startup"""
    required_vars = [
        "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER",
        "OPENAI_API_KEY", "LLAMA_API_KEY", "DEEPGRAM_API_KEY",
        "REDIS_URL", "DATABASE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
    
    if missing_vars:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    create_tables()
    from app.models.database import SessionLocal
    db = SessionLocal()
    try:
        create_admin_user_if_not_exists(db)
    finally:
        db.close()
    asyncio.create_task(cleanup_old_audio_files())

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
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "BAKAME MVP",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    overall_healthy = True
    
    try:
        from app.services.redis_service import redis_service
        redis_service.redis_client.ping()
        health_status["checks"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False
    
    try:
        from app.models.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False
    
    try:
        from app.services.llama_service import llama_service
        test_response = await llama_service.generate_response([{"role": "user", "content": "ping"}], "general")
        if test_response:
            health_status["checks"]["llama_api"] = {"status": "healthy"}
        else:
            health_status["checks"]["llama_api"] = {"status": "degraded", "note": "Empty response"}
    except Exception as e:
        health_status["checks"]["llama_api"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False
    
    try:
        from app.services.openai_service import openai_service
        test_response = await openai_service.generate_response([{"role": "user", "content": "ping"}], "general")
        if test_response:
            health_status["checks"]["openai_api"] = {"status": "healthy"}
        else:
            health_status["checks"]["openai_api"] = {"status": "degraded", "note": "Empty response"}
    except Exception as e:
        health_status["checks"]["openai_api"] = {"status": "unhealthy", "error": str(e)}
    
    try:
        from app.services.deepgram_service import deepgram_service
        health_status["checks"]["deepgram_api"] = {"status": "healthy", "note": "Service available"}
    except Exception as e:
        health_status["checks"]["deepgram_api"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False
    
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"
    
    return health_status
