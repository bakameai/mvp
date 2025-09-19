from fastapi import FastAPI, Form, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI()

@app.post("/webhook/call")
async def twilio_webhook(From: str = Form(...), To: str = Form(...)):
    """Redirect to router handler"""
    from app.routers.webhooks import handle_voice_call
    return await handle_voice_call(From, To)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import webhooks, admin, auth, content
app.include_router(webhooks.router, prefix="/webhook", tags=["webhooks"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(content.router, prefix="/content", tags=["content"])
