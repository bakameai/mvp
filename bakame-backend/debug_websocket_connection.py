import asyncio
import json
import base64
import websockets
import os
from app.elevenlabs_client import open_el_ws

async def debug_websocket_connection():
    """Debug WebSocket connection stability issues"""
    try:
        print("🔍 Testing WebSocket connection stability...")
        
        os.environ["ELEVENLABS_AGENT_ID"] = "agent_0301k3y6dwrve63sb37n6f4ffkrj"
        os.environ["ELEVENLABS_WS_SECRET"] = os.environ.get("Bakame11L", "")
        
        el_ws = await open_el_ws()
        print("✅ ElevenLabs WebSocket connected")
        
        print(f"WebSocket state: {el_ws.state}")
        print(f"WebSocket closed: {el_ws.closed}")
        
        sample_audio = b'\x00\x01' * 160
        audio_b64 = base64.b64encode(sample_audio).decode('utf-8')
        
        for i in range(5):
            try:
                test_message = {"user_audio_chunk": audio_b64}
                await el_ws.send(json.dumps(test_message))
                print(f"✅ Test {i+1}: Audio sent successfully")
                
                try:
                    response = await asyncio.wait_for(el_ws.recv(), timeout=1.0)
                    if isinstance(response, (bytes, bytearray)):
                        print(f"📥 Test {i+1}: Received binary response ({len(response)} bytes)")
                    else:
                        msg = json.loads(response)
                        print(f"📥 Test {i+1}: Received JSON: {msg.get('type', 'unknown')}")
                except asyncio.TimeoutError:
                    print(f"⏰ Test {i+1}: No response received")
                
                print(f"WebSocket state after test {i+1}: {el_ws.state}")
                
            except Exception as e:
                print(f"❌ Test {i+1} failed: {e}")
                print(f"WebSocket state: {el_ws.state}")
                print(f"WebSocket closed: {el_ws.closed}")
                break
        
        await el_ws.close()
        print("🎯 WebSocket connection test completed")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_websocket_connection())
    if success:
        print("\n🎉 WEBSOCKET CONNECTION TEST COMPLETED!")
    else:
        print("\n💥 WEBSOCKET CONNECTION TEST FAILED!")
