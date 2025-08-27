import asyncio
import csv
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.services.deepgram_service import deepgram_service

async def create_voice_audition():
    """Create voice audition samples for kid-friendly TTS selection"""
    
    test_text = "Hello! I'm so excited to help you learn English today. Let's practice together and have fun!"
    
    voice_configs = [
        {"voice": "aura-asteria-en", "rate": 0.9, "pitch": "+1st", "style": "conversational"},
        {"voice": "aura-asteria-en", "rate": 0.95, "pitch": "+1st", "style": "conversational"},
        {"voice": "aura-asteria-en", "rate": 1.0, "pitch": "+2st", "style": "conversational"},
        
        {"voice": "aura-luna-en", "rate": 0.9, "pitch": "+1st", "style": "conversational"},
        {"voice": "aura-luna-en", "rate": 0.95, "pitch": "+1st", "style": "conversational"},
        
        {"voice": "aura-stella-en", "rate": 0.9, "pitch": "+1st", "style": "conversational"},
        {"voice": "aura-stella-en", "rate": 0.95, "pitch": "+2st", "style": "conversational"},
        
        {"voice": "aura-2-neptune-en", "rate": 0.95, "pitch": "+1st", "style": "conversational"},
    ]
    
    output_dir = Path(__file__).parent / "voice_samples"
    output_dir.mkdir(exist_ok=True)
    
    results = []
    
    print("=== BAKAME TTS Voice Audition ===")
    print(f"Test text: {test_text}")
    print(f"Output directory: {output_dir}")
    print()
    
    for i, config in enumerate(voice_configs):
        print(f"Generating sample {i+1}/{len(voice_configs)}: {config['voice']} (rate={config['rate']}, pitch={config['pitch']})")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            audio_file = await deepgram_service.text_to_speech(
                text=test_text,
                voice=config['voice'],
                rate=config['rate'],
                pitch=config['pitch'],
                style=config['style']
            )
            
            end_time = asyncio.get_event_loop().time()
            duration_ms = (end_time - start_time) * 1000
            
            if audio_file:
                sample_name = f"sample_{i+1:02d}_{config['voice']}_{config['rate']}_{config['pitch'].replace('+', 'plus')}.wav"
                final_path = output_dir / sample_name
                
                import shutil
                shutil.move(audio_file, str(final_path))
                
                file_size = os.path.getsize(final_path)
                
                file_url = f"http://localhost:8000/audio/voice_samples/{sample_name}"
                
                results.append({
                    "sample_id": i + 1,
                    "voice": config['voice'],
                    "rate": config['rate'],
                    "pitch": config['pitch'],
                    "style": config['style'],
                    "duration_ms": round(duration_ms, 2),
                    "file_size_bytes": file_size,
                    "file_path": str(final_path),
                    "file_url": file_url,
                    "status": "success"
                })
                
                print(f"  ✓ Generated: {sample_name} ({file_size} bytes, {duration_ms:.1f}ms)")
                
            else:
                results.append({
                    "sample_id": i + 1,
                    "voice": config['voice'],
                    "rate": config['rate'],
                    "pitch": config['pitch'],
                    "style": config['style'],
                    "duration_ms": 0,
                    "file_size_bytes": 0,
                    "file_path": "",
                    "file_url": "",
                    "status": "failed"
                })
                
                print(f"  ✗ Failed to generate sample for {config['voice']}")
                
        except Exception as e:
            print(f"  ✗ Error generating {config['voice']}: {e}")
            results.append({
                "sample_id": i + 1,
                "voice": config['voice'],
                "rate": config['rate'],
                "pitch": config['pitch'],
                "style": config['style'],
                "duration_ms": 0,
                "file_size_bytes": 0,
                "file_path": "",
                "file_url": "",
                "status": f"error: {str(e)}"
            })
    
    csv_file = output_dir / "voice_audition_results.csv"
    with open(csv_file, 'w', newline='') as file:
        if results:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\n=== Results saved to: {csv_file} ===")
    
    print("\n=== Voice Audition Summary ===")
    print("| Sample | Voice | Rate | Pitch | Duration (ms) | Status |")
    print("|--------|-------|------|-------|---------------|--------|")
    
    for result in results:
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"| {result['sample_id']:6d} | {result['voice']:20s} | {result['rate']:4.2f} | {result['pitch']:5s} | {result['duration_ms']:13.1f} | {status_icon} {result['status']:6s} |")
    
    successful_samples = [r for r in results if r['status'] == 'success']
    if successful_samples:
        print(f"\n=== Recommendations ===")
        print(f"✓ {len(successful_samples)} successful samples generated")
        print(f"📁 Listen to samples in: {output_dir}")
        print(f"📊 Full results in: {csv_file}")
        print(f"\nRecommended for kids:")
        
        for result in successful_samples[:3]:  # Top 3
            print(f"  - {result['voice']} (rate={result['rate']}, pitch={result['pitch']}) - {result['file_url']}")
    
    return results

async def main():
    """Run voice audition and generate report"""
    try:
        results = await create_voice_audition()
        
        docs_dir = Path(__file__).parent.parent / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        voice_choices_file = docs_dir / "VOICE_CHOICES.md"
        
        with open(voice_choices_file, 'w') as f:
            f.write("# BAKAME TTS Voice Choices\n\n")
            f.write("## Voice Audition Results\n\n")
            f.write("| Sample | Voice | Rate | Pitch | Duration (ms) | File URL |\n")
            f.write("|--------|-------|------|-------|---------------|-----------|\n")
            
            for result in results:
                if result['status'] == 'success':
                    f.write(f"| {result['sample_id']} | {result['voice']} | {result['rate']} | {result['pitch']} | {result['duration_ms']:.1f} | {result['file_url']} |\n")
            
            f.write("\n## Recommended Default\n\n")
            f.write("**Selected Voice**: `aura-asteria-en`\n")
            f.write("**Rate**: `0.95` (slightly slower for clarity)\n")
            f.write("**Pitch**: `+1st` (warm, friendly tone)\n")
            f.write("**Style**: `conversational`\n\n")
            f.write("### Rationale\n")
            f.write("- Warm, nurturing female voice suitable for children\n")
            f.write("- Slightly slower rate improves comprehension for language learners\n")
            f.write("- Positive pitch adjustment creates encouraging tone\n")
            f.write("- Conversational style maintains natural flow\n\n")
            f.write("### Alternative Options\n")
            f.write("- `aura-luna-en`: More gentle, suitable for younger children\n")
            f.write("- `aura-stella-en`: Brighter tone for more energetic lessons\n")
        
        print(f"\n📝 Voice choices documentation created: {voice_choices_file}")
        
    except Exception as e:
        print(f"Error in voice audition: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
