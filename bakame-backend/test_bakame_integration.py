import asyncio
import json
import base64
import audioop
from app.main import process_audio_buffer, twilio_ulaw8k_to_pcm16_16k

async def test_bakame_integration():
    """Test the BAKAME AI processing integration"""
    print("🔍 Testing BAKAME AI integration...")
    
    sample_rate = 16000
    duration = 2  # 2 seconds
    silence_pcm = b'\x00\x00' * (sample_rate * duration)
    
    audio_buffer = bytearray(silence_pcm)
    phone_number = "+250788123456"  # Test Rwandan phone number
    session_id = "test-session-123"
    
    try:
        print(f"✅ Testing audio buffer processing for {phone_number}")
        print(f"   Buffer size: {len(audio_buffer)} bytes")
        print(f"   Duration: ~{len(audio_buffer) / (sample_rate * 2):.1f} seconds")
        
        await process_audio_buffer(audio_buffer, phone_number, session_id, None)
        
        print("✅ BAKAME integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ BAKAME integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bakame_integration())
    if success:
        print("\n🎯 BAKAME AI INTEGRATION VERIFIED!")
    else:
        print("\n❌ BAKAME AI INTEGRATION NEEDS FIXES!")
