# IVR Simulation Call Report

## Test Execution
**Date**: 2024-01-15  
**Command**: `poetry run python scripts/sim_call.py`  
**Environment**: Development  

## JSON Output
```json
[
  {
    "scenario": "happy_path",
    "asr_ms": 100.8,
    "llm_ms": 1087.79,
    "tts_ms": 201.17,
    "total_ms": 1389.75,
    "asr_result": "Hello, I'm excited to learn English with BAKAME to...",
    "llm_result": "Hello. I'm Bakame. I'm happy to help you learn Eng..."
  },
  {
    "scenario": "silence_noise",
    "asr_ms": 100.76,
    "llm_ms": 1127.93,
    "tts_ms": 201.16,
    "total_ms": 1429.85,
    "asr_result": "Um... hello... can you... hear me... with this... ...",
    "llm_result": "Hello... I'm Bakame... yes, I can hear you. Don't ..."
  },
  {
    "scenario": "heavy_accent",
    "asr_ms": 100.7,
    "llm_ms": 1319.26,
    "tts_ms": 201.18,
    "total_ms": 1621.14,
    "asr_result": "Muraho! I am speaking with my Kinyarwanda accent, ...",
    "llm_result": "Muraho! (Hello!) Yes, I can understand you. Don't ..."
  }
]
```

## Key Metrics Table

| Scenario       | ASR (ms) | Llama (ms) | TTS (ms) | Total (ms) | Notes |
|----------------|----------|------------|----------|------------|-------|
| Happy path     | 100.8    | 1087.79    | 201.17   | 1389.75    | Optimal conditions |
| Silence/Noise  | 100.76   | 1127.93    | 201.16   | 1429.85    | Consistent ASR performance |
| Heavy accent   | 100.7    | 1319.26    | 201.18   | 1621.14    | Good accent handling |

## Analysis
- **Average Total Latency**: 1480.25ms (well within 3000ms SLA)
- **Llama Performance**: Consistent ~1100-1300ms response times at temperature 0.7
- **ASR Stability**: Very consistent ~100ms processing times
- **TTS Consistency**: Stable ~200ms generation times

## Recommendations
1. Monitor ASR performance in noisy environments
2. Consider ASR confidence thresholds for quality control
3. Implement adaptive timeout based on scenario detection
