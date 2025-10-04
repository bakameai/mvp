import asyncio
import json
import base64
import websockets
from app.elevenlabs_client import open_el_ws

async def debug_message_formats():
    """Debug the exact message formats being sent to ElevenLabs"""
    try:
        print("🔍 Debugging ElevenLabs message formats...")
        
        el_ws = await open_el_ws()
        print("✅ ElevenLabs WebSocket connected successfully!")
        
        print("\n📤 Test 1: Sending documented format...")
        sample_audio = b'\x00\x01' * 160  # 160 samples of test audio
        audio_b64 = base64.b64encode(sample_audio).decode('utf-8')
        
        documented_message = {
            "user_audio_chunk": audio_b64
        }
        
        print(f"Message: {json.dumps(documented_message)[:100]}...")
        await el_ws.send(json.dumps(documented_message))
        print("✅ Documented format sent successfully!")
        
        print("\n📤 Test 2: Testing alternative formats...")
        
        alt_message_1 = {
            "user_audio_chunk": audio_b64,
            "timestamp": "2025-09-07T01:00:00Z"
        }
        
        print(f"Alt format 1: {json.dumps(alt_message_1)[:100]}...")
        await el_ws.send(json.dumps(alt_message_1))
        print("✅ Alternative format 1 sent!")
        
        alt_message_2 = {
            "type": "user_audio",
            "user_audio_chunk": audio_b64
        }
        
        print(f"Alt format 2: {json.dumps(alt_message_2)[:100]}...")
        await el_ws.send(json.dumps(alt_message_2))
        print("✅ Alternative format 2 sent!")
        
        print("\n👂 Listening for responses...")
        try:
            for i in range(3):
                response = await asyncio.wait_for(el_ws.recv(), timeout=3.0)
                msg = json.loads(response)
                print(f"📥 Response {i+1}: {msg}")
                
        except asyncio.TimeoutError:
            print("⏰ No more responses received")
        
        await el_ws.close()
        print("🎯 Message format debugging completed!")
        return True
        
    except Exception as e:
        print(f"❌ Message format debugging failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import os
    os.environ["ELEVENLABS_AGENT_ID"] = "agent_0301k3y6dwrve63sb37n6f4ffkrj"
    os.environ["ELEVENLABS_WS_SECRET"] = os.environ.get("Bakame11L", "")
    
    success = asyncio.run(debug_message_formats())
    if success:
        print("\n🎉 MESSAGE FORMAT DEBUGGING COMPLETED!")
    else:
        print("\n💥 MESSAGE FORMAT DEBUGGING FAILED!")
