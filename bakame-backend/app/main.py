from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import webhooks, admin, auth, content
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

@app.websocket("/twilio-stream")
async def twilio_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[Twilio] WebSocket connected successfully - endpoint is working!", flush=True)

    try:
        while True:
            data = await websocket.receive_text()
            print(f"[Twilio->Relay] {data}", flush=True)
    except WebSocketDisconnect:
        print("[Twilio] WebSocket disconnected", flush=True)

@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve temporary audio files for Twilio"""
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-cache"}
        )
    return {"error": "File not found"}

async def cleanup_old_audio_files():
    """Clean up audio files older than 1 hour"""
    while True:
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)
            audio_files = glob.glob("/tmp/*.mp3")
            
            for file_path in audio_files:
                if os.path.getctime(file_path) < cutoff_time.timestamp():
                    os.unlink(file_path)
                    
        except Exception as e:
            print(f"Error cleaning up audio files: {e}")
        
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
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
    return {"status": "ok", "service": "BAKAME MVP"}
