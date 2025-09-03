import subprocess
import tempfile
import os
import asyncio
from typing import Optional

async def convert_to_telephony(input_file: str) -> Optional[str]:
    """Convert audio to 8kHz mono μ-law for Twilio telephony"""
    try:
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='_telephony.wav')
        output_file.close()
        
        cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            '-i', input_file,  # Input file
            '-ar', '8000',  # Sample rate: 8kHz
            '-ac', '1',  # Channels: mono
            '-acodec', 'pcm_mulaw',  # Codec: μ-law
            '-f', 'wav',  # Format: WAV container
            '-loglevel', 'error',  # Suppress verbose output
            output_file.name
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print(f"Successfully converted audio to telephony format: {output_file.name}")
            return output_file.name
        else:
            print(f"FFmpeg conversion failed: {stderr.decode()}")
            if os.path.exists(output_file.name):
                os.unlink(output_file.name)
            return None
            
    except FileNotFoundError:
        print("FFmpeg not found. Please install ffmpeg for audio conversion.")
        return None
    except Exception as e:
        print(f"Error in audio conversion: {e}")
        return None

def validate_telephony_audio(file_path: str) -> bool:
    """Validate that audio file meets telephony requirements"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            
            if 'streams' in data and len(data['streams']) > 0:
                stream = data['streams'][0]
                
                sample_rate = int(stream.get('sample_rate', 0))
                channels = int(stream.get('channels', 0))
                codec = stream.get('codec_name', '')
                
                is_valid = (
                    sample_rate == 8000 and
                    channels == 1 and
                    codec == 'pcm_mulaw'
                )
                
                print(f"Audio validation - Rate: {sample_rate}Hz, Channels: {channels}, Codec: {codec}, Valid: {is_valid}")
                return is_valid
        
        return False
        
    except Exception as e:
        print(f"Error validating audio: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python audio_transcode.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    async def main():
        result = await convert_to_telephony(input_file)
        if result:
            import shutil
            shutil.move(result, output_file)
            print(f"Converted audio saved to: {output_file}")
            
            if validate_telephony_audio(output_file):
                print("✓ Audio meets telephony requirements")
            else:
                print("⚠ Audio may not meet telephony requirements")
        else:
            print("Conversion failed")
            sys.exit(1)
    
    asyncio.run(main())
