from fastapi import APIRouter, Request, Response, HTTPException
from typing import Dict, Any, Optional
import json
import logging
import os
import asyncio
import requests
from app.services.telnyx_service import telnyx_service
from app.services.stt_service import stt_service
from app.modules.general_module import general_module

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Store call sessions for maintaining context
call_sessions = {}

@router.post("/incoming")
async def handle_telnyx_webhook(request: Request):
    """
    Main webhook endpoint for all Telnyx events
    Replaces the old /webhook/call endpoint from Twilio
    """
    try:
        # Get the raw body for signature verification
        body = await request.body()
        
        # Parse JSON payload
        webhook_data = await request.json()
        
        # Log all webhook events for debugging
        logger.info(f"[Telnyx Webhook] Received event: {json.dumps(webhook_data, indent=2)}")
        
        # Verify webhook signature (optional but recommended for production)
        # signature = request.headers.get("telnyx-signature")
        # if not telnyx_service.verify_webhook_signature(body, signature):
        #     logger.error("Invalid webhook signature")
        #     raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Extract event data
        event_data = webhook_data.get("data", {})
        event_type = event_data.get("event_type")
        payload = event_data.get("payload", {})
        
        # Extract common fields
        call_control_id = payload.get("call_control_id")
        call_session_id = payload.get("call_session_id")
        from_number = payload.get("from")
        to_number = payload.get("to")
        
        logger.info(f"[Telnyx Webhook] Event Type: {event_type}")
        logger.info(f"[Telnyx Webhook] Call Control ID: {call_control_id}")
        logger.info(f"[Telnyx Webhook] From: {from_number} -> To: {to_number}")
        
        # Handle different event types
        if event_type == "call.initiated":
            # New incoming call
            await handle_call_initiated(call_control_id, from_number)
            
        elif event_type == "call.answered":
            # Call was answered successfully
            await handle_call_answered(call_control_id, from_number)
            
        elif event_type == "call.speak.ended":
            # Speaking has finished, start recording for next user input
            logger.info(f"[Telnyx Webhook] Speak ended for call {call_control_id}, starting recording")
            await handle_speak_ended(call_control_id, from_number)
            
        elif event_type == "call.gather.ended":
            # User input received
            digits = payload.get("digits")
            await handle_gather_ended(call_control_id, from_number, digits)
            
        elif event_type == "call.hangup":
            # Call ended
            logger.info(f"[Telnyx Webhook] Call {call_control_id} hung up")
            # Clean up session
            if call_session_id in call_sessions:
                del call_sessions[call_session_id]
                
        elif event_type == "call.recording.saved":
            # Recording available - process with STT → AI → TTS
            # recording_urls is a list, get the first WAV URL
            recording_urls = payload.get("recording_urls", [])
            recording_url = None
            if isinstance(recording_urls, list) and len(recording_urls) > 0:
                recording_url = recording_urls[0]
            logger.info(f"[Telnyx Webhook] Recording saved: {recording_url}")
            await handle_recording_saved(call_control_id, from_number, recording_url)
            
        else:
            logger.info(f"[Telnyx Webhook] Unhandled event type: {event_type}")
        
        # Return 200 OK to acknowledge webhook receipt
        return {"status": "ok", "message": f"Event {event_type} processed"}
        
    except json.JSONDecodeError as e:
        logger.error(f"[Telnyx Webhook] JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"[Telnyx Webhook] Error processing webhook: {str(e)}")
        # Return 200 to prevent retries even on error
        return {"status": "error", "message": str(e)}

async def handle_call_initiated(call_control_id: str, from_number: str):
    """
    Handle new incoming call - equivalent to Twilio's initial /webhook/call
    """
    try:
        logger.info(f"[Telnyx] Handling new call from {from_number}")
        
        # Answer the call first
        await telnyx_service.answer_call(call_control_id)
        
    except Exception as e:
        logger.error(f"[Telnyx] Error handling call initiated: {str(e)}")

async def handle_call_answered(call_control_id: str, from_number: str):
    """
    Handle call answered event - speak greeting
    Recording will start automatically when call.speak.ended event fires
    """
    try:
        logger.info(f"[Telnyx] Call answered from {from_number}")
        
        # Speak a greeting - recording will start when speak ends
        greeting = "Hello! I'm your AI assistant. How can I help you today?"
        await telnyx_service.speak(
            call_control_id=call_control_id,
            text=greeting,
            voice="male",
            language="en-US"
        )
        
        logger.info(f"[Telnyx] Greeting sent to {from_number}")
        
    except Exception as e:
        logger.error(f"[Telnyx] Error in call answered handler: {str(e)}")

async def handle_speak_ended(call_control_id: str, from_number: str):
    """
    Handle speak ended event - start recording for user input
    """
    try:
        logger.info(f"[Telnyx] Starting recording for {from_number}")
        
        await telnyx_service.start_recording(
            call_control_id=call_control_id,
            format="wav",
            channels="single",
            max_length=30
        )
        
        logger.info(f"[Telnyx] Recording started for {from_number}")
        
    except Exception as e:
        logger.error(f"[Telnyx] Error starting recording: {str(e)}")

async def handle_gather_ended(call_control_id: str, from_number: str, digits: str = ""):
    """
    Handle user input - equivalent to Twilio's /webhook/voice/process
    """
    try:
        user_input = digits if digits else "..."
        logger.info(f"[Telnyx] Received input from {from_number}: {user_input}")
        
        # Get AI response (same as before)
        ai_response = await general_module.process(user_input, {})
        
        # Send response and gather more input
        # This replaces the Twilio <Gather> + <Say> combination
        await telnyx_service.gather_using_speak(
            call_control_id=call_control_id,
            prompt_text=ai_response,
            timeout_millis=60000,  # 60 seconds
            voice="male",
            language="en-US"
        )
        
        logger.info(f"[Telnyx] AI response sent to {from_number}")
        
    except Exception as e:
        logger.error(f"[Telnyx] Error processing user input: {str(e)}")
        
        # Send error message
        try:
            error_response = await general_module.process("System error occurred", {})
            await telnyx_service.speak(
                call_control_id=call_control_id,
                text=error_response,
                voice="male",
                language="en-US"
            )
        except:
            # If all else fails, just speak a generic error
            await telnyx_service.speak(
                call_control_id=call_control_id,
                text="I'm sorry, there was an error processing your request.",
                voice="male",
                language="en-US"
            )

async def handle_recording_saved(call_control_id: str, from_number: str, recording_url: Optional[str]):
    """
    Handle saved recording - traditional STT → AI → TTS pipeline
    Recording will restart automatically when call.speak.ended event fires
    """
    try:
        # Validate recording URL
        if not recording_url:
            logger.error(f"[Telnyx] No recording URL provided for {from_number}")
            # Stop any ongoing recording and speak error
            try:
                await telnyx_service.stop_recording(call_control_id)
            except:
                pass
            await telnyx_service.speak(
                call_control_id=call_control_id,
                text="I'm sorry, there was a problem with the recording.",
                voice="male",
                language="en-US"
            )
            return
        
        logger.info(f"[Telnyx] Processing recording from {from_number}")
        
        # Step 1: Download the recording (async with executor to avoid blocking)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.get(recording_url, timeout=30)
        )
        response.raise_for_status()
        audio_data = response.content
        
        logger.info(f"[Telnyx] Downloaded {len(audio_data)} bytes of audio")
        
        # Step 2: Transcribe with STT (OpenAI Whisper)
        transcription = await stt_service.transcribe_audio(audio_data, audio_format="wav")
        
        if not transcription or transcription.strip() == "":
            logger.warning(f"[Telnyx] Empty transcription for {from_number}, asking to repeat")
            # Stop recording before speaking
            try:
                await telnyx_service.stop_recording(call_control_id)
            except:
                pass
            await telnyx_service.speak(
                call_control_id=call_control_id,
                text="I'm sorry, I didn't catch that. Could you please repeat?",
                voice="male",
                language="en-US"
            )
            return
        
        logger.info(f"[Telnyx] User said: {transcription}")
        
        # Step 3: Process with AI
        ai_response = await general_module.process(transcription, {})
        logger.info(f"[Telnyx] AI response: {ai_response}")
        
        # Step 4: Stop recording before speaking (ensures recording.saved event fires promptly)
        try:
            await telnyx_service.stop_recording(call_control_id)
        except Exception as e:
            logger.warning(f"[Telnyx] Could not stop recording (may not be active): {str(e)}")
        
        # Step 5: Speak the AI response using TTS
        # Recording will automatically restart when call.speak.ended fires
        await telnyx_service.speak(
            call_control_id=call_control_id,
            text=ai_response,
            voice="male",
            language="en-US"
        )
        
        logger.info(f"[Telnyx] AI response sent, waiting for speak.ended to restart recording")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[Telnyx] Error downloading recording: {str(e)}")
        try:
            await telnyx_service.stop_recording(call_control_id)
        except:
            pass
        try:
            await telnyx_service.speak(
                call_control_id=call_control_id,
                text="I'm sorry, I had trouble accessing the recording. Please try again.",
                voice="male",
                language="en-US"
            )
        except:
            pass
    except Exception as e:
        logger.error(f"[Telnyx] Error processing recording: {str(e)}")
        try:
            await telnyx_service.stop_recording(call_control_id)
        except:
            pass
        try:
            await telnyx_service.speak(
                call_control_id=call_control_id,
                text="I'm sorry, there was an error processing your message. Please try again.",
                voice="male",
                language="en-US"
            )
        except:
            pass

