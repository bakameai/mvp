#!/usr/bin/env python3
"""Enhanced debug script to test ElevenLabs audio response by sending test audio input."""

import asyncio
import json
import time
import sys
import os
import base64
import struct
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.elevenlabs_client import open_el_ws

def generate_test_audio_pcm16k(duration_seconds=2.0, frequency=1000.0):
    """Generate test audio in PCM 16kHz format."""
    sample_rate = 16000
    amplitude = 8000
    samples = []
    
    for i in range(int(sample_rate * duration_seconds)):
        value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
        value = max(-32768, min(32767, value))
        samples.append(struct.pack('<h', value))
    
    return b''.join(samples)

async def debug_elevenlabs_audio_response():
    """Debug ElevenLabs by sending test audio and monitoring for audio responses."""
    print("=== Enhanced ElevenLabs Audio Response Debug ===")
    
    try:
        el_ws = await open_el_ws()
        print("✅ Connected to ElevenLabs WebSocket")
        
        message_count = 0
        audio_message_count = 0
        conversation_initiated = False
        test_audio_sent = False
        
        print("\n🔍 Monitoring ElevenLabs messages and testing audio input...")
        start_time = time.time()
        
        test_pcm16k = generate_test_audio_pcm16k(duration_seconds=1.0, frequency=800.0)
        print(f"📢 Generated {len(test_pcm16k)} bytes of test audio (1s, 800Hz)")
        
        while time.time() - start_time < 30:  # Reduced to 30 seconds for faster testing
            try:
                try:
                    message = await asyncio.wait_for(el_ws.recv(), timeout=0.5)
                    message_count += 1
                    
                    data = json.loads(message)
                    msg_type = data.get("type", "unknown")
                    
                    print(f"\n[MSG {message_count}] Type: {msg_type}")
                    
                    if msg_type == "conversation_initiation_metadata":
                        conversation_initiated = True
                        print("✅ Conversation initiated - EL ready for audio")
                        
                    elif msg_type == "audio":
                        audio_message_count += 1
                        audio_event = data.get("audio_event", {})
                        audio_base64 = audio_event.get("audio_base_64", "")
                        event_id = audio_event.get("event_id", "unknown")
                        
                        print(f"🎵 AUDIO RESPONSE #{audio_message_count}")
                        print(f"   Event ID: {event_id}")
                        print(f"   Audio data length: {len(audio_base64)} chars")
                        print(f"   Has audio data: {'YES' if audio_base64 else 'NO'}")
                        
                        if audio_base64:
                            print(f"   ✅ ElevenLabs IS responding with audio!")
                        else:
                            print(f"   ❌ Empty audio response")
                            
                    elif msg_type == "ping":
                        ping_event = data.get("ping_event", {})
                        event_id = ping_event.get("event_id")
                        pong_message = {"type": "pong", "event_id": event_id}
                        await el_ws.send(json.dumps(pong_message))
                        print(f"🏓 Ping/Pong: {event_id}")
                        
                    else:
                        print(f"📝 Other message type: {msg_type}")
                        
                except asyncio.TimeoutError:
                    pass
                
                if conversation_initiated and not test_audio_sent and time.time() - start_time > 2:
                    print(f"\n📤 Sending test audio to ElevenLabs...")
                    
                    audio_b64 = base64.b64encode(test_pcm16k).decode('utf-8')
                    el_message = {
                        "user_audio_chunk": audio_b64
                    }
                    
                    await el_ws.send(json.dumps(el_message))
                    test_audio_sent = True
                    print(f"✅ Sent {len(test_pcm16k)} bytes of test audio to ElevenLabs")
                    print("🔍 Waiting for audio response...")
                    
            except Exception as e:
                print(f"❌ Error during message processing: {e}")
                break
                
        print(f"\n=== Enhanced Debug Summary ===")
        print(f"Total messages received: {message_count}")
        print(f"Audio responses received: {audio_message_count}")
        print(f"Conversation initiated: {'YES' if conversation_initiated else 'NO'}")
        print(f"Test audio sent: {'YES' if test_audio_sent else 'NO'}")
        
        if not conversation_initiated:
            print("\n❌ ISSUE: Conversation never initiated")
        elif not test_audio_sent:
            print("\n❌ ISSUE: Could not send test audio")
        elif audio_message_count == 0:
            print("\n❌ ISSUE CONFIRMED: ElevenLabs receives audio but doesn't respond")
            print("   Possible causes:")
            print("   - Agent not configured to respond to audio input")
            print("   - Audio format incompatible with agent")
            print("   - Agent requires specific conversation triggers")
            print("   - Agent configuration issue in ElevenLabs dashboard")
        else:
            print(f"\n✅ SUCCESS: ElevenLabs responded with {audio_message_count} audio messages")
            print("   The audio frame counting should work during real conversations")
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            await el_ws.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(debug_elevenlabs_audio_response())
