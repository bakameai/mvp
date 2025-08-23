from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime

from app.models.database import get_db
from app.models.auth import ContentPage, WebUser
from app.routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class ContentUpdate(BaseModel):
    page_name: str
    content_data: Dict[str, Any]

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
