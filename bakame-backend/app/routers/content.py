from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
from datetime import datetime
import time

from app.models.database import get_db
from app.models.auth import ContentPage, WebUser
from app.routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class ContentUpdate(BaseModel):
    page_name: str
    content_data: Dict[str, Any]

class EarlyAccessRequest(BaseModel):
    email: str
    name: str
    company: str
    solution_interest: str

class ContactFormSubmission(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    subject: Optional[str] = None
    message: str
    solution_type: Optional[str] = None
    status: str = "new"

class IVRMessageRequest(BaseModel):
    message: str
    sessionId: str

@router.get("/content/{page_name}")
async def get_page_content(page_name: str, db: Session = Depends(get_db)):
    content = db.query(ContentPage).filter(ContentPage.page_name == page_name).first()
    if not content:
        return {
            "page_name": page_name,
            "content_data": {},
            "last_updated": None
        }
    
    return {
        "page_name": content.page_name,
        "content_data": json.loads(content.content_data),
        "last_updated": content.last_updated
    }

@router.put("/content/{page_name}")
async def update_page_content(
    page_name: str, 
    content_update: ContentUpdate,
    current_user: WebUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can edit content")
    
    content = db.query(ContentPage).filter(ContentPage.page_name == page_name).first()
    
    if content:
        content.content_data = json.dumps(content_update.content_data)
        content.last_updated = datetime.utcnow()
        content.updated_by = current_user.id
    else:
        content = ContentPage(
            page_name=page_name,
            content_data=json.dumps(content_update.content_data),
            updated_by=current_user.id
        )
        db.add(content)
    
    db.commit()
    db.refresh(content)
    
    return {
        "message": "Content updated successfully",
        "page_name": content.page_name,
        "last_updated": content.last_updated
    }

@router.get("/content")
async def list_all_content(
    current_user: WebUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    content_pages = db.query(ContentPage).all()
    return [
        {
            "page_name": page.page_name,
            "last_updated": page.last_updated,
            "updated_by": page.updated_by
        }
        for page in content_pages
    ]

@router.post("/early-access")
async def submit_early_access(request: EarlyAccessRequest, db: Session = Depends(get_db)):
    """Handle early access form submissions"""
    try:
        print(f"Early access request: {request.email} from {request.company}")
        
        
        return {
            "success": True,
            "message": "Early access request submitted successfully"
        }
    except Exception as e:
        print(f"Error processing early access request: {e}")
        raise HTTPException(status_code=500, detail="Failed to process request")

@router.post("/contact")
async def submit_contact_form(request: ContactFormSubmission, db: Session = Depends(get_db)):
    """Handle contact form submissions"""
    try:
        print(f"Contact form submission: {request.email} - {request.subject}")
        
        
        return {
            "success": True,
            "message": "Contact form submitted successfully"
        }
    except Exception as e:
        print(f"Error processing contact form: {e}")
        raise HTTPException(status_code=500, detail="Failed to process contact form")

@router.post("/sessions/create")
async def create_session(db: Session = Depends(get_db)):
    """Create a new IVR session for WebRTC"""
    try:
        import os
        
        ephemeral_token = os.environ.get('OPENAI_API_KEY', 'mock_ephemeral_token')
        
        return {
            "client_secret": {
                "value": ephemeral_token
            },
            "session_id": f"session_{int(time.time())}_{os.urandom(4).hex()}"
        }
    except Exception as e:
        print(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Session creation error: {str(e)}")

@router.post("/ivr/message")
async def handle_ivr_message(request: IVRMessageRequest, db: Session = Depends(get_db)):
    """Handle IVR chat messages"""
    try:
        from app.services.llama_service import LlamaService
        
        llama_service = LlamaService()
        
        messages = [{"role": "user", "content": request.message}]
        response = await llama_service.generate_response(messages, "english")
        
        return {
            "success": True,
            "response": response,
            "sessionId": request.sessionId
        }
    except Exception as e:
        print(f"Error processing IVR message: {e}")
        raise HTTPException(status_code=400, detail=f"AI tutor error: {str(e)}")
