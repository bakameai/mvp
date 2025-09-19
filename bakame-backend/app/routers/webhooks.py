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

MODULES = {
    "english": english_module,
    "math": math_module,
    "comprehension": comprehension_module,
    "debate": debate_module,
    "general": general_module
}

@router.post("/call")
async def handle_voice_call(From: str = Form(...), To: str = Form(...)):
    """Handle incoming voice calls from Twilio using TwiML gather/say"""
    phone_number = From
    
    user_context = redis_service.get_user_context(phone_number)
    user_name = user_context.get("user_name")
    learning_preferences = user_context.get("learning_preferences")
    
    if user_name and learning_preferences:
        welcome_message = f"Muraho {user_name}! Welcome back to BAKAME. I remember you're interested in {learning_preferences}. What would you like to work on today?"
    elif user_name:
        welcome_message = f"Muraho {user_name}! Welcome back to BAKAME. What would you like to learn about today?"
    else:
        welcome_message = "Muraho! Welcome to BAKAME, your AI learning companion. Please tell me your name first."
    
    twiml_response = await twilio_service.create_voice_response(
        message=welcome_message,
        gather_input=True
    )
    
    return Response(content=twiml_response, media_type="application/xml")

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
    """Handle voice processing using Twilio's speech recognition"""
    phone_number = From
    session_id = CallSid
    user_input = SpeechResult
    
    try:
        if not user_input or len(user_input.strip()) < 2:
            retry_message = "I didn't hear anything. Please tell me what you'd like to learn about."
            twiml_response = await twilio_service.create_voice_response(
                message=retry_message,
                gather_input=True
            )
            return Response(content=twiml_response, media_type="application/xml")
        
        print(f"[BAKAME] Voice input from {phone_number}: {user_input}", flush=True)
        
        if user_input and any(word in user_input.lower() for word in ["goodbye", "bye", "end", "stop", "quit", "exit"]):
            goodbye_message = "Murakoze for using BAKAME! Keep learning and growing. Goodbye!"
            twiml_response = await twilio_service.create_voice_response(
                message=goodbye_message,
                gather_input=False,
                end_call=True
            )
            return Response(content=twiml_response, media_type="application/xml")
        
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
            interaction_type="voice",
            user_input=user_input,
            ai_response=ai_response
        )
        
        print(f"[BAKAME] AI Response: {ai_response}", flush=True)
        
        twiml_response = await twilio_service.create_voice_response(
            message=ai_response,
            gather_input=True
        )
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"Error in voice processing: {e}")
        await logging_service.log_error(f"Voice processing error for {phone_number}: {str(e)}")
        
        fallback_message = "I'm sorry, I'm having trouble processing your request. Please try again or say 'help' for assistance."
        twiml_response = await twilio_service.create_voice_response(
            message=fallback_message,
            gather_input=True
        )
        
        return Response(content=twiml_response, media_type="application/xml")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BAKAME MVP"}