@router.post("/outbound/call")
async def make_outbound_call(to_number: str, message: str):
    """
    Initiate an outbound call (optional - for future use)
    """
    try:
        import telnyx
        from app.config import settings
        telnyx.api_key = settings.telnyx_api_key
        
        call_response = telnyx.Call.create(
            to=to_number,
            from_=telnyx_service.phone_number,
            webhook_url="https://your-domain.com/telnyx/incoming",
            webhook_url_method="POST"
        )
        
        # Extract call_control_id from response
        call_control_id = call_response.get("call_control_id", "")
        
        # Store initial message for when call is answered
        call_sessions[call_control_id] = {
            "initial_message": message
        }
        
        return {
            "status": "success",
            "call_id": call_control_id,
            "message": "Outbound call initiated"
        }
        
    except Exception as e:
        logger.error(f"[Telnyx] Error making outbound call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "BAKAME Telnyx Integration",
        "provider": "Telnyx"
    }

# Debugging endpoint to test Telnyx connection
@router.post("/test/speak")
async def test_speak(call_control_id: str, message: str):
    """
    Test endpoint to send a speak command directly
    Useful for debugging
    """
    try:
        result = await telnyx_service.speak(
            call_control_id=call_control_id,
            text=message,
            voice="male",
            language="en-US"
        )
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"[Telnyx Test] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))