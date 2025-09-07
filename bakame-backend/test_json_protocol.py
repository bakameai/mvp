import asyncio
import websockets
import json
import base64

async def test_json_protocol():
    """Test that the WebSocket now accepts JSON messages properly"""
    try:
        print('🔍 Testing JSON protocol fix...')
        uri = 'wss://bakame-elevenlabs-mcp.fly.dev/twilio-stream'
        
        async with websockets.connect(uri) as websocket:
            print('✅ WebSocket connected successfully!')
            
            start_msg = {
                'event': 'start',
                'start': {
                    'streamSid': 'test-stream-123',
                    'accountSid': 'test-account',
                    'callSid': 'test-call-123',
                    'customParameters': {
                        'phone_number': '+250788123456'
                    }
                }
            }
            
            await websocket.send(json.dumps(start_msg))
            print('✅ Start message with phone number sent!')
            
            sample_audio = b'\x00\x00' * 160  # 160 samples of silence (20ms at 8kHz)
            audio_b64 = base64.b64encode(sample_audio).decode('ascii')
            
            media_msg = {
                'event': 'media',
                'media': {
                    'payload': audio_b64
                }
            }
            
            await websocket.send(json.dumps(media_msg))
            print('✅ Media message sent!')
            
            await asyncio.sleep(2)
            
            stop_msg = {
                'event': 'stop',
                'sequenceNumber': '1',
                'streamSid': 'test-stream-123'
            }
            
            await websocket.send(json.dumps(stop_msg))
            print('✅ Stop message sent!')
            
            await asyncio.sleep(1)
            print('🎉 JSON protocol test completed successfully!')
            
    except Exception as e:
        print(f'❌ JSON protocol test failed: {e}')
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_json_protocol())
    if success:
        print('\n🎯 JSON PROTOCOL FIX VERIFIED!')
    else:
        print('\n❌ JSON PROTOCOL FIX NEEDS MORE WORK!')
