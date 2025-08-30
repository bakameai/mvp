import asyncio
import sys
import os
sys.path.append('/home/ubuntu/repos/mvp/bakame-backend')

from app.services.elevenlabs_service import elevenlabs_service
from app.services.mcp_client import mcp_client
from app.services.twilio_service import TwilioService
from app.services.redis_service import redis_service

async def test_elevenlabs_integration():
    print("=== Testing ElevenLabs Integration ===")
    
    print("\n1. Testing ElevenLabs Service:")
    
    user_context = {
        "user_name": "Amahoro",
        "phone_number": "+250123456789",
        "current_module": "grammar",
        "curriculum_stage": "remember"
    }
    
    conversation_id = await elevenlabs_service.create_conversation("+250123456789", user_context)
    if conversation_id:
        print(f"✓ Conversation created: {conversation_id}")
        
        response = await elevenlabs_service.send_message(conversation_id, "Hello, I want to practice English grammar")
        if response:
            print(f"✓ Message sent, response: {response[:100]}...")
        else:
            print("✗ Message sending failed")
    else:
        print("✗ Conversation creation failed")
    
    print("\n2. Testing MCP Client:")
    
    profile = await mcp_client.get_student_profile("+250123456789")
    if profile:
        print(f"✓ Student profile retrieved: {profile.get('phone_number')}")
    else:
        print("✗ Student profile retrieval failed")
    
    progress_updated = await mcp_client.update_student_progress(
        "+250123456789", "grammar", "remember", 0.8, True
    )
    if progress_updated:
        print("✓ Student progress updated")
    else:
        print("✗ Student progress update failed")
    
    evaluation_logged = await mcp_client.log_evaluation(
        "+250123456789", "grammar", "remember", 
        "Yesterday I went to school", 0.8, True, "neutral", "Good work!"
    )
    if evaluation_logged:
        print("✓ Evaluation logged")
    else:
        print("✗ Evaluation logging failed")
    
    print("\n3. Testing Twilio Service Integration:")
    
    twilio_service = TwilioService()
    
    twiml_response = await twilio_service.create_voice_response(
        "Welcome to BAKAME! Let's practice English grammar.",
        gather_input=True,
        call_sid="test_call_123",
        user_context=user_context
    )
    
    if "elevenlabs" in twiml_response.lower() or "play" in twiml_response.lower():
        print("✓ TwiML response generated with ElevenLabs integration")
    else:
        print("✓ TwiML response generated with fallback")
    
    print(f"TwiML Response: {twiml_response[:200]}...")
    
    print("\n4. Testing Redis Session Management:")
    
    redis_service.set_session_data("test_call_123", "elevenlabs_conversation_id", conversation_id, ttl=3600)
    stored_conversation_id = redis_service.get_session_data("test_call_123", "elevenlabs_conversation_id")
    
    if stored_conversation_id == conversation_id:
        print("✓ Redis session management working")
    else:
        print("✗ Redis session management failed")
    
    print("\n=== ElevenLabs Integration Testing Complete ===")

if __name__ == "__main__":
    asyncio.run(test_elevenlabs_integration())
