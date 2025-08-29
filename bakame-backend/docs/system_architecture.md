# BAKAME IVR System Architecture

## Overview

The BAKAME IVR system is a comprehensive voice-based learning platform designed for Rwandan students. It combines telephony infrastructure with AI-powered educational content delivery, featuring curriculum-aligned learning paths, emotion-aware interactions, and cultural sensitivity.

## Core Architecture

### Service Layer Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Twilio Voice  │    │  Media Streams  │    │   WebSocket     │
│   Webhooks      │◄──►│   (Real-time)   │◄──►│   Handler       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                             │
├─────────────────┬─────────────────┬─────────────────┬─────────┤
│   Webhooks      │   Admin API     │   Media Stream  │  Health │
│   Router        │   Router        │   Router        │  Check  │
└─────────────────┴─────────────────┴─────────────────┴─────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                             │
├─────────────┬─────────────┬─────────────┬─────────────┬───────┤
│ Curriculum  │ Language    │ Emotional   │ Gamification│ Redis │
│ Service     │ Scaffolding │ Intelligence│ Service     │Service│
└─────────────┴─────────────┴─────────────┴─────────────┴───────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Learning Modules                            │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│   English   │    Math     │   Debate    │   Comprehension     │
│   Module    │   Module    │   Module    │     Module          │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI & External APIs                          │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│   Llama     │   OpenAI    │  Deepgram   │     Twilio          │
│   API       │   API       │   TTS/ASR   │     Voice           │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
```

## Curriculum-Aware Prompt Flow

### Bloom's Taxonomy Integration

The system implements a sophisticated curriculum framework based on Bloom's Taxonomy:

```
Remember → Understand → Apply → Analyze → Evaluate → Create
   ↓           ↓          ↓        ↓         ↓         ↓
Basic      Comprehension  Usage   Analysis  Judgment  Innovation
Recall     & Explanation  in New  of Parts  of Value  & Original
                         Context                      Content
```

### Prompt Injection Architecture

```python
# Curriculum-Aware Prompt Generation
def get_curriculum_prompt(module: str, stage: str, user_context: Dict) -> str:
    curriculum = load_curriculum_data(module, stage)
    
    return f"""
    Module: {module.title()}
    Stage: {stage.title()} (Bloom's Taxonomy)
    Student: {user_context.get('user_name', 'friend')}
    Goal: {curriculum.get('goal', '')}
    
    Key Skills to Practice:
    {format_skills_list(curriculum.get('skills', []))}
    
    Teaching Approach:
    - Use warm, encouraging tone with African cultural context
    - Keep responses under 2 sentences for phone interaction
    - Focus on meaning over perfect grammar
    - Provide gentle corrections when needed
    - Use Rwandan examples and cultural references
    - Encourage effort and progress
    
    Temperature Setting: {get_temperature_for_state(conversation_state)}
    """
```

## Language/Knowledge Split Architecture

### Scaffolding Pipeline

```
User Input → Language Scaffolding → Knowledge Assessment → Response Generation
     │              │                      │                     │
     ▼              ▼                      ▼                     ▼
┌─────────┐  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Raw     │  │ Meaning     │  │ Multi-Factor    │  │ Curriculum-     │
│ Speech  │  │ Extraction  │  │ Scoring:        │  │ Aware Response  │
│ (ASR)   │  │ & Grammar   │  │ • Keyword (40%) │  │ with Cultural   │
│         │  │ Correction  │  │ • Structure(30%)│  │ Context         │
│         │  │             │  │ • LLM Eval(30%) │  │                 │
└─────────┘  └─────────────┘  └─────────────────┘  └─────────────────┘
```

### Assessment Scoring Logic

```python
def assess_student_response(user_input: str, module: str, stage: str) -> Dict:
    # Multi-factor assessment
    keyword_score = assess_keywords(user_input, curriculum_data)
    structure_score = assess_sentence_structure(user_input)
    llm_score = await assess_with_llm(user_input, curriculum_data)
    
    # Weighted final score
    final_score = (
        keyword_score * 0.4 +      # Content relevance
        structure_score * 0.3 +    # Basic grammar
        llm_score * 0.3           # Meaning & effort
    )
    
    # Pass/Fail determination (60% threshold)
    is_pass = final_score >= 0.6
    
    return {
        "overall_score": final_score,
        "is_pass": is_pass,
        "feedback": generate_encouraging_feedback(final_score, is_pass),
        "next_action": "continue" if is_pass else "retry"
    }
