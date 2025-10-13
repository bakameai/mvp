from fastapi import APIRouter, Request, Form, Response
from typing import Optional
from app.services.twilio_service import twilio_service
from app.modules.general_module import general_module

router = APIRouter()

@router.post("/call")
async def handle_voice_call(From: str = Form(...)):
    """Handle incoming voice calls - always fresh, no history"""
    
    print(f"[Webhook] New call from {From}")
    
    # Always call OpenAI for welcome message - fresh greeting each time
    welcome_message = await general_module.process("Hello", {})
    
    # Create voice response
    response = await twilio_service.create_voice_response(
        message=welcome_message,
        gather_input=True,
        timeout=60
    )
    
    return Response(content=response, media_type="application/xml")

@router.post("/voice/process")
async def process_voice_input(
    From: str = Form(...),
    SpeechResult: Optional[str] = Form(None)
):
    """Process voice input - always fresh, no history"""
    
    user_input = SpeechResult if SpeechResult else "..."
    print(f"[Webhook] Voice input from {From}: {user_input}")
    
    try:
        # Always fresh call to OpenAI - no context
        ai_response = await general_module.process(user_input, {})
        
        # Create voice response
        response = await twilio_service.create_voice_response(
            message=ai_response,
            gather_input=True,
            timeout=60
        )
        
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        print(f"[Webhook] Error: {e}")
        # Even errors go through OpenAI
        error_response = await general_module.process("System error occurred", {})
        response = await twilio_service.create_voice_response(
            message=error_response,
            gather_input=True,
            timeout=60
        )
        return Response(content=response, media_type="application/xml")

@router.post("/sms")
async def handle_sms(
    From: str = Form(...),
    Body: str = Form(...)
):
    """Handle incoming SMS - always fresh, no history"""
    
    print(f"[Webhook] SMS from {From}: {Body}")
    
    try:
        # Always fresh call to OpenAI - no context
        ai_response = await general_module.process(Body, {})
        
        return Response(
            content=twilio_service.create_sms_response(ai_response),
            media_type="application/xml"
        )
        
    except Exception as e:
        print(f"[Webhook] SMS Error: {e}")
        error_response = await general_module.process("Error processing message", {})
        return Response(
            content=twilio_service.create_sms_response(error_response),
            media_type="application/xml"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BAKAME"}