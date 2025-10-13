from fastapi import APIRouter, Request, Form, Response
from typing import Optional
from app.services.twilio_service import twilio_service
from app.services.redis_service import redis_service
from app.modules.general_module import general_module

router = APIRouter()

@router.post("/call")
async def handle_voice_call(From: str = Form(...)):
    """Handle incoming voice calls - pure English conversation teaching"""
    
    phone_number = From
    
    # Get or create user context
    user_context = redis_service.get_user_context(phone_number)
    if not user_context:
        user_context = {"phone_number": phone_number, "conversation_history": []}
    else:
        user_context["phone_number"] = phone_number
    
    # Generate conversational welcome
    welcome_message = await general_module.process("Hello", user_context)
    
    # Save context
    redis_service.set_user_context(phone_number, user_context)
    
    # Create voice response with 60 second timeout
    response = await twilio_service.create_voice_response(
        message=welcome_message,
        gather_input=True,
        timeout=60  # Wait 60 seconds for user to speak
    )
    
    return Response(content=response, media_type="application/xml")

@router.post("/voice/process")
async def process_voice_input(
    From: str = Form(...),
    SpeechResult: Optional[str] = Form(None)
):
    """Process voice input - pure English conversation teaching"""
    
    phone_number = From
    user_input = SpeechResult if SpeechResult else "[User was silent]"
    
    try:
        # Get user context
        user_context = redis_service.get_user_context(phone_number)
        if not user_context:
            user_context = {"phone_number": phone_number, "conversation_history": []}
        else:
            user_context["phone_number"] = phone_number
        
        # Process through English conversation
        ai_response = await general_module.process(user_input, user_context)
        
        # Save context
        redis_service.set_user_context(phone_number, user_context)
        
        # Create voice response with 60 second timeout
        response = await twilio_service.create_voice_response(
            message=ai_response,
            gather_input=True,
            timeout=60  # Wait 60 seconds for user to speak
        )
        
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        print(f"Error processing voice input: {e}")
        error_response = await twilio_service.create_voice_response(
            message="I didn't quite catch that. Could you please repeat?",
            gather_input=True,
            timeout=60
        )
        return Response(content=error_response, media_type="application/xml")

@router.post("/sms")
async def handle_sms(
    From: str = Form(...),
    Body: str = Form(...)
):
    """Handle incoming SMS - pure English conversation teaching"""
    
    phone_number = From
    user_input = Body.strip()
    
    try:
        # Get user context
        user_context = redis_service.get_user_context(phone_number)
        if not user_context:
            user_context = {"phone_number": phone_number, "conversation_history": []}
        else:
            user_context["phone_number"] = phone_number
        
        # Process through English conversation
        ai_response = await general_module.process(user_input, user_context)
        
        # Save context
        redis_service.set_user_context(phone_number, user_context)
        
        # Send SMS response
        return Response(
            content=twilio_service.create_sms_response(ai_response),
            media_type="application/xml"
        )
        
    except Exception as e:
        print(f"Error in SMS handler: {e}")
        return Response(
            content=twilio_service.create_sms_response(
                "Sorry, I couldn't process your message. Please try again."
            ),
            media_type="application/xml"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BAKAME English Teaching"}