```

## Student Progression Tracking

### Redis Data Structure

```
session:{phone_number} = {
    "user_name": "Kevin",
    "curriculum_stages": {
        "english": "apply",
        "math": "understand", 
        "debate": "remember",
        "comprehension": "analyze"
    },
    "assessment_history": {
        "english": [
            {
                "timestamp": "2025-08-29T01:00:00Z",
                "stage": "apply",
                "score": 0.75,
                "is_pass": true,
                "feedback": "Great job! You're showing strong understanding."
            }
        ]
    }
}
```

### Advancement Logic

```python
def check_stage_advancement(phone_number: str, module: str) -> Optional[str]:
    history = get_assessment_history(phone_number, module)
    recent_attempts = history[-5:]  # Last 5 attempts
    
    passes = sum(1 for attempt in recent_attempts if attempt["is_pass"])
    
    # Advancement: 3 passes out of last 5
    if passes >= 3:
        return advance_to_next_stage(phone_number, module)
    
    # Demotion: 3 consecutive failures
    if len(recent_attempts) >= 3:
        recent_failures = all(not attempt["is_pass"] for attempt in recent_attempts[-3:])
        if recent_failures:
            return demote_to_previous_stage(phone_number, module)
    
    return None  # Stay at current stage
```

## Emotion-Aware Interaction System

### Sentiment Analysis Integration

```python
class EmotionalIntelligenceService:
    def detect_emotion(self, user_input: str, asr_confidence: float) -> Dict:
        # Pattern-based emotion detection
        frustration_indicators = ["difficult", "hard", "can't", "don't understand"]
        confidence_indicators = ["easy", "got it", "understand", "ready"]
        
        # Combine text analysis with ASR confidence
        emotion_score = analyze_text_sentiment(user_input)
        confidence_factor = asr_confidence
        
        return {
            "primary_emotion": determine_primary_emotion(emotion_score),
            "confidence_level": confidence_factor,
            "needs_encouragement": emotion_score < 0.3,
            "suggested_temperature": adjust_temperature_for_emotion(emotion_score)
        }
```

### Dynamic Temperature Control

```python
def get_temperature_for_state(conversation_state: str, emotion_context: Dict = None) -> float:
    base_temperatures = {
        "intro": 0.4,           # Consistent greeting
        "normal": 0.9,          # Balanced conversation
        "assessment": 0.2,      # Precise evaluation
        "facts": 1.6,          # Creative Rwanda facts
        "encouragement": 1.2    # Warm, varied support
    }
    
    base_temp = base_temperatures.get(conversation_state, 0.9)
    
    # Adjust for emotional context
    if emotion_context and emotion_context.get("needs_encouragement"):
        base_temp = min(1.6, base_temp + 0.3)  # Warmer for struggling students
    
    return base_temp
