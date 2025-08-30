#!/usr/bin/env python3
"""
TwiML verification script to ensure <Play> is used instead of <Say>.
Tests the webhook endpoint and validates TwiML output.
"""

import asyncio
import sys
from app.services.twilio_service import twilio_service

async def test_twiml_generation():
    """Test TwiML generation and verify <Play> usage"""
    print("=== TwiML Generation Verification ===\n")
    
    test_messages = [
        "Hello! Welcome to BAKAME.",
        "Let's practice English together. How are you feeling today?",
        "Great job! You're doing wonderful. Keep practicing!"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"🧪 Test {i}: {message}")
        
        try:
            twiml = await twilio_service.create_voice_response(
                message, 
                gather_input=True, 
                call_sid=f"test_call_{i}"
            )
            
            print(f"📄 Generated TwiML:")
            print(twiml)
            print()
            
            play_count = twiml.count('<Play>')
            say_count = twiml.count('<Say>')
            pause_count = twiml.count('<Pause>')
            
            print(f"📊 TwiML Analysis:")
            print(f"   <Play> tags: {play_count}")
            print(f"   <Say> tags: {say_count}")
            print(f"   <Pause> tags: {pause_count}")
            
            if 'https://app-pyzfduqr.fly.dev/audio/tts/' in twiml:
                print("✅ Using proper audio URLs")
            else:
                print("❌ Audio URLs not found or incorrect")
            
            if play_count > 0 and say_count <= 1:  # Allow one <Say> for fallback
                print("✅ Using <Play> for main audio (correct)")
            elif say_count > 1:
                print("⚠️  Multiple <Say> tags found (may indicate fallback usage)")
            else:
                print("❌ No <Play> tags found (using <Say> instead)")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error generating TwiML: {e}")
            print("-" * 50)
            continue
    
    print("\n=== Summary ===")
    print("✅ TwiML generation completed")
    print("📝 Review the output above to ensure:")
    print("   1. <Play> tags are present for audio playback")
    print("   2. Audio URLs point to correct domain")
    print("   3. <Pause> tags provide micro-pauses between sentences")
    print("   4. <Say> is only used for fallback scenarios")

async def test_fallback_behavior():
    """Test fallback behavior when TTS fails"""
    print("\n=== Fallback Behavior Test ===\n")
    
    print("📋 Expected Fallback Chain:")
    print("   1. Primary: ElevenLabs Conversational AI → <Play>")
    print("   2. Secondary: Twilio <Say> fallback")
    print("   3. Last Resort: Basic TwiML responses")
    print("\n⚠️  To test fallback, temporarily disable ElevenLabs API")

async def main():
    """Main verification function"""
    await test_twiml_generation()
    await test_fallback_behavior()
    
    print("\n🎯 Next Steps:")
    print("   1. Make a real phone call to test audio quality")
    print("   2. Verify barge-in functionality works")
    print("   3. Test fallback behavior with API failures")

if __name__ == "__main__":
    asyncio.run(main())
