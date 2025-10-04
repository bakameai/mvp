# WebSocket Bridge Fix Implementation Plan

## Root Cause Summary
Investigation confirms ElevenLabs generates audio correctly (108,452 bytes, ~3.39 seconds) but the `pump_el_to_twilio()` function fails to deliver audio to callers due to WebSocket state management and timing issues.

## Identified Issues in Current Implementation

### 1. Aggressive WebSocket State Checking
```python
# CURRENT ISSUE (lines 195-197 in main.py):
if ws.client_state.name != "CONNECTED":
    print(f"[EL->Twilio] Twilio WebSocket not connected (state: {ws.client_state.name}), skipping audio", flush=True)
    return  # ❌ EXITS ENTIRE FUNCTION PERMANENTLY
```

**Problem**: If Twilio WebSocket is temporarily not "CONNECTED" when audio arrives, the entire pump function exits and never recovers, causing all subsequent audio to be lost.

### 2. Premature Function Exit on Errors
```python
# CURRENT ISSUE (lines 206-208 in main.py):
if "close message has been sent" in str(e) or "not connected" in str(e).lower():
    print("[EL->Twilio] Twilio WebSocket closed, stopping audio pump", flush=True)
    return  # ❌ PERMANENT EXIT ON RECOVERABLE ERRORS
```

**Problem**: Function exits permanently on potentially recoverable connection errors.

### 3. No Audio Buffering or Retry Logic
**Problem**: Audio chunks are processed immediately without buffering, causing timing issues when WebSocket isn't ready.

## Proposed Implementation Plan

### Phase 1: Add Real-Time Monitoring (Deploy First)
```python
# Add detailed logging to understand WebSocket state during real calls
import time

async def pump_el_to_twilio():
    try:
        async for raw in el_ws:
            if isinstance(raw, str):
                msg = json.loads(raw)
                if msg.get("type") == "audio":
                    # Log WebSocket state when audio arrives
                    current_time = time.time()
                    ws_state = ws.client_state.name
                    print(f"[TIMING] Audio arrived at {current_time}, Twilio state: {ws_state}", flush=True)
                    
                    # Continue with existing logic but don't exit on state issues
```

### Phase 2: Implement Audio Buffering
```python
import asyncio
from collections import deque

# Add audio buffer at function level
audio_buffer = deque()
buffer_task = None

async def pump_el_to_twilio():
    async def process_audio_buffer():
        """Process buffered audio when WebSocket is ready"""
        while True:
            if audio_buffer and ws.client_state.name == "CONNECTED":
                try:
                    audio_data = audio_buffer.popleft()
                    await ws.send_text(json.dumps(audio_data))
                    print(f"[BUFFER] Sent buffered audio ({len(audio_data)} chars)", flush=True)
                except Exception as e:
                    print(f"[BUFFER] Error sending buffered audio: {e}", flush=True)
                    # Re-queue audio for retry
                    audio_buffer.appendleft(audio_data)
            await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
    
    # Start buffer processing task
    buffer_task = asyncio.create_task(process_audio_buffer())
    
    try:
        async for raw in el_ws:
            # ... existing message parsing ...
            
            if msg_type == "audio":
                audio_event = msg.get("audio_event", {})
                audio_base64 = audio_event.get("audio_base_64", "")
                if audio_base64:
                    pcm16k = base64.b64decode(audio_base64)
                    ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                    out = {"event": "media", "media": {"payload": ulaw_b64}}
                    
                    if ws.client_state.name == "CONNECTED":
                        # Send immediately if connected
                        try:
                            await ws.send_text(json.dumps(out))
                            print(f"[DIRECT] Sent audio immediately", flush=True)
                        except Exception as e:
                            print(f"[DIRECT] Failed, buffering: {e}", flush=True)
                            audio_buffer.append(out)
                    else:
                        # Buffer for later if not connected
                        audio_buffer.append(out)
                        print(f"[BUFFER] Buffered audio (state: {ws.client_state.name})", flush=True)
```

### Phase 3: Add Retry Logic with Exponential Backoff
```python
async def send_audio_with_retry(ws, audio_data, max_retries=3):
    """Send audio with retry logic"""
    for attempt in range(max_retries):
        try:
            if ws.client_state.name == "CONNECTED":
                await ws.send_text(json.dumps(audio_data))
                return True
            else:
                print(f"[RETRY] WebSocket not connected (attempt {attempt + 1})", flush=True)
        except Exception as e:
            print(f"[RETRY] Attempt {attempt + 1} failed: {e}", flush=True)
        
        if attempt < max_retries - 1:
            delay = 0.1 * (2 ** attempt)  # Exponential backoff
            await asyncio.sleep(delay)
    
    return False
```

### Phase 4: Graceful Error Handling
```python
# Replace aggressive exits with graceful handling
try:
    # Audio processing logic
    success = await send_audio_with_retry(ws, out)
    if not success:
        print("[GRACEFUL] Audio delivery failed after retries, continuing...", flush=True)
        # Continue processing instead of exiting
except Exception as e:
    print(f"[GRACEFUL] Error processing audio: {e}", flush=True)
    # Log error but continue processing
    continue  # Don't exit entire function
```

## Implementation Sequence

### Step 1: Deploy Monitoring (Immediate)
- Add real-time WebSocket state logging
- Deploy to production to gather data from real calls
- Monitor logs during test calls to understand timing

### Step 2: Implement Buffering (After monitoring data)
- Add audio buffering system
- Test locally with simulated WebSocket state changes
- Deploy and test with real calls

### Step 3: Add Retry Logic (Final)
- Implement retry mechanism with exponential backoff
- Add graceful error handling
- Final testing and deployment

## Testing Strategy

### Local Testing
```python
# Create test script to simulate WebSocket state changes
async def test_websocket_states():
    # Simulate CONNECTING -> CONNECTED -> CLOSED states
    # Verify audio buffering and retry logic
```

### Production Testing
1. Deploy monitoring first
2. Make test calls and analyze logs
3. Verify WebSocket state transitions during calls
4. Confirm audio delivery timing

## Success Criteria
- [ ] Audio reaches callers consistently during phone calls
- [ ] WebSocket state changes don't cause audio loss
- [ ] Buffering handles timing issues gracefully
- [ ] Retry logic recovers from temporary connection issues
- [ ] No more "send after close" errors in logs
- [ ] Real-time monitoring shows successful audio delivery

## Risk Mitigation
- Deploy changes incrementally (monitoring → buffering → retry)
- Keep existing error logging for debugging
- Add rollback plan if issues occur
- Test thoroughly with actual phone calls before final deployment

## Files to Modify
- `app/main.py` - Update `pump_el_to_twilio()` function
- Add comprehensive logging and monitoring
- Implement audio buffering system
- Add retry logic with graceful error handling

This plan addresses the root cause identified in the investigation: WebSocket bridge timing and state management issues preventing audio delivery to callers.
</script>
