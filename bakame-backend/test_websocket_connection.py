import asyncio
import websockets
import json

async def test_websocket():
    try:
        print('Testing WebSocket connection to bakame-elevenlabs-mcp...')
        uri = 'wss://bakame-elevenlabs-mcp.fly.dev/twilio-stream'
        
        async with websockets.connect(uri) as websocket:
            print('✅ WebSocket connected successfully!')
            
            start_msg = {
                'event': 'start',
                'start': {
                    'streamSid': 'test-stream-123',
                    'accountSid': 'test-account',
                    'callSid': 'test-call-123'
                }
            }
            
            await websocket.send(json.dumps(start_msg))
            print('✅ Test start message sent!')
            
            await asyncio.sleep(2)
            
            stop_msg = {
                'event': 'stop',
                'sequenceNumber': '1',
                'streamSid': 'test-stream-123'
            }
            
            await websocket.send(json.dumps(stop_msg))
            print('✅ Test stop message sent!')
            
            await asyncio.sleep(1)
            print('🎉 WebSocket test completed successfully!')
            
    except Exception as e:
        print(f'❌ WebSocket test failed: {e}')
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    print(f'\nTest result: {"PASSED" if success else "FAILED"}')
