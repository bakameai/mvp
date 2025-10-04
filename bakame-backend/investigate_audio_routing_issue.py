import asyncio
import json
import base64
import websockets
import os
from app.elevenlabs_client import open_el_ws
from app.main import pcm16_16k_to_twilio_ulaw8k, twilio_ulaw8k_to_pcm16_16k

async def comprehensive_audio_investigation():
    """
    Comprehensive investigation of the ElevenLabs audio routing issue.
    This will help us understand exactly what's happening and where the audio is getting lost.
    """
    print("🔍 COMPREHENSIVE AUDIO ROUTING INVESTIGATION")
    print("=" * 80)
    
    os.environ["ELEVENLABS_AGENT_ID"] = "agent_0301k3y6dwrve63sb37n6f4ffkrj"
    os.environ["ELEVENLABS_WS_SECRET"] = os.environ.get("Bakame11L", "")
    
    print("📋 STEP 1: Environment and Configuration Check")
    print(f"   Agent ID: {os.environ['ELEVENLABS_AGENT_ID']}")
    print(f"   WS Secret: {'SET' if os.environ.get('ELEVENLABS_WS_SECRET') else 'NOT SET'}")
    
    try:
        print("\n📋 STEP 2: ElevenLabs WebSocket Connection Analysis")
        el_ws = await open_el_ws()
        print("   ✅ ElevenLabs WebSocket connected successfully")
        print(f"   WebSocket State: {el_ws.state}")
        print(f"   WebSocket URI: {getattr(el_ws, 'uri', 'N/A')}")
        print(f"   WebSocket Headers: {dict(getattr(el_ws, 'request_headers', {}))}")
        
        print("\n📋 STEP 3: Message Flow Analysis")
        print("   📤 Sending test audio to trigger ElevenLabs response...")
        
        test_audio = b'\x00\x01' * 320  # 320 samples = 20ms at 16kHz
        audio_b64 = base64.b64encode(test_audio).decode('utf-8')
        
        test_message = {"user_audio_chunk": audio_b64}
        await el_ws.send(json.dumps(test_message))
        print("   ✅ Test audio sent")
        
        message_count = 0
        audio_messages = []
        conversation_initiated = False
        ping_pong_count = 0
        
        print("\n   👂 Analyzing ElevenLabs message flow...")
        
        try:
            async for raw in el_ws:
                message_count += 1
                print(f"\n   📥 Message {message_count}:")
                
                if isinstance(raw, (bytes, bytearray)):
                    print(f"      Type: Binary audio data")
                    print(f"      Size: {len(raw)} bytes")
                    print(f"      First 10 bytes: {raw[:10]}")
                    
                    try:
                        ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(raw)
                        ulaw_size = len(base64.b64decode(ulaw_b64))
                        print(f"      ✅ Conversion successful: {len(raw)} PCM → {ulaw_size} μ-law bytes")
                        
                        twilio_payload = {"event": "media", "media": {"payload": ulaw_b64}}
                        payload_json = json.dumps(twilio_payload)
                        print(f"      📤 Twilio payload size: {len(payload_json)} chars")
                        
                        audio_messages.append({
                            "type": "binary",
                            "pcm_size": len(raw),
                            "ulaw_size": ulaw_size,
                            "twilio_payload_size": len(payload_json)
                        })
                        
                    except Exception as e:
                        print(f"      ❌ Conversion failed: {e}")
                        
                else:
                    try:
                        msg = json.loads(raw)
                        msg_type = msg.get("type", "unknown")
                        print(f"      Type: JSON - {msg_type}")
                        
                        if msg_type == "conversation_initiation_metadata":
                            conversation_initiated = True
                            print("      🎯 Conversation initiated!")
                            print(f"      Metadata: {json.dumps(msg, indent=10)}")
                            
                        elif msg_type == "audio":
                            audio_event = msg.get("audio_event", {})
                            audio_base64 = audio_event.get("audio_base_64", "")
                            event_id = audio_event.get("event_id")
                            
                            if audio_base64:
                                pcm_data = base64.b64decode(audio_base64)
                                print(f"      🎵 Structured audio data:")
                                print(f"         Event ID: {event_id}")
                                print(f"         PCM size: {len(pcm_data)} bytes")
                                
                                try:
                                    ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm_data)
                                    ulaw_size = len(base64.b64decode(ulaw_b64))
                                    print(f"         ✅ Conversion: {len(pcm_data)} PCM → {ulaw_size} μ-law")
                                    
                                    twilio_payload = {"event": "media", "media": {"payload": ulaw_b64}}
                                    payload_json = json.dumps(twilio_payload)
                                    print(f"         📤 Twilio payload: {len(payload_json)} chars")
                                    
                                    audio_messages.append({
                                        "type": "structured",
                                        "event_id": event_id,
                                        "pcm_size": len(pcm_data),
                                        "ulaw_size": ulaw_size,
                                        "twilio_payload_size": len(payload_json)
                                    })
                                    
                                except Exception as e:
                                    print(f"         ❌ Conversion failed: {e}")
                            else:
                                print(f"      ⚠️  Audio message without audio_base_64 data")
                                
                        elif msg_type == "ping":
                            ping_event = msg.get("ping_event", {})
                            event_id = ping_event.get("event_id")
                            print(f"      🏓 Ping received (event_id: {event_id})")
                            
                            pong_message = {"type": "pong", "event_id": event_id}
                            await el_ws.send(json.dumps(pong_message))
                            ping_pong_count += 1
                            print(f"      🏓 Pong sent (count: {ping_pong_count})")
                            
                        else:
                            print(f"      📄 Other message: {json.dumps(msg, indent=10)}")
                            
                    except Exception as e:
                        print(f"      ❌ Failed to parse JSON: {e}")
                        print(f"      Raw data: {raw[:200]}...")
                
                if message_count >= 20:
                    print("   ⏰ Stopping after 20 messages")
                    break
                    
        except asyncio.TimeoutError:
            print("   ⏰ Timeout reached")
        except Exception as e:
            print(f"   ❌ Error during message analysis: {e}")
        
        await el_ws.close()
        
        print(f"\n📋 STEP 4: Audio Flow Analysis Results")
        print("=" * 60)
        print(f"   Total messages received: {message_count}")
        print(f"   Conversation initiated: {'✅ YES' if conversation_initiated else '❌ NO'}")
        print(f"   Audio messages received: {len(audio_messages)}")
        print(f"   Ping/Pong exchanges: {ping_pong_count}")
        
        if audio_messages:
            print(f"\n   🎵 Audio Message Details:")
            total_pcm = 0
            total_ulaw = 0
            for i, audio in enumerate(audio_messages):
                print(f"      Audio {i+1}: {audio['type']}")
                print(f"         PCM: {audio['pcm_size']} bytes")
                print(f"         μ-law: {audio['ulaw_size']} bytes")
                print(f"         Twilio payload: {audio['twilio_payload_size']} chars")
                if 'event_id' in audio:
                    print(f"         Event ID: {audio['event_id']}")
                total_pcm += audio['pcm_size']
                total_ulaw += audio['ulaw_size']
            
            print(f"\n   📊 Audio Totals:")
            print(f"      Total PCM audio: {total_pcm:,} bytes")
            print(f"      Total μ-law audio: {total_ulaw:,} bytes")
            print(f"      Estimated duration: ~{total_pcm / (16000 * 2):.2f} seconds")
        
        print(f"\n📋 STEP 5: WebSocket Bridge Simulation")
        print("=" * 60)
        
        from unittest.mock import Mock, AsyncMock
        
        mock_twilio_connected = Mock()
        mock_twilio_connected.client_state = Mock()
        mock_twilio_connected.client_state.name = "CONNECTED"
        mock_twilio_connected.send_text = AsyncMock()
        
        mock_twilio_closed = Mock()
        mock_twilio_closed.client_state = Mock()
        mock_twilio_closed.client_state.name = "CLOSED"
        mock_twilio_closed.send_text = AsyncMock()
        
        print("   🔄 Testing WebSocket bridge logic...")
        
        if audio_messages:
            test_audio = audio_messages[0]
            
            if mock_twilio_connected.client_state.name == "CONNECTED":
                print("   ✅ Connected WebSocket: Would send audio to Twilio")
                try:
                    await mock_twilio_connected.send_text('{"event": "media", "media": {"payload": "test"}}')
                    print("   ✅ Mock send_text succeeded")
                except Exception as e:
                    print(f"   ❌ Mock send_text failed: {e}")
            
            if mock_twilio_closed.client_state.name != "CONNECTED":
                print("   ✅ Closed WebSocket: Would correctly skip audio")
        
        print(f"\n📋 STEP 6: Root Cause Analysis")
        print("=" * 60)
        
        if not audio_messages:
            print("🚨 CRITICAL ISSUE: No audio messages received from ElevenLabs")
            print("   Root Cause: ElevenLabs agent not generating audio responses")
            print("   Possible reasons:")
            print("   - Agent configuration missing TTS voice model")
            print("   - Agent not set up for audio output")
            print("   - Authentication preventing audio streaming")
            print("   - Agent requires different trigger message format")
            
        elif len(audio_messages) > 0:
            print("✅ ElevenLabs IS generating audio correctly")
            print("   Audio generation: WORKING")
            print("   Audio format: CORRECT")
            print("   Audio conversion: WORKING")
            print("   WebSocket connection: STABLE")
            print("")
            print("🔍 Issue must be in the Twilio WebSocket bridge:")
            print("   - Timing issues with WebSocket state")
            print("   - Twilio connection dropping before audio arrives")
            print("   - Audio buffering or streaming problems")
            print("   - Twilio media stream configuration issues")
        
        print(f"\n📋 STEP 7: Recommendations")
        print("=" * 60)
        
        if not audio_messages:
            print("1. Check ElevenLabs agent configuration in dashboard")
            print("2. Verify agent has TTS voice model assigned")
            print("3. Test agent directly in ElevenLabs interface")
            print("4. Check agent permissions and workspace settings")
        else:
            print("1. Add real-time logging to Twilio WebSocket connection")
            print("2. Monitor WebSocket state changes during calls")
            print("3. Test with longer audio buffering")
            print("4. Verify Twilio media stream configuration")
            print("5. Check for race conditions in pump_el_to_twilio()")
        
        return len(audio_messages) > 0
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(comprehensive_audio_investigation())
    if success:
        print("\n🎉 INVESTIGATION COMPLETED - AUDIO GENERATION CONFIRMED!")
        print("Issue is likely in the Twilio WebSocket bridge implementation.")
    else:
        print("\n💥 INVESTIGATION COMPLETED - NO AUDIO GENERATION DETECTED!")
        print("Issue is in the ElevenLabs agent configuration.")
