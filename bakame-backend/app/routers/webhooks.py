from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response
import uuid
from typing import Optional

from app.services.twilio_service import twilio_service
from app.services.openai_service import openai_service
from app.services.elevenlabs_service import elevenlabs_service
from app.services.redis_service import redis_service
from app.services.logging_service import logging_service
from app.services.offline_service import offline_service
from app.services.multimodal_service import multimodal_service
from app.config import settings
from app.modules.english_module import english_module
from app.modules.math_module import math_module
from app.modules.comprehension_module import comprehension_module
from app.modules.debate_module import debate_module
from app.modules.general_module import general_module

router = APIRouter()

@router.post("/call")
def handle_voice_call():
    """Handle incoming voice calls from Twilio - Connect to ElevenLabs WebSocket stream"""
    
    WS_URL = "wss://bakame-elevenlabs-mcp.fly.dev/twilio-stream"
    
<<<<<<< HEAD
    try:
        redis_service.clear_user_context(phone_number)
        user_context = redis_service.get_user_context(phone_number)
        
        if not SpeechResult and not RecordingUrl:
            welcome_msg = "Hello! I'm BAKAME, your AI learning assistant. What would you like to learn about today?"
            
            await logging_service.log_interaction(
                phone_number=phone_number,
                session_id=session_id,
                module_name="general",
                interaction_type="voice",
                user_input="[CALL_START]",
                ai_response=welcome_msg
            )
            
            return Response(
                content=twilio_service.create_voice_response(welcome_msg),
                media_type="application/xml"
            )
        
        user_input = ""
        if SpeechResult:
            user_input = SpeechResult
        
        if not user_input:
            return Response(
                content=twilio_service.create_voice_response("I didn't catch that. Could you please repeat?", gather_input=True),
                media_type="application/xml"
            )
        
        messages = [{"role": "user", "content": user_input}]
        ai_response = await openai_service.generate_response(messages, "general")
        
        await logging_service.log_interaction(
            phone_number=phone_number,
            session_id=session_id,
            module_name="general",
            interaction_type="voice",
            user_input=user_input,
            ai_response=ai_response
        )
        
        if any(word in user_input.lower() for word in ["goodbye", "bye", "end call", "hang up", "stop"]):
            return Response(
                content=twilio_service.create_voice_response("Thank you for using BAKAME! Keep learning and have a great day!", gather_input=False),
                media_type="application/xml"
            )
        
        return Response(
            content=twilio_service.create_voice_response(ai_response),
            media_type="application/xml"
        )
        
    except Exception as e:
        print(f"Error in voice call handler: {e}")
        return Response(
            content=twilio_service.create_voice_response("I'm sorry, I'm having technical difficulties. Please try again later.", gather_input=True),
            media_type="application/xml"
        )
=======
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="{WS_URL}"/>
  </Connect>
</Response>"""
    
    return Response(content=twiml, media_type="application/xml")
>>>>>>> bakame-mvp-implementation

@router.post("/sms")
async def handle_sms(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...)
):
    """Handle incoming SMS messages from Twilio"""
    
    phone_number = From
    session_id = MessageSid
    user_input = Body.strip()
    
    try:
        redis_service.clear_user_context(phone_number)
        user_context = redis_service.get_user_context(phone_number)
        
<<<<<<< HEAD
        messages = [{"role": "user", "content": user_input}]
        ai_response = await openai_service.generate_response(messages, "general")
=======
        user_context["phone_number"] = phone_number
        
        current_module_name = redis_service.get_current_module(phone_number) or "general"
        
        requested_module = user_context.get("user_state", {}).get("requested_module")
        if requested_module and requested_module in MODULES:
            current_module_name = requested_module
            redis_service.set_current_module(phone_number, current_module_name)
            user_context["user_state"]["requested_module"] = None
            redis_service.set_user_context(phone_number, user_context)
        
        current_module = MODULES.get(current_module_name, general_module)
        
        ai_response = await current_module.process_input(user_input, user_context)
        
        redis_service.add_to_conversation_history(phone_number, user_input, ai_response)
>>>>>>> bakame-mvp-implementation
        
        await logging_service.log_interaction(
            phone_number=phone_number,
            session_id=session_id,
            module_name="general",
            interaction_type="sms",
            user_input=user_input,
            ai_response=ai_response
        )
        
        await offline_service.cache_interaction(phone_number, user_input, ai_response, current_module_name)
        
        return Response(
            content=twilio_service.create_sms_response(ai_response),
            media_type="application/xml"
        )
        
    except Exception as e:
        print(f"Error in SMS handler: {e}")
        await logging_service.log_error(f"SMS error for {phone_number}: {str(e)}")
        
        try:
            fallback_response = "Welcome to BAKAME! I'm your AI learning assistant. Reply MATH for math practice, ENGLISH for language learning, or HELP for more options."
            return Response(
                content=twilio_service.create_sms_response(fallback_response),
                media_type="application/xml"
            )
        except Exception as fallback_error:
            print(f"SMS fallback error: {fallback_error}")
            return Response(
                content='<?xml version="1.0" encoding="UTF-8"?><Response><Message>Welcome to BAKAME learning assistant. Please try again.</Message></Response>',
                media_type="application/xml"
            )

@router.post("/voice/process")
def handle_voice_process():
    """Handle continued voice interactions from Twilio"""
    return handle_voice_call()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BAKAME MVP"}
