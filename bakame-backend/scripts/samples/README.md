# Audio Test Samples

This directory contains test audio samples for the IVR latency harness.

## Current Samples

- `happy.wav` - Clear, enthusiastic English speech
- `noisy.wav` - Speech with background noise and hesitations
- `accent.wav` - Speech with Kinyarwanda accent

## Replacing Samples

To replace these samples with real audio files:

1. Record or obtain WAV files under 10 seconds each
2. Replace the existing files with the same names
3. Ensure files are in WAV format, 16kHz sample rate preferred
4. Test with `poetry run python scripts/sim_call.py`

## Usage

The latency harness will automatically use these samples when running simulation tests.
