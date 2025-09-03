import asyncio
import time
import json
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.services.llama_service import llama_service
from app.services.openai_service import openai_service
from app.services.elevenlabs_service import elevenlabs_service

async def create_test_audio_samples():
    """Create test audio samples if they don't exist"""
    samples_dir = Path(__file__).parent / "samples"
    samples_dir.mkdir(exist_ok=True)
    
    samples = {
        "happy.wav": "Hello, I'm excited to learn English with BAKAME today!",
        "noisy.wav": "Um... hello... can you... hear me... with this... background noise?",
        "accent.wav": "Muraho! I am speaking with my Kinyarwanda accent, can you understand me?"
    }
    
    for filename, content in samples.items():
        sample_path = samples_dir / filename
        if not sample_path.exists():
            sample_path.write_text(content)
    
    return samples_dir

async def simulate_asr(text_content: str) -> tuple[str, float]:
    """Simulate ASR processing and measure latency"""
    start_time = time.time()
    
    await asyncio.sleep(0.1)  # Simulate ASR processing time
    
    latency_ms = (time.time() - start_time) * 1000
    return text_content, latency_ms

async def simulate_llm(text: str, scenario: str) -> tuple[str, float]:
    """Simulate LLM processing and measure latency"""
    start_time = time.time()
    
    messages = [{"role": "user", "content": text}]
    response = await llama_service.generate_response(messages, "english")
    
    latency_ms = (time.time() - start_time) * 1000
    return response, latency_ms

async def simulate_tts(text: str) -> tuple[str, float]:
    """Simulate TTS processing and measure latency"""
    start_time = time.time()
    
    await asyncio.sleep(0.2)  # Simulate TTS processing time
    
    latency_ms = (time.time() - start_time) * 1000
    return "audio_generated", latency_ms

async def run_scenario(scenario_name: str, text_content: str) -> dict:
    """Run a complete ASR→LLM→TTS scenario and measure timings"""
    print(f"Running scenario: {scenario_name}")
    
    asr_result, asr_ms = await simulate_asr(text_content)
    
    llm_result, llm_ms = await simulate_llm(asr_result, scenario_name)
    
    tts_result, tts_ms = await simulate_tts(llm_result)
    
    total_ms = asr_ms + llm_ms + tts_ms
    
    return {
        "scenario": scenario_name,
        "asr_ms": round(asr_ms, 2),
        "llm_ms": round(llm_ms, 2),
        "tts_ms": round(tts_ms, 2),
        "total_ms": round(total_ms, 2),
        "asr_result": asr_result[:50] + "..." if len(asr_result) > 50 else asr_result,
        "llm_result": llm_result[:50] + "..." if len(llm_result) > 50 else llm_result
    }

async def main():
    """Run all test scenarios and output JSON results"""
    print("=== BAKAME IVR Latency Test ===")
    
    samples_dir = await create_test_audio_samples()
    
    scenarios = [
        ("happy_path", "Hello, I'm excited to learn English with BAKAME today!"),
        ("silence_noise", "Um... hello... can you... hear me... with this... background noise?"),
        ("heavy_accent", "Muraho! I am speaking with my Kinyarwanda accent, can you understand me?")
    ]
    
    results = []
    
    for scenario_name, text_content in scenarios:
        try:
            result = await run_scenario(scenario_name, text_content)
            results.append(result)
        except Exception as e:
            print(f"Error in scenario {scenario_name}: {e}")
            results.append({
                "scenario": scenario_name,
                "error": str(e),
                "asr_ms": 0,
                "llm_ms": 0,
                "tts_ms": 0,
                "total_ms": 0
            })
    
    print("\n=== JSON RESULTS ===")
    print(json.dumps(results, indent=2))
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
