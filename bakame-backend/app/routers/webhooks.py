from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response
import uuid
from typing import Optional
from app.services.twilio_service import twilio_service
from app.services.openai_service import openai_service
from app.services.redis_service import redis_service
from app.services.logging_service import logging_service
from app.services.sentiment_service import sentiment_service
from app.services.name_extraction_service import name_extraction_service
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
            intro_msg = await name_extraction_service.generate_intro_message()
            redis_service.set_current_module(phone_number, "general")
            redis_service.set_session_data(phone_number, "conversation_state", "intro", ttl=600)
            
            await logging_service.log_interaction(
                phone_number=phone_number,
                session_id=session_id,
                module_name="general",
                interaction_type="voice",
                user_input="[CALL_START]",
                ai_response=intro_msg
            )
            
            return Response(
                content=await twilio_service.create_voice_response(intro_msg, call_sid=session_id, rate=0.95),
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
            conversation_state = redis_service.get_session_data(phone_number, "conversation_state") or "normal"
            
            if conversation_state == "intro" or conversation_state == "name_capture":
                silence_count = redis_service.get_session_data(phone_number, "name_silence_count") or 0
                silence_count = int(silence_count) + 1
                redis_service.set_session_data(phone_number, "name_silence_count", str(silence_count), ttl=300)
                
                if silence_count == 1:
                    response_msg = "Take your time — please tell me your name so I can personalize our practice."
                else:
                    response_msg = "No problem — I'll call you friend for now. We can change that anytime."
                    redis_service.set_session_data(phone_number, "user_name", "Friend", ttl=3600)
                    redis_service.set_session_data(phone_number, "conversation_state", "normal", ttl=600)
                    redis_service.delete_session_data(phone_number, "name_silence_count")
                
                return Response(
                    content=await twilio_service.create_voice_response(response_msg, call_sid=session_id, rate=0.95),
                    media_type="application/xml"
                )
            else:
                silence_count = redis_service.get_session_data(phone_number, "silence_count") or 0
                silence_count = int(silence_count) + 1
                redis_service.set_session_data(phone_number, "silence_count", str(silence_count), ttl=300)
                
                if silence_count == 1:
                    response_msg = "I didn't catch that. Could you please repeat what you'd like to learn about?"
                elif silence_count == 2:
                    response_msg = "Let me make this easier. Just say ENGLISH, MATH, or HELP to get started."
                else:
                    response_msg = "I'll send you a text message with some tips. Thank you for calling BAKAME!"
                    
                    sms_tip = "BAKAME Tip: Call back and say 'ENGLISH' for language practice, 'MATH' for numbers, or 'HELP' for options. Muraho!"
                    twilio_service.send_sms(phone_number, sms_tip)
                    
                    redis_service.delete_session_data(phone_number, "silence_count")
                    
                    return Response(
                        content=await twilio_service.create_voice_response(response_msg, gather_input=False),
                        media_type="application/xml"
                    )
                
                return Response(
                    content=await twilio_service.create_voice_response(response_msg),
                    media_type="application/xml"
                )
        
        redis_service.delete_session_data(phone_number, "silence_count")
        redis_service.delete_session_data(phone_number, "name_silence_count")
        
        conversation_state = redis_service.get_session_data(phone_number, "conversation_state") or "normal"
        
        if conversation_state == "intro":
            name, confidence = name_extraction_service.extract_name(user_input)
            
            if name and confidence >= 0.7:
                confirmation_msg = name_extraction_service.generate_confirmation_message(name)
                redis_service.set_session_data(phone_number, "pending_name", name, ttl=600)
                redis_service.set_session_data(phone_number, "conversation_state", "name_confirm", ttl=600)
                
                return Response(
                    content=await twilio_service.create_voice_response(confirmation_msg, call_sid=session_id, rate=0.95),
                    media_type="application/xml"
                )
            else:
                redis_service.set_session_data(phone_number, "conversation_state", "name_capture", ttl=600)
                response_msg = "I didn't catch your name clearly. Could you please say it again?"
                
                return Response(
                    content=await twilio_service.create_voice_response(response_msg, call_sid=session_id, rate=0.95),
                    media_type="application/xml"
                )
        
        elif conversation_state == "name_confirm":
            if name_extraction_service.is_confirmation(user_input):
                pending_name = redis_service.get_session_data(phone_number, "pending_name")
                redis_service.set_session_data(phone_number, "user_name", pending_name, ttl=3600)
                redis_service.set_session_data(phone_number, "conversation_state", "normal", ttl=600)
                redis_service.delete_session_data(phone_number, "pending_name")
                
                welcome_msg = f"Great to meet you, {pending_name}! I'm excited to learn with you today. What would you like to practice? Say ENGLISH, MATH, STORIES, or DEBATE."
                
                await logging_service.log_interaction(
                    phone_number=phone_number,
                    session_id=session_id,
                    module_name="general",
                    interaction_type="voice",
                    user_input=f"[NAME_CONFIRMED: {pending_name}]",
                    ai_response=welcome_msg
                )
                
                return Response(
                    content=await twilio_service.create_voice_response(welcome_msg, call_sid=session_id),
                    media_type="application/xml"
                )
            else:
                name, confidence = name_extraction_service.extract_name(user_input)
                
                if name and confidence >= 0.6:
                    confirmation_msg = name_extraction_service.generate_confirmation_message(name)
                    redis_service.set_session_data(phone_number, "pending_name", name, ttl=600)
                    
                    return Response(
                        content=await twilio_service.create_voice_response(confirmation_msg, call_sid=session_id, rate=0.95),
                        media_type="application/xml"
                    )
                else:
                    spell_msg = name_extraction_service.generate_spell_request()
                    redis_service.set_session_data(phone_number, "conversation_state", "name_spell", ttl=600)
                    
                    return Response(
                        content=await twilio_service.create_voice_response(spell_msg, call_sid=session_id, rate=0.85),
                        media_type="application/xml"
                    )
        
        elif conversation_state == "name_capture":
            name, confidence = name_extraction_service.extract_name(user_input)
            
            if name and confidence >= 0.6:
                confirmation_msg = name_extraction_service.generate_confirmation_message(name)
                redis_service.set_session_data(phone_number, "pending_name", name, ttl=600)
                redis_service.set_session_data(phone_number, "conversation_state", "name_confirm", ttl=600)
                
                return Response(
                    content=await twilio_service.create_voice_response(confirmation_msg, call_sid=session_id, rate=0.95),
                    media_type="application/xml"
                )
            else:
                spell_msg = name_extraction_service.generate_spell_request()
                redis_service.set_session_data(phone_number, "conversation_state", "name_spell", ttl=600)
                
                return Response(
                    content=await twilio_service.create_voice_response(spell_msg, call_sid=session_id, rate=0.85),
                    media_type="application/xml"
                )
        
        elif conversation_state == "name_spell":
            spelled_name = name_extraction_service.extract_spelling(user_input)
            
            if spelled_name and len(spelled_name) >= 2:
                confirmation_msg = name_extraction_service.generate_confirmation_message(spelled_name)
                redis_service.set_session_data(phone_number, "pending_name", spelled_name, ttl=600)
                redis_service.set_session_data(phone_number, "conversation_state", "name_confirm", ttl=600)
                
                return Response(
                    content=await twilio_service.create_voice_response(confirmation_msg, call_sid=session_id, rate=0.95),
                    media_type="application/xml"
                )
            else:
                redis_service.set_session_data(phone_number, "user_name", "Friend", ttl=3600)
                redis_service.set_session_data(phone_number, "conversation_state", "normal", ttl=600)
                
                fallback_msg = "That's okay! I'll call you Friend for now. Let's start learning! What would you like to practice?"
                
                return Response(
                    content=await twilio_service.create_voice_response(fallback_msg, call_sid=session_id),
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
        
        user_name = redis_service.get_session_data(phone_number, "user_name")
        if user_name:
            user_context["user_name"] = user_name
        
        current_module_name = redis_service.get_current_module(phone_number) or "general"
        
        requested_module = user_context.get("user_state", {}).get("requested_module")
        if requested_module and requested_module in MODULES:
            current_module_name = requested_module
            redis_service.set_current_module(phone_number, current_module_name)
            user_context["user_state"]["requested_module"] = None
            redis_service.set_user_context(phone_number, user_context)
        
        current_module = MODULES.get(current_module_name, general_module)
        
        sentiment_result = sentiment_service.analyze_sentiment(user_input)
        user_context["current_sentiment"] = sentiment_result.sentiment
        
        tts_kwargs = {}
        if sentiment_result.sentiment == "frustrated":
            tts_kwargs["rate"] = 0.85
            
        ai_response = await current_module.process_input(user_input, user_context)
        
        if sentiment_result.sentiment == "frustrated":
            encouragement = sentiment_service.get_encouraging_response("frustrated")
            ai_response = f"{encouragement} {ai_response}"
        
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
            from app.services.rwanda_facts_service import rwanda_facts_service
            from app.services.llama_service import llama_service
            
            try:
                rwanda_fact = await rwanda_facts_service.get_creative_fact(llama_service)
                goodbye_msg = f"Before you go, here's something cool: {rwanda_fact} Thank you for learning with BAKAME! Keep practicing and have a wonderful day!"
            except Exception as e:
                print(f"Error getting Rwanda fact: {e}")
                goodbye_msg = "Thank you for using BAKAME! Keep learning and have a great day!"
            
            return Response(
                content=await twilio_service.create_voice_response(goodbye_msg, gather_input=False, call_sid=session_id, **tts_kwargs),
                media_type="application/xml"
            )
        
        return Response(
            content=await twilio_service.create_voice_response(ai_response, call_sid=session_id, **tts_kwargs),
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
        
        sentiment_result = sentiment_service.analyze_sentiment(user_input)
        user_context["current_sentiment"] = sentiment_result.sentiment
        
        tts_kwargs = {}
        if sentiment_result.sentiment == "frustrated":
            tts_kwargs["rate"] = 0.85
            
        ai_response = await current_module.process_input(user_input, user_context)
        
        if sentiment_result.sentiment == "frustrated":
            encouragement = sentiment_service.get_encouraging_response("frustrated")
            ai_response = f"{encouragement} {ai_response}"
        
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
