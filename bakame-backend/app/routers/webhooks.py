from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response
import uuid
from typing import Optional
from app.services.twilio_service import twilio_service
from app.services.openai_service import openai_service
from app.services.redis_service import redis_service
from app.services.logging_service import logging_service
from app.services.offline_service import offline_service
from app.services.multimodal_service import multimodal_service
from app.modules.english_module import english_module
from app.modules.math_module import math_module
from app.modules.comprehension_module import comprehension_module
from app.modules.debate_module import debate_module
from app.modules.general_module import general_module

router = APIRouter()

MODULES = {
    "english": english_module,
    "math": math_module,
    "comprehension": comprehension_module,
    "debate": debate_module,
    "general": general_module
}

@router.post("/call")
async def handle_voice_call(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    CallSid: str = Form(...),
    SpeechResult: Optional[str] = Form(None),
    RecordingUrl: Optional[str] = Form(None)
):
    """Handle incoming voice calls from Twilio"""
    
    phone_number = From
    session_id = CallSid
    
    try:
        user_context = redis_service.get_user_context(phone_number)
        user_context["phone_number"] = phone_number
        
        if not SpeechResult and not RecordingUrl:
            welcome_msg = await general_module.get_welcome_message(user_context)
            redis_service.set_current_module(phone_number, "general")
            
            await logging_service.log_interaction(
                phone_number=phone_number,
                session_id=session_id,
                module_name="general",
                interaction_type="voice",
                user_input="[CALL_START]",
                ai_response=welcome_msg
            )
            
            return Response(
                content=await twilio_service.create_voice_response(welcome_msg),
                media_type="application/xml"
            )
        
        user_input = ""
        if SpeechResult:
            user_input = SpeechResult
        elif RecordingUrl:
            audio_data = await twilio_service.download_recording(RecordingUrl)
            if audio_data:
                user_input = await openai_service.transcribe_audio(audio_data)
        
        if not user_input:
            return Response(
                content=await twilio_service.create_voice_response("I didn't catch that. Could you please repeat?"),
                media_type="application/xml"
            )
        
        if user_input and (user_input.lower().strip() == "reset" or any(word in user_input.lower() for word in ["hello", "hi", "hey", "start", "new", "help", "menu", "general"])):
            redis_service.clear_user_context(phone_number)
            user_context = redis_service.get_user_context(phone_number)
            current_module_name = "general"
            redis_service.set_current_module(phone_number, current_module_name)
        else:
            user_context = redis_service.get_user_context(phone_number)
        
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
        
        await logging_service.log_interaction(
            phone_number=phone_number,
            session_id=session_id,
            module_name=current_module_name,
            interaction_type="voice",
            user_input=user_input,
            ai_response=ai_response
        )
        
        if any(word in user_input.lower() for word in ["goodbye", "bye", "end call", "hang up", "stop"]):
            return Response(
                content=await twilio_service.create_voice_response("Thank you for using BAKAME! Keep learning and have a great day!", gather_input=False),
                media_type="application/xml"
            )
        
        return Response(
            content=await twilio_service.create_voice_response(ai_response),
            media_type="application/xml"
        )
        
    except Exception as e:
        print(f"Error in voice call handler: {e}")
        await logging_service.log_error(f"Voice call error for {phone_number}: {str(e)}")
        
        try:
            fallback_response = "Welcome to BAKAME! I'm your AI learning assistant. Say MATH for math practice, ENGLISH for language learning, or HELP for more options."
            return Response(
                content=await twilio_service.create_voice_response(fallback_response),
                media_type="application/xml"
            )
        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            return Response(
                content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Welcome to BAKAME learning assistant. Please try again.</Say></Response>',
                media_type="application/xml"
            )

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
        if user_input.lower().strip() == "reset" or any(word in user_input.lower() for word in ["hello", "hi", "hey", "start", "new", "help", "menu", "general"]):
            redis_service.clear_user_context(phone_number)
            user_context = redis_service.get_user_context(phone_number)
            current_module_name = "general"
            redis_service.set_current_module(phone_number, current_module_name)
        else:
            user_context = redis_service.get_user_context(phone_number)
        
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
        
        await logging_service.log_interaction(
            phone_number=phone_number,
            session_id=session_id,
            module_name=current_module_name,
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
async def handle_voice_process(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    CallSid: str = Form(...),
    SpeechResult: Optional[str] = Form(None),
    RecordingUrl: Optional[str] = Form(None)
):
    """Handle continued voice interactions from Twilio"""
    return await handle_voice_call(request, From, To, CallSid, SpeechResult, RecordingUrl)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BAKAME MVP"}
