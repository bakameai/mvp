#!/usr/bin/env python3
"""Debug script to compare audio conversion pipeline between test audio and Twilio audio."""

import asyncio
import json
import time
import sys
import os
import base64
import struct
import math
import audioop

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.elevenlabs_client import open_el_ws
from app.main import twilio_ulaw8k_to_pcm16_16k, enhance_voice_audio

def generate_test_audio_pcm16k(duration_seconds=1.0, frequency=800.0):
    """Generate clean test audio in PCM 16kHz format (same as debug script)."""
    sample_rate = 16000
    amplitude = 8000
    samples = []
    
    for i in range(int(sample_rate * duration_seconds)):
        value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
        value = max(-32768, min(32767, value))
        samples.append(struct.pack('<h', value))
    
    return b''.join(samples)

def generate_simulated_twilio_audio(duration_seconds=1.0, frequency=800.0):
    """Generate audio that simulates Twilio's μ-law 8kHz -> PCM 16kHz conversion."""
    sample_rate_16k = 16000
    amplitude = 8000
    samples_16k = []
    
    for i in range(int(sample_rate_16k * duration_seconds)):
        value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate_16k))
        value = max(-32768, min(32767, value))
        samples_16k.append(struct.pack('<h', value))
    
    pcm16k_clean = b''.join(samples_16k)
    
    pcm8k, _ = audioop.ratecv(pcm16k_clean, 2, 1, 16000, 8000, None)
    
    ulaw = audioop.lin2ulaw(pcm8k, 2)
    
    pcm8k_restored = audioop.ulaw2lin(ulaw, 2)
    
    pcm16k_restored, _ = audioop.ratecv(pcm8k_restored, 2, 1, 8000, 16000, None)
    
    return pcm16k_clean, pcm16k_restored

async def test_audio_formats_with_elevenlabs():
    """Test different audio formats with ElevenLabs to identify why real phone audio doesn't trigger responses."""
    print("=== Audio Conversion Pipeline Debug ===")
    
    try:
        el_ws = await open_el_ws()
        print("✅ Connected to ElevenLabs WebSocket")
        
        print("\n🔍 Waiting for conversation initiation...")
        conversation_initiated = False
        start_time = time.time()
        
        while time.time() - start_time < 10 and not conversation_initiated:
            try:
                message = await asyncio.wait_for(el_ws.recv(), timeout=2.0)
                data = json.loads(message)
                if data.get("type") == "conversation_initiation_metadata":
                    conversation_initiated = True
                    print("✅ Conversation initiated")
                    break
            except asyncio.TimeoutError:
                continue
        
        if not conversation_initiated:
            print("❌ Failed to initiate conversation")
            return
        
        print("\n📢 Test 1: Clean PCM 16kHz audio (baseline)")
        clean_audio = generate_test_audio_pcm16k(duration_seconds=0.5, frequency=800.0)
        audio_b64 = base64.b64encode(clean_audio).decode('utf-8')
        
        el_message = {"user_audio_chunk": audio_b64}
        await el_ws.send(json.dumps(el_message))
        print(f"✅ Sent {len(clean_audio)} bytes of clean audio")
        
        audio_responses = 0
        for _ in range(10):  # Wait up to 5 seconds
            try:
                message = await asyncio.wait_for(el_ws.recv(), timeout=0.5)
                data = json.loads(message)
                if data.get("type") == "audio":
                    audio_responses += 1
                    print(f"🎵 Clean audio triggered response #{audio_responses}")
            except asyncio.TimeoutError:
                break
        
        print(f"Clean audio responses: {audio_responses}")
        
        print("\n📢 Test 2: Simulated Twilio μ-law conversion")
        clean_audio, twilio_audio = generate_simulated_twilio_audio(duration_seconds=0.5, frequency=800.0)
        
        print(f"Original audio: {len(clean_audio)} bytes")
        print(f"After Twilio conversion: {len(twilio_audio)} bytes")
        
        enhanced_audio = enhance_voice_audio(twilio_audio)
        print(f"After voice enhancement: {len(enhanced_audio)} bytes")
        
        audio_b64 = base64.b64encode(enhanced_audio).decode('utf-8')
        el_message = {"user_audio_chunk": audio_b64}
        await el_ws.send(json.dumps(el_message))
        print(f"✅ Sent simulated Twilio audio")
        
        twilio_responses = 0
        for _ in range(10):  # Wait up to 5 seconds
            try:
                message = await asyncio.wait_for(el_ws.recv(), timeout=0.5)
                data = json.loads(message)
                if data.get("type") == "audio":
                    twilio_responses += 1
                    print(f"🎵 Twilio audio triggered response #{twilio_responses}")
            except asyncio.TimeoutError:
                break
        
        print(f"Twilio audio responses: {twilio_responses}")
        
        print("\n📢 Test 3: Short audio chunks (20ms like real calls)")
        short_audio = generate_test_audio_pcm16k(duration_seconds=0.02, frequency=800.0)  # 20ms
        
        short_responses = 0
        for i in range(5):
            audio_b64 = base64.b64encode(short_audio).decode('utf-8')
            el_message = {"user_audio_chunk": audio_b64}
            await el_ws.send(json.dumps(el_message))
            await asyncio.sleep(0.02)  # 20ms intervals
        
        print(f"✅ Sent 5 short audio chunks ({len(short_audio)} bytes each)")
        
        for _ in range(15):  # Wait up to 7.5 seconds
            try:
                message = await asyncio.wait_for(el_ws.recv(), timeout=0.5)
                data = json.loads(message)
                if data.get("type") == "audio":
                    short_responses += 1
                    print(f"🎵 Short chunks triggered response #{short_responses}")
            except asyncio.TimeoutError:
                break
        
        print(f"Short chunks responses: {short_responses}")
        
        print(f"\n=== Audio Format Analysis ===")
        print(f"Clean audio responses: {audio_responses}")
        print(f"Twilio-simulated responses: {twilio_responses}")
        print(f"Short chunks responses: {short_responses}")
        
        if audio_responses > 0 and twilio_responses == 0:
            print("\n❌ ISSUE IDENTIFIED: Twilio audio conversion pipeline breaks ElevenLabs compatibility")
            print("   Possible causes:")
            print("   - μ-law compression artifacts")
            print("   - Sample rate conversion quality loss")
            print("   - Audio enhancement pipeline issues")
        elif audio_responses > 0 and short_responses == 0:
            print("\n❌ ISSUE IDENTIFIED: Short audio chunks don't trigger ElevenLabs responses")
            print("   Possible causes:")
            print("   - ElevenLabs requires minimum audio duration")
            print("   - Need to accumulate chunks before sending")
        elif all(r > 0 for r in [audio_responses, twilio_responses, short_responses]):
            print("\n✅ All audio formats work - issue might be in real-time timing or connection state")
        else:
            print("\n❓ Mixed results - need further investigation")
            
    except Exception as e:
        print(f"❌ Error during audio format testing: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            await el_ws.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_audio_formats_with_elevenlabs())
