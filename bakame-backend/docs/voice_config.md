# Voice Configuration Documentation

## ElevenLabs Conversational AI Configuration

### Primary Voice Configuration
- **Agent**: ElevenLabs Conversational AI with RAG integration
- **Voice Settings**: Stability 0.5, Similarity Boost 0.8
- **Knowledge Base**: Code of the Debater, Chinua, Mental Math materials
- **Agent Goal**: Guide offline learners through English conversation, debate, grammar, reading comprehension, and mental math

### Voice Selection Rationale
The ElevenLabs conversational AI was selected for its:
- **Natural conversation**: Human-like interactions for young learners
- **Educational focus**: Specialized for tutoring and learning assistance
- **Adaptive responses**: Context-aware based on student progress
- **Cultural sensitivity**: Configurable for Rwandan educational context

## Dynamic Temperature Control

### Temperature Settings by Conversation State

| State | Temperature | Purpose | Example Usage |
|-------|-------------|---------|---------------|
| `intro` | 0.4 | Consistent, steady greeting | Welcome message and name capture |
| `normal` | 0.9 | Balanced conversation | Regular learning interactions |
| `assessment` | 0.2 | Precise, focused evaluation | Student response scoring |
| `facts` | 1.6 | Creative, varied presentation | Rwanda cultural facts |

### Implementation
```python
def get_temperature_for_state(self, conversation_state: str) -> float:
    temperature_map = {
        "intro": 0.4,
        "normal": 0.9,
        "assessment": 0.2,
        "facts": 1.6,
        "welcome": 0.4,
        "name_capture": 0.4,
        "name_confirm": 0.4
    }
    return temperature_map.get(conversation_state, 0.9)
```

## Sentiment-Aware Adjustments

### Frustration Detection and Response
When frustration is detected in student responses:
- **Rate adjustment**: Reduce to 0.85 (slower, more patient)
- **Tone modification**: More encouraging and supportive
- **Response style**: Shorter sentences, clearer explanations

### Sentiment Indicators
- **Frustrated**: "difficult", "hard", "can't", "don't understand"
- **Confident**: "easy", "got it", "understand", "ready"
- **Discouraged**: "tired", "give up", "pointless", "bad at"

## Audio Format Requirements

### Telephony Standards
- **Output Format**: Audio URLs from ElevenLabs API
- **Source Quality**: High-quality conversational AI audio
- **Integration**: Direct audio playback via Twilio `<Play>` verb

### Quality Assurance
- **Bit Rate**: Optimized for telephony bandwidth
- **Latency**: <500ms for TTS generation
- **Clarity**: Tested for phone line quality

## Barge-in Configuration

### Sentence Chunking
- **Method**: Automatic splitting on sentence boundaries
- **Micro-pauses**: 200ms between sentences
- **Interruption**: Redis flags enable mid-sentence barge-in
- **Response Time**: ≤250ms interruption detection

### Implementation Details
```python
# Enable barge-in after intro
if conversation_state == "intro" and len(response) > 100:
    chunks = self._split_into_sentences(response)
    return self._create_chunked_twiml(chunks, enable_barge_in=True)
```

## Fallback Chain

### Voice Provider Hierarchy
1. **Primary**: ElevenLabs Conversational AI
2. **Secondary**: Twilio `<Say>` verb with fallback message
3. **Last Resort**: Basic TwiML error handling

### Fallback Triggers
- API timeout (>5 seconds)
- Service unavailability
- Audio format conversion errors

## Cultural Context Integration

### Rwandan Context Features
- **Greetings**: "Muraho neza!" in introductions
- **Cultural references**: Hills, coffee, community values
- **Ubuntu philosophy**: Emphasis on community and mutual support
- **Local examples**: Kigali, markets, familiar scenarios

### Language Sensitivity
- **Accent tolerance**: Focus on meaning over pronunciation
- **Grammar scaffolding**: Gentle corrections without interruption
- **Cultural bridge**: Mixing Kinyarwanda and English appropriately

## Environment Variables

### Required Configuration
```bash
ELEVENLABS_API_KEY=your_elevenlabs_api_key
MCP_SERVER_URL=http://localhost:8001
```

### ElevenLabs Agent Configuration
```bash
# Agent ID in ElevenLabs dashboard
ELEVENLABS_AGENT_ID=bakame

# Voice settings
ELEVENLABS_STABILITY=0.5
ELEVENLABS_SIMILARITY_BOOST=0.8
```

## Testing and Validation

### Voice Quality Tests
```bash
# Test TTS pipeline
poetry run python scripts/tts_audit.py

# Validate audio format
poetry run python scripts/check_audio.py

# Test barge-in functionality
poetry run python scripts/test_barge_in.py
```

### Performance Metrics
- **TTS Latency**: Target <500ms
- **Audio Quality**: 8kHz μ-law validation
- **Barge-in Response**: <250ms detection time
- **Fallback Success**: >99% availability

## Troubleshooting

### Common Issues
1. **Deepgram API Errors**: Check encoding parameter (must be 'linear16', not 'wav')
2. **Audio Format Issues**: Verify FFmpeg installation and μ-law codec support
3. **Barge-in Problems**: Check Redis connectivity and session flag management
4. **Temperature Not Applied**: Verify conversation_state parameter in LLM calls

### Debug Commands
```bash
# Check TTS service health
curl -X POST "https://api.deepgram.com/v1/speak" \
  -H "Authorization: Token YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}'

# Validate audio output
ffprobe output.wav

# Test Redis session flags
redis-cli GET "session:phone_number:barge_in_enabled"
```
