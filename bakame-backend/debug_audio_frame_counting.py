#!/usr/bin/env python3
"""Debug script to investigate why audio_frames_count isn't incrementing during active speech."""

import asyncio
import json
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.elevenlabs_client import open_el_ws

async def debug_elevenlabs_audio_flow():
    """Debug ElevenLabs audio message flow to understand why audio frames aren't counted."""
    print("=== Debugging ElevenLabs Audio Frame Counting ===")
    
    try:
        el_ws = await open_el_ws()
        print("✅ Connected to ElevenLabs WebSocket")
        
        message_count = 0
        audio_message_count = 0
        conversation_initiated = False
        
        print("\n🔍 Monitoring ElevenLabs messages for 60 seconds...")
        start_time = time.time()
        
        while time.time() - start_time < 60:
            try:
                message = await asyncio.wait_for(el_ws.recv(), timeout=2.0)
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
                    
                    print(f"🎵 AUDIO MESSAGE #{audio_message_count}")
                    print(f"   Event ID: {event_id}")
                    print(f"   Audio data length: {len(audio_base64)} chars")
                    print(f"   Has audio data: {'YES' if audio_base64 else 'NO'}")
                    
                    if audio_base64:
                        print(f"   ✅ This would increment audio_frames_count")
                    else:
                        print(f"   ❌ No audio data - audio_frames_count NOT incremented")
                        
                elif msg_type == "ping":
                    ping_event = data.get("ping_event", {})
                    event_id = ping_event.get("event_id")
                    pong_message = {"type": "pong", "event_id": event_id}
                    await el_ws.send(json.dumps(pong_message))
                    print(f"🏓 Ping/Pong: {event_id}")
                    
                else:
                    print(f"📝 Other message type: {msg_type}")
                    
            except asyncio.TimeoutError:
                continue
                
        print(f"\n=== Debug Summary ===")
        print(f"Total messages received: {message_count}")
        print(f"Audio messages received: {audio_message_count}")
        print(f"Conversation initiated: {'YES' if conversation_initiated else 'NO'}")
        
        if audio_message_count == 0:
            print("\n❌ ISSUE IDENTIFIED: No audio messages received from ElevenLabs")
            print("   This explains why audio_frames_count stays at 0")
        else:
            print(f"\n✅ ElevenLabs is sending audio messages")
            
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
    asyncio.run(debug_elevenlabs_audio_flow())
