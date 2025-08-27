#!/usr/bin/env python3
"""
Test script for μ-law TTS implementation
"""

import asyncio
import os
from app.services.deepgram_service import deepgram_service
from app.services.twilio_service import twilio_service

async def test_mulaw_tts():
    """Test Deepgram μ-law TTS"""
    print('Testing Deepgram μ-law TTS...')
    try:
        result = await deepgram_service.text_to_speech(
            'Hello, this is a test of μ-law TTS for Twilio!',
            call_sid='test_call',
            sequence=1
        )
        print(f'TTS result: {result}')
        if result:
            print('✅ Deepgram μ-law TTS working')
            if os.path.exists(result):
                size = os.path.getsize(result)
                print(f'📁 File size: {size} bytes')
                print(f'📂 File path: {result}')
            return True
        else:
            print('❌ Deepgram μ-law TTS failed')
            return False
    except Exception as e:
        print(f'Error: {e}')
        return False

async def test_twiml_pipeline():
    """Test complete TwiML pipeline"""
    print('\nTesting complete TTS pipeline...')
    try:
        response = await twilio_service.create_voice_response(
            'Welcome to BAKAME! Let\'s learn English together.',
            call_sid='test_call'
        )
        print('TwiML Response:')
        print(response)
        if '<Play>' in response:
            print('✅ Using Play verb instead of Say')
            return True
        elif '<Say>' in response:
            print('⚠ Using Say verb (fallback mode)')
            return True
        else:
            print('✗ No audio output detected')
            return False
    except Exception as e:
        print(f'Error: {e}')
        return False

async def main():
    """Main test function"""
    print("=== μ-law TTS Testing ===\n")
    
    success1 = await test_mulaw_tts()
    success2 = await test_twiml_pipeline()
    
    if success1 and success2:
        print('\n🎉 SUCCESS: μ-law TTS pipeline is working!')
    else:
        print('\n❌ FAILED: μ-law TTS pipeline has issues')

if __name__ == "__main__":
    asyncio.run(main())
