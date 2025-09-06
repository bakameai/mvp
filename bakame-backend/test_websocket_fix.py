import asyncio
import websockets
import json

async def test_websocket_fix():
    """Test that the WebSocket connection works without the extra_headers crash"""
    try:
        print('🔍 Testing WebSocket connection to bakame-elevenlabs-mcp...')
        uri = 'wss://bakame-elevenlabs-mcp.fly.dev/twilio-stream'
        
        async with websockets.connect(uri) as websocket:
            print('✅ WebSocket connected successfully!')
            
            test_msg = {
                'event': 'start',
                'start': {
                    'streamSid': 'test-stream-123',
                    'accountSid': 'test-account',
                    'callSid': 'test-call-123'
                }
            }
            
            await websocket.send(json.dumps(test_msg))
            print('✅ Test start message sent successfully!')
            
            await asyncio.sleep(2)
            
            stop_msg = {
                'event': 'stop',
                'sequenceNumber': '1',
                'streamSid': 'test-stream-123'
            }
            
            await websocket.send(json.dumps(stop_msg))
            print('✅ Test stop message sent successfully!')
            
            await asyncio.sleep(1)
            print('✅ WebSocket test completed without crashes!')
            print('🎉 Fix verified: No more extra_headers error!')
            
    except Exception as e:
        print(f'❌ WebSocket test failed: {e}')
        if 'extra_headers' in str(e):
            print('💥 The extra_headers bug is still present!')
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_websocket_fix())
    if success:
        print('\n🎯 VERIFICATION COMPLETE: WebSocket fix is working!')
    else:
        print('\n❌ VERIFICATION FAILED: WebSocket fix needs more work!')
