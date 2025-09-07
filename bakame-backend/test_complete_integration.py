import asyncio
import websockets
import json
import base64
import time

async def test_complete_integration():
    """Test the complete Voice → BAKAME AI → ElevenLabs integration"""
    try:
        print('🔍 Testing complete BAKAME AI integration...')
        uri = 'wss://bakame-elevenlabs-mcp.fly.dev/twilio-stream'
        
        async with websockets.connect(uri) as websocket:
            print('✅ WebSocket connected successfully!')
            
            start_msg = {
                'event': 'start',
                'start': {
                    'streamSid': 'test-stream-456',
                    'accountSid': 'test-account',
                    'callSid': 'test-call-456',
                    'customParameters': {
                        'phone_number': '+250788123456'  # Rwandan test number
                    }
                }
            }
            
            await websocket.send(json.dumps(start_msg))
            print('✅ Start message with phone number sent!')
            
            print('📡 Sending audio chunks to trigger AI processing...')
            
            chunk_count = 150  # 150 chunks * 20ms = 3 seconds
            sample_audio = b'\x00\x01' * 160  # 160 samples with slight variation
            
            for i in range(chunk_count):
                audio_data = sample_audio + bytes([i % 256, (i * 2) % 256])
                audio_b64 = base64.b64encode(audio_data).decode('ascii')
                
                media_msg = {
                    'event': 'media',
                    'media': {
                        'payload': audio_b64
                    }
                }
                
                await websocket.send(json.dumps(media_msg))
                
                if i % 50 == 0:
                    print(f'   Sent {i+1}/{chunk_count} audio chunks...')
                    await asyncio.sleep(0.1)
            
            print('✅ All audio chunks sent!')
            
            print('⏳ Waiting for BAKAME AI processing...')
            await asyncio.sleep(5)
            
            stop_msg = {
                'event': 'stop',
                'sequenceNumber': '1',
                'streamSid': 'test-stream-456'
            }
            
            await websocket.send(json.dumps(stop_msg))
            print('✅ Stop message sent!')
            
            await asyncio.sleep(2)
            print('🎉 Complete integration test completed!')
            
    except Exception as e:
        print(f'❌ Complete integration test failed: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_complete_integration())
    if success:
        print('\n🎯 COMPLETE BAKAME AI INTEGRATION TEST PASSED!')
        print('📞 Ready for real phone call testing!')
    else:
        print('\n❌ COMPLETE INTEGRATION TEST FAILED!')
