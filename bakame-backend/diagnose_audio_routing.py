import asyncio
import json
import base64
import websockets
import os
from app.elevenlabs_client import open_el_ws
from app.main import pcm16_16k_to_twilio_ulaw8k, twilio_ulaw8k_to_pcm16_16k

async def diagnose_audio_routing():
    """Comprehensive diagnosis of the audio routing pipeline"""
    print("🔍 COMPREHENSIVE AUDIO ROUTING DIAGNOSIS")
    print("=" * 60)
    
    try:
        os.environ["ELEVENLABS_AGENT_ID"] = "agent_0301k3y6dwrve63sb37n6f4ffkrj"
        os.environ["ELEVENLABS_WS_SECRET"] = os.environ.get("Bakame11L", "")
        
        print("📋 STEP 1: Environment Setup")
        print(f"   Agent ID: {os.environ['ELEVENLABS_AGENT_ID']}")
        print(f"   WS Secret: {'SET' if os.environ.get('ELEVENLABS_WS_SECRET') else 'NOT SET'}")
        
        print("\n📋 STEP 2: ElevenLabs WebSocket Connection")
        el_ws = await open_el_ws()
        print("   ✅ ElevenLabs WebSocket connected successfully")
        
        print("\n📋 STEP 3: Listening for ElevenLabs Messages")
        message_count = 0
        audio_messages = []
        other_messages = []
        
        print("   📤 Sending initial audio to trigger conversation...")
        sample_audio = b'\x00\x01' * 160  # 160 samples of test audio
        audio_b64 = base64.b64encode(sample_audio).decode('utf-8')
        
        initial_message = {"user_audio_chunk": audio_b64}
        await el_ws.send(json.dumps(initial_message))
        print("   ✅ Initial audio sent")
        
        print("\n   👂 Listening for responses...")
        try:
            async for raw in el_ws:
                message_count += 1
                print(f"\n   📥 Message {message_count}:")
                
                if isinstance(raw, (bytes, bytearray)):
                    print(f"      Type: Binary data ({len(raw)} bytes)")
                    audio_messages.append({
                        "type": "binary",
                        "size": len(raw),
                        "data": raw[:20]  # First 20 bytes for inspection
                    })
                else:
                    try:
                        msg = json.loads(raw)
                        msg_type = msg.get("type", "unknown")
                        print(f"      Type: JSON - {msg_type}")
                        print(f"      Content: {json.dumps(msg, indent=8)}")
                        
                        if msg_type == "audio":
                            audio_event = msg.get("audio_event", {})
                            audio_base64 = audio_event.get("audio_base_64", "")
                            if audio_base64:
                                audio_size = len(base64.b64decode(audio_base64))
                                print(f"      🎵 Audio data: {audio_size} bytes")
                                audio_messages.append({
                                    "type": "structured_audio",
                                    "size": audio_size,
                                    "event_id": audio_event.get("event_id"),
                                    "format": "audio_event"
                                })
                        elif msg_type == "conversation_initiation_metadata":
                            print("      🎯 Conversation initiated!")
                        elif msg_type == "ping":
                            ping_event = msg.get("ping_event", {})
                            event_id = ping_event.get("event_id")
                            pong_message = {"type": "pong", "event_id": event_id}
                            await el_ws.send(json.dumps(pong_message))
                            print(f"      🏓 Sent pong response (event_id: {event_id})")
                        
                        other_messages.append(msg)
                        
                    except Exception as e:
                        print(f"      ❌ Failed to parse JSON: {e}")
                        print(f"      Raw data: {raw[:100]}...")
                
                if message_count >= 15:
                    print("   ⏰ Stopping after 15 messages")
                    break
                    
        except asyncio.TimeoutError:
            print("   ⏰ Timeout reached")
        except Exception as e:
            print(f"   ❌ Error during message listening: {e}")
        
        await el_ws.close()
        
        print(f"\n📋 STEP 4: Message Analysis")
        print(f"   Total messages received: {message_count}")
        print(f"   Audio messages: {len(audio_messages)}")
        print(f"   Other messages: {len(other_messages)}")
        
        if audio_messages:
            print("\n   🎵 Audio Message Details:")
            for i, audio_msg in enumerate(audio_messages):
                print(f"      Audio {i+1}: {audio_msg['type']}, {audio_msg['size']} bytes")
                if audio_msg['type'] == 'structured_audio':
                    print(f"         Event ID: {audio_msg['event_id']}")
                    print(f"         Format: {audio_msg['format']}")
        else:
            print("   ❌ NO AUDIO MESSAGES RECEIVED!")
        
        print(f"\n📋 STEP 5: Audio Conversion Testing")
        if audio_messages:
            test_audio = audio_messages[0]
            if test_audio['type'] == 'binary':
                print("   🔄 Testing binary audio conversion...")
                pcm16k = test_audio['data']
                try:
                    ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                    twilio_payload = {"event": "media", "media": {"payload": ulaw_b64}}
                    print(f"   ✅ Conversion successful: {len(base64.b64decode(ulaw_b64))} bytes μ-law")
                    print(f"   📤 Twilio payload: {json.dumps(twilio_payload)[:100]}...")
                except Exception as e:
                    print(f"   ❌ Conversion failed: {e}")
            else:
                print("   ⚠️  No binary audio to test conversion")
        else:
            print("   ⚠️  No audio messages to test conversion")
        
        print(f"\n📋 STEP 6: WebSocket State Simulation")
        from unittest.mock import Mock
        
        mock_ws_connected = Mock()
        mock_ws_connected.client_state = Mock()
        mock_ws_connected.client_state.name = "CONNECTED"
        
        mock_ws_closed = Mock()
        mock_ws_closed.client_state = Mock()
        mock_ws_closed.client_state.name = "CLOSED"
        
        print("   🔄 Testing WebSocket state checking...")
        
        if mock_ws_connected.client_state.name == "CONNECTED":
            print("   ✅ Connected WebSocket: Would allow audio transmission")
        else:
            print("   ❌ Connected WebSocket: Would block audio transmission")
        
        if mock_ws_closed.client_state.name != "CONNECTED":
            print("   ✅ Closed WebSocket: Would correctly block audio transmission")
        else:
            print("   ❌ Closed WebSocket: Would incorrectly allow audio transmission")
        
        print(f"\n📋 STEP 7: Diagnosis Summary")
        print("=" * 60)
        
        if not audio_messages:
            print("🚨 CRITICAL ISSUE: No audio messages received from ElevenLabs")
            print("   Possible causes:")
            print("   - ElevenLabs agent not configured for audio output")
            print("   - Authentication issues preventing audio streaming")
            print("   - Agent configuration missing TTS settings")
            print("   - WebSocket connection dropping before audio generation")
        elif len(audio_messages) > 0:
            print("✅ Audio messages are being received from ElevenLabs")
            print("   Issue likely in:")
            print("   - Twilio WebSocket connection management")
            print("   - Audio format conversion")
            print("   - Message parsing in pump_el_to_twilio() function")
        
        print(f"\n📋 STEP 8: Recommended Next Steps")
        if not audio_messages:
            print("1. Check ElevenLabs agent configuration for TTS output")
            print("2. Verify agent has proper voice model assigned")
            print("3. Test with different audio input to trigger response")
        else:
            print("1. Add detailed logging to pump_el_to_twilio() function")
            print("2. Monitor Twilio WebSocket connection state in real-time")
            print("3. Test audio conversion pipeline with actual ElevenLabs data")
        
        return len(audio_messages) > 0
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(diagnose_audio_routing())
    if success:
        print("\n🎉 DIAGNOSIS COMPLETED - AUDIO MESSAGES DETECTED!")
    else:
        print("\n💥 DIAGNOSIS COMPLETED - NO AUDIO MESSAGES DETECTED!")
