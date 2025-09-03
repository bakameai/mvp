#!/usr/bin/env python3
"""
Audio format verification script for Twilio compatibility.
Checks that audio files are mono, 8000 Hz, pcm_mulaw format.
NOTE: This script is deprecated as BAKAME has transitioned to ElevenLabs conversational AI.
"""

import subprocess
import sys
import os
import asyncio

async def generate_test_audio():
    """Generate a test audio file - deprecated after ElevenLabs transition"""
    print("This script is deprecated after transitioning to ElevenLabs conversational AI.")
    print("ElevenLabs handles audio format compatibility automatically.")
    return None

def check_audio_format(file_path):
    """Check audio format using ffprobe"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ ffprobe failed: {result.stderr}")
            return False
        
        import json
        data = json.loads(result.stdout)
        
        audio_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break
        
        if not audio_stream:
            print("❌ No audio stream found")
            return False
        
        sample_rate = int(audio_stream.get('sample_rate', 0))
        channels = int(audio_stream.get('channels', 0))
        codec_name = audio_stream.get('codec_name', '')
        
        print(f"📊 Audio Format Analysis:")
        print(f"   Sample Rate: {sample_rate} Hz")
        print(f"   Channels: {channels}")
        print(f"   Codec: {codec_name}")
        print(f"   Duration: {audio_stream.get('duration', 'unknown')} seconds")
        
        checks_passed = 0
        total_checks = 3
        
        if sample_rate == 8000:
            print("✅ Sample rate: 8000 Hz (correct)")
            checks_passed += 1
        else:
            print(f"❌ Sample rate: {sample_rate} Hz (should be 8000)")
        
        if channels == 1:
            print("✅ Channels: mono (correct)")
            checks_passed += 1
        else:
            print(f"❌ Channels: {channels} (should be 1 for mono)")
        
        if codec_name == 'pcm_mulaw':
            print("✅ Codec: pcm_mulaw (correct)")
            checks_passed += 1
        else:
            print(f"❌ Codec: {codec_name} (should be pcm_mulaw)")
        
        print(f"\n📈 Compatibility Score: {checks_passed}/{total_checks}")
        
        if checks_passed == total_checks:
            print("🎉 Audio file is fully Twilio-compatible!")
            return True
        else:
            print("⚠️  Audio file may not work properly with Twilio")
            return False
            
    except Exception as e:
        print(f"❌ Error checking audio format: {e}")
        return False

async def main():
    """Main verification function"""
    print("=== Twilio Audio Format Verification ===\n")
    
    test_file = await generate_test_audio()
    if not test_file:
        print("❌ Failed to generate test audio file")
        sys.exit(1)
    
    print(f"📁 Test file: {test_file}\n")
    
    is_compatible = check_audio_format(test_file)
    
    try:
        os.unlink(test_file)
        print(f"\n🧹 Cleaned up test file: {test_file}")
    except:
        pass
    
    if is_compatible:
        print("\n✅ PASS: Audio format is Twilio-compatible")
        sys.exit(0)
    else:
        print("\n❌ FAIL: Audio format is NOT Twilio-compatible")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
