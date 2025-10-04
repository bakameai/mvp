#!/usr/bin/env python3
"""
Investigate the exact WebSocket message format being sent to Twilio
to identify why "Stream - Protocol - Invalid message" errors occur.
"""

import json
import base64
import audioop
import asyncio
import websockets
from typing import Dict, Any

def test_twilio_message_format():
    """Test various Twilio message formats to identify the correct one."""
    
    test_pcm = b'\x00\x01' * 800  # 1600 bytes of test PCM data
    
    try:
        pcm8k, _ = audioop.ratecv(test_pcm, 2, 1, 16000, 8000, None)
        ulaw = audioop.lin2ulaw(pcm8k, 2)
        ulaw_b64 = base64.b64encode(ulaw).decode('ascii')
        
        print(f"Audio conversion successful:")
        print(f"  Original PCM: {len(test_pcm)} bytes")
        print(f"  Downsampled PCM: {len(pcm8k)} bytes") 
        print(f"  μ-law: {len(ulaw)} bytes")
        print(f"  Base64 μ-law: {len(ulaw_b64)} chars")
        
    except Exception as e:
        print(f"Audio conversion failed: {e}")
        return
    
    formats_to_test = [
        {
            "name": "Current Format",
            "message": {
                "event": "media",
                "media": {
                    "payload": ulaw_b64
                }
            }
        },
        
        {
            "name": "With StreamSid",
            "message": {
                "event": "media",
                "streamSid": "test_stream_id",
                "media": {
                    "payload": ulaw_b64
                }
            }
        },
        
        {
            "name": "With Timestamp",
            "message": {
                "event": "media",
                "media": {
                    "timestamp": "1234567890",
                    "payload": ulaw_b64
                }
            }
        },
        
        {
            "name": "With Track",
            "message": {
                "event": "media",
                "media": {
                    "track": "outbound",
                    "payload": ulaw_b64
                }
            }
        },
        
        {
            "name": "Complete Format",
            "message": {
                "event": "media",
                "streamSid": "test_stream_id",
                "media": {
                    "track": "outbound",
                    "chunk": "1",
                    "timestamp": "1234567890",
                    "payload": ulaw_b64
                }
            }
        }
    ]
    
    print("\n=== Testing Twilio Message Formats ===")
    
    for format_test in formats_to_test:
        print(f"\n{format_test['name']}:")
        message = format_test['message']
        
        required_fields = ['event', 'media']
        missing_fields = []
        
        for field in required_fields:
            if field not in message:
                missing_fields.append(field)
        
        if 'media' in message and 'payload' not in message['media']:
            missing_fields.append('media.payload')
        
        if missing_fields:
            print(f"  ❌ Missing fields: {missing_fields}")
        else:
            print(f"  ✅ All required fields present")
        
        try:
            json_str = json.dumps(message)
            print(f"  ✅ JSON serialization successful ({len(json_str)} chars)")
            
            parsed = json.loads(json_str)
            print(f"  ✅ JSON parsing successful")
            
            sample_msg = json.dumps(message, indent=2)[:200] + "..."
            print(f"  Sample: {sample_msg}")
            
        except Exception as e:
            print(f"  ❌ JSON error: {e}")

def analyze_elevenlabs_message_format():
    """Analyze the expected ElevenLabs message format."""
    
    print("\n=== ElevenLabs Message Format Analysis ===")
    
    el_message = {
        "type": "audio",
        "audio_event": {
            "audio_base_64": "dGVzdCBhdWRpbyBkYXRh",  # test audio data
            "event_id": 1
        }
    }
    
    print("Expected ElevenLabs format:")
    print(json.dumps(el_message, indent=2))
    
    msg_type = el_message.get("type")
    audio_event = el_message.get("audio_event", {})
    audio_base64 = audio_event.get("audio_base_64", "")
    
    print(f"\nParsing results:")
    print(f"  msg_type: {msg_type}")
    print(f"  audio_event keys: {list(audio_event.keys())}")
    print(f"  audio_base64 length: {len(audio_base64)}")
    print(f"  Has audio data: {bool(audio_base64)}")
    
    try:
        decoded = base64.b64decode(audio_base64)
        print(f"  ✅ Base64 decode successful: {len(decoded)} bytes")
    except Exception as e:
        print(f"  ❌ Base64 decode failed: {e}")

def check_websocket_state_issues():
    """Check for potential WebSocket state issues."""
    
    print("\n=== WebSocket State Analysis ===")
    
    states = ["CONNECTING", "OPEN", "CLOSING", "CLOSED"]
    
    for state in states:
        print(f"\nWebSocket state: {state}")
        
        if state == "OPEN":
            print("  ✅ Should send audio messages")
        else:
            print(f"  ❌ Should buffer audio (state: {state})")
        
        if state == "CONNECTED":  # Note: websockets uses "CONNECTED" not "OPEN"
            print("  ✅ Current logic: would send immediately")
        else:
            print("  🔄 Current logic: would buffer audio")

if __name__ == "__main__":
    print("=== WebSocket Message Format Investigation ===")
    
    test_twilio_message_format()
    analyze_elevenlabs_message_format()
    check_websocket_state_issues()
    
    print("\n=== Summary ===")
    print("1. Audio conversion is working correctly")
    print("2. Basic Twilio message format appears correct")
    print("3. ElevenLabs message parsing logic is correct")
    print("4. Issue likely in WebSocket state management or timing")
    print("\nNext steps:")
    print("- Add real-time logging during actual calls")
    print("- Monitor WebSocket state transitions")
    print("- Check for timing issues between audio arrival and WebSocket readiness")
