import asyncio
import json
import base64
import websockets
import os
from app.elevenlabs_client import open_el_ws

async def debug_websocket_traffic():
    """Debug the exact WebSocket traffic to identify policy violation cause"""
    try:
        print("🔍 Debugging WebSocket traffic to identify policy violations...")
        
        os.environ["ELEVENLABS_AGENT_ID"] = "agent_0301k3y6dwrve63sb37n6f4ffkrj"
        os.environ["ELEVENLABS_WS_SECRET"] = os.environ.get("Bakame11L", "")
        
        print(f"[DEBUG] Agent ID: {os.environ['ELEVENLABS_AGENT_ID']}")
        print(f"[DEBUG] WS Secret set: {'Yes' if os.environ.get('ELEVENLABS_WS_SECRET') else 'No'}")
        
        el_ws = await open_el_ws()
        print("✅ ElevenLabs WebSocket connected successfully!")
        
        print("\n👂 Waiting for conversation initiation metadata...")
        el_ready = False
        
        async def listen_for_messages():
            nonlocal el_ready
            try:
                async for raw in el_ws:
                    if isinstance(raw, (bytes, bytearray)):
                        print(f"📥 Received binary data: {len(raw)} bytes")
                    else:
                        try:
                            msg = json.loads(raw)
                            print(f"📥 Received JSON: {msg}")
                            
                            if msg.get("type") == "conversation_initiation_metadata":
                                el_ready = True
                                print("✅ Conversation initiated! Ready to send audio.")
                                break
                        except Exception as e:
                            print(f"❌ Failed to parse message: {e}")
            except Exception as e:
                print(f"❌ Listen error: {e}")
        
        listen_task = asyncio.create_task(listen_for_messages())
        
        try:
            await asyncio.wait_for(listen_task, timeout=10.0)
        except asyncio.TimeoutError:
            print("⏰ Timeout waiting for conversation initiation")
            el_ready = True  # Proceed anyway for testing
        
        if el_ready:
            print("\n📤 Testing different audio message formats...")
            
            sample_audio = b'\x00\x01' * 160
            audio_b64 = base64.b64encode(sample_audio).decode('utf-8')
            
            test_message_1 = {
                "user_audio_chunk": audio_b64
            }
            
            print(f"Test 1 - Simple format: {json.dumps(test_message_1)[:100]}...")
            await el_ws.send(json.dumps(test_message_1))
            print("✅ Test 1 sent successfully!")
            
            import audioop
            ulaw_data = b'\xff\x7f' * 80  # Sample μ-law data
            pcm_data = audioop.ulaw2lin(ulaw_data, 2)
            pcm16k_data, _ = audioop.ratecv(pcm_data, 2, 1, 8000, 16000, None)
            
            real_audio_b64 = base64.b64encode(pcm16k_data).decode('utf-8')
            
            test_message_2 = {
                "user_audio_chunk": real_audio_b64
            }
            
            print(f"Test 2 - Twilio-like format: {json.dumps(test_message_2)[:100]}...")
            await el_ws.send(json.dumps(test_message_2))
            print("✅ Test 2 sent successfully!")
            
            empty_audio = b'\x00' * 320  # Silence
            empty_b64 = base64.b64encode(empty_audio).decode('utf-8')
            
            test_message_3 = {
                "user_audio_chunk": empty_b64
            }
            
            print(f"Test 3 - Silent audio: {json.dumps(test_message_3)[:100]}...")
            await el_ws.send(json.dumps(test_message_3))
            print("✅ Test 3 sent successfully!")
            
            print("\n👂 Listening for responses...")
            try:
                for i in range(5):
                    response = await asyncio.wait_for(el_ws.recv(), timeout=2.0)
                    if isinstance(response, (bytes, bytearray)):
                        print(f"📥 Response {i+1}: Binary data ({len(response)} bytes)")
                    else:
                        msg = json.loads(response)
                        print(f"📥 Response {i+1}: {msg}")
                        
            except asyncio.TimeoutError:
                print("⏰ No more responses received")
        
        await el_ws.close()
        print("🎯 WebSocket traffic debugging completed!")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket traffic debugging failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_websocket_traffic())
    if success:
        print("\n🎉 WEBSOCKET TRAFFIC DEBUGGING COMPLETED!")
    else:
        print("\n💥 WEBSOCKET TRAFFIC DEBUGGING FAILED!")
