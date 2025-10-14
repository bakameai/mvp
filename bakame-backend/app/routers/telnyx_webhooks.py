from fastapi import APIRouter, Request, Response, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
import logging
import os
from app.services.telnyx_service import telnyx_service
from app.services.voice_bridge_service import voice_bridge_service
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
            # Speaking has finished, ready for next action
            logger.info(f"[Telnyx Webhook] Speak ended for call {call_control_id}")
            # Could initiate gather here if needed
            
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
            # Recording available (if recording was enabled)
            recording_url = payload.get("recording_urls", {}).get("wav")
            logger.info(f"[Telnyx Webhook] Recording saved: {recording_url}")
            
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
    Handle call answered event - start media streaming and connect to OpenAI Realtime API
    """
    try:
        logger.info(f"[Telnyx] Call answered, starting OpenAI Realtime voice session")
        
        # Get the WebSocket URL for media streaming
        # Use environment variable for the Replit domain
        replit_domain = os.getenv("REPLIT_DOMAINS", "localhost")
        stream_url = f"wss://{replit_domain}:8000/telnyx/stream/{call_control_id}"
        
        # Start media streaming to our WebSocket endpoint
        await telnyx_service.start_streaming(
            call_control_id=call_control_id,
            stream_url=stream_url,
            track="both_tracks",  # Stream both caller and AI audio
            codec="PCMU"  # G.711 µ-law codec (case-sensitive!)
        )
        
        logger.info(f"[Telnyx] Media streaming started for {from_number}")
        
    except Exception as e:
        logger.error(f"[Telnyx] Error sending welcome message: {str(e)}")

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

@router.websocket("/stream/{call_control_id}")
async def telnyx_media_stream(websocket: WebSocket, call_control_id: str):
    """
    WebSocket endpoint to receive Telnyx media streams and bridge to OpenAI Realtime API.
    """
    await websocket.accept()
    logger.info(f"[Telnyx Stream] WebSocket connected for call: {call_control_id}")
    
    try:
        # Start voice AI session with bidirectional audio streaming
        await voice_bridge_service.start_session(call_control_id, websocket)
        
    except WebSocketDisconnect:
        logger.info(f"[Telnyx Stream] WebSocket disconnected for call: {call_control_id}")
    except Exception as e:
        logger.error(f"[Telnyx Stream] Error in media stream: {str(e)}")
    finally:
        # Cleanup
        await voice_bridge_service.end_session(call_control_id)

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