```

## Cultural Context Integration

### Ubuntu Philosophy Implementation

The system integrates Ubuntu philosophy throughout:

```python
cultural_context = {
    "ubuntu_principles": [
        "Community support and mutual aid",
        "Respect for elders and traditional wisdom", 
        "Collective responsibility for learning",
        "Patience and understanding in teaching"
    ],
    "rwandan_examples": {
        "locations": ["Kigali", "Butare", "Musanze", "Nyungwe Forest"],
        "activities": ["coffee farming", "market visits", "community meetings"],
        "values": ["hard work", "unity", "progress", "education"]
    },
    "language_patterns": {
        "greetings": "Muraho neza!",
        "encouragement": "Ni byiza cyane! (Very good!)",
        "patience": "Twihangane (Let's be patient)"
    }
}
```

## Data Flow Architecture

### Call Processing Flow

```
1. Twilio Voice Call → Webhook Handler
2. Name Extraction & Confirmation → Redis Session
3. Module Selection → Curriculum Stage Lookup
4. User Input → Language Scaffolding → Assessment
5. LLM Response Generation → TTS → Audio Playback
6. Progress Tracking → Redis/DB Storage
7. Stage Advancement Check → Notification
```

### Assessment Data Pipeline

```
User Response → ASR Transcription → Language Scaffolding → Multi-Factor Assessment
     ↓                ↓                    ↓                      ↓
Raw Audio → Text Confidence → Corrected Text → Keyword + Structure + LLM Scores
     ↓                ↓                    ↓                      ↓
Emotion Detection → Sentiment Analysis → Cultural Context → Encouraging Feedback
     ↓                ↓                    ↓                      ↓
Progress Logging → Redis Storage → Stage Advancement → Dashboard Analytics
```

## Scalability Considerations

### Horizontal Scaling

- **Stateless Services**: All services designed for horizontal scaling
- **Redis Clustering**: Session data distributed across Redis cluster
- **Load Balancing**: Multiple FastAPI instances behind load balancer
- **Circuit Breakers**: Automatic failover between AI providers

### Performance Optimization

- **Curriculum Caching**: Curriculum data cached in memory on startup
- **Connection Pooling**: Persistent connections to external APIs
- **Async Processing**: Non-blocking I/O for all external calls
- **Batch Assessment**: Multiple student responses processed in parallel

## Security & Privacy

### Data Protection

- **PII Redaction**: Automatic removal of sensitive data from logs
- **Session Encryption**: All Redis data encrypted at rest
- **API Authentication**: Secure token-based authentication
- **Audit Logging**: Comprehensive audit trail for all actions

### Compliance

- **GDPR Compliance**: Right to deletion and data portability
- **Educational Privacy**: FERPA-compliant student data handling
- **Rwandan Regulations**: Compliance with local data protection laws

## Monitoring & Observability

### Metrics Collection

```python
@metrics_collector
async def process_student_response(user_input: str, module: str) -> str:
    start_time = time.time()
    
    # Process response
    result = await curriculum_service.assess_student_response(user_input, module)
    
    # Log metrics
    metrics = {
        "processing_time_ms": (time.time() - start_time) * 1000,
        "module": module,
        "assessment_score": result["overall_score"],
        "is_pass": result["is_pass"]
    }
    
    log_turn_metrics(metrics)
    return result
```

### Health Checks

```python
@router.get("/healthz")
async def health_check():
    checks = {
        "redis": await check_redis_connectivity(),
        "database": await check_database_connectivity(), 
        "llama_api": await check_llama_api_health(),
        "openai_api": await check_openai_api_health(),
        "deepgram_api": await check_deepgram_api_health()
    }
    
    overall_status = "healthy" if all(checks.values()) else "degraded"
    
    return {
        "status": overall_status,
        "service": "BAKAME MVP",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Future Architecture Enhancements

### Planned Improvements

1. **Microservices Migration**: Split monolithic backend into focused microservices
2. **Event-Driven Architecture**: Implement event sourcing for student progress
3. **Machine Learning Pipeline**: Add ML models for personalized learning paths
4. **Multi-Language Support**: Extend to support Kinyarwanda and French
5. **Offline Capabilities**: Local AI models for areas with poor connectivity

### Research & Development

- **Adaptive Learning**: AI-driven personalization based on learning patterns
- **Peer Learning**: Student-to-student interaction capabilities
- **Teacher Integration**: Tools for educators to guide and monitor progress
- **Assessment Analytics**: Advanced analytics for curriculum effectiveness
