import os
import re
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, List, Dict
import json

app = FastAPI(title="Bakame AI MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using GPT-4o as requested by user
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Enhanced storage for comprehensive logging
call_logs = []
openai_usage_logs = []
twilio_call_details = {}

# Session storage: conversation history per call
call_sessions = {}

class CallLog(BaseModel):
    call_sid: Optional[str] = None
    from_number: Optional[str] = None
    message: Optional[str] = None
    ai_response: Optional[str] = None
    timestamp: str

class OpenAIUsage(BaseModel):
    call_sid: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    request_type: str
    timestamp: str

def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate OpenAI API cost based on token usage"""
    # Pricing as of 2024 (per 1M tokens)
    pricing = {
        "gpt-4o": {"prompt": 2.50, "completion": 10.00},
        "gpt-4": {"prompt": 30.00, "completion": 60.00},
    }
    
    if model in pricing:
        prompt_cost = (prompt_tokens / 1_000_000) * pricing[model]["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing[model]["completion"]
        return round(prompt_cost + completion_cost, 6)
    return 0.0

def log_openai_usage(call_sid: str, model: str, usage, request_type: str):
    """Log OpenAI API usage for cost tracking"""
    log_entry = {
        "call_sid": call_sid,
        "model": model,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "estimated_cost": estimate_cost(model, usage.prompt_tokens, usage.completion_tokens),
        "request_type": request_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    openai_usage_logs.append(log_entry)
    print(f"[OPENAI USAGE] {request_type}: {usage.total_tokens} tokens, ~${log_entry['estimated_cost']}")
    return log_entry

@app.get("/")
async def root():
    return {"message": "Bakame AI MVP Backend", "status": "running"}

@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio voice calls"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    call_status = form_data.get("CallStatus")
    
    # Store Twilio call details
    if call_sid not in twilio_call_details:
        twilio_call_details[call_sid] = {
            "call_sid": call_sid,
            "from_number": from_number,
            "to_number": form_data.get("To"),
            "call_status": call_status,
            "direction": form_data.get("Direction"),
            "from_city": form_data.get("FromCity"),
            "from_state": form_data.get("FromState"),
            "from_country": form_data.get("FromCountry"),
            "start_time": datetime.utcnow().isoformat(),
            "interactions": 0
        }
    
    # Initialize conversation history for this call
    if call_sid not in call_sessions:
        call_sessions[call_sid] = []
        print(f"[SESSION] Started new conversation for {call_sid}")
    
    # Log the incoming call
    call_logs.append({
        "call_sid": call_sid,
        "from_number": from_number,
        "message": "Incoming call",
        "ai_response": None,
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "call_started"
    })
    
    # Generate dynamic GPT greeting
    greeting = "Hello! I'm here to help you learn. What would you like to explore today?"
    try:
        system_prompt = """You are Bakame AI, an educational tutor helping students in underserved communities learn through voice calls.

Core Teaching Principles:
- Use the Socratic method: ask guiding questions rather than giving direct answers
- Adapt to the student's knowledge level and pace
- Keep responses brief (2-3 sentences max) for natural phone conversation
- Be encouraging and patient - celebrate progress
- Break complex topics into simple, digestible pieces
- Use real-world examples and analogies
- Check for understanding before moving forward

Communication Style:
- Friendly, warm, and supportive tone
- Use conversational language, avoid jargon
- Include natural verbal cues like "Great question!", "I see", "Let's think about this"
- Speak clearly and pause naturally between ideas

Your Approach:
1. First assess what the student already knows
2. Guide them to discover answers through questions and hints
3. Provide clear explanations only after they've tried
4. Encourage critical thinking and curiosity

Remember: You're on a phone call, so be concise and conversational. Your goal is to help students discover knowledge, not just deliver information."""

        print("[GREETING] Generating dynamic GPT-4o greeting...")
        greeting_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "A student just called. Please greet them warmly and invite them to ask a question. Keep it very brief - just 1-2 sentences for a phone call."}
            ],
            temperature=1.0
        )
        greeting = greeting_response.choices[0].message.content
        
        # Log OpenAI usage
        log_openai_usage(str(call_sid), "gpt-4o", greeting_response.usage, "greeting_generation")
        
        print(f"[GREETING] GPT-4o greeting: {greeting}")
    except Exception as e:
        print(f"[GREETING] Error generating greeting: {e}")
    
    # Create TwiML response with dynamic greeting
    response = VoiceResponse()
    response.say(greeting, voice="alice", language="en-US")
    
    # Gather user speech
    gather = Gather(
        input='speech',
        action='/voice/process',
        speech_timeout='auto',
        language='en-US'
    )
    response.append(gather)
    
    # If no input, redirect
    response.redirect('/voice/incoming')
    
    return Response(content=str(response), media_type="application/xml")

@app.post("/voice/process")
async def process_speech(request: Request):
    """Process user speech and generate AI response"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    user_speech = form_data.get("SpeechResult", "")
    
    if not user_speech:
        response = VoiceResponse()
        response.say("I didn't catch that. Let's try again.")
        response.redirect('/voice/incoming')
        return Response(content=str(response), media_type="application/xml")
    
    # Initialize session if needed
    if call_sid not in call_sessions:
        call_sessions[call_sid] = []
    
    # Update Twilio call details
    if call_sid in twilio_call_details:
        twilio_call_details[call_sid]["interactions"] += 1
    
    # Add user message to conversation history
    call_sessions[call_sid].append({"role": "user", "content": user_speech})
    print(f"[GPT-4o CALL] User said: {user_speech}")
    print(f"[SESSION] Conversation history length: {len(call_sessions[call_sid])} messages")
    
    # Get AI response from OpenAI with streaming
    try:
        system_prompt = """You are Bakame AI, an educational tutor helping students in underserved communities learn through voice calls.

Core Teaching Principles:
- Use the Socratic method: ask guiding questions rather than giving direct answers
- Adapt to the student's knowledge level and pace
- Keep responses brief (2-3 sentences max) for natural phone conversation
- Be encouraging and patient - celebrate progress
- Break complex topics into simple, digestible pieces
- Use real-world examples and analogies
- Check for understanding before moving forward

Communication Style:
- Friendly, warm, and supportive tone
- Use conversational language, avoid jargon
- Include natural verbal cues like "Great question!", "I see", "Let's think about this"
- Speak clearly and pause naturally between ideas

Your Approach:
1. First assess what the student already knows
2. Guide them to discover answers through questions and hints
3. Provide clear explanations only after they've tried
4. Encourage critical thinking and curiosity

Remember: You're on a phone call, so be concise and conversational. Your goal is to help students discover knowledge, not just deliver information."""

        # Build messages with full conversation history
        messages = [{"role": "system", "content": system_prompt}] + call_sessions[call_sid]
        
        # Use non-streaming for complete usage data
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=1.0
        )
        
        ai_text = completion.choices[0].message.content
        
        # Log OpenAI usage
        log_openai_usage(str(call_sid), "gpt-4o", completion.usage, "conversation_response")
        
        print(f"[GPT-4o RESPONSE] AI said: {ai_text}")
        
        # Add assistant response to conversation history
        call_sessions[call_sid].append({"role": "assistant", "content": ai_text})
    except Exception as e:
        ai_text = "I'm having trouble processing that right now. Please try again later."
        print(f"OpenAI error: {e}")
    
    # Log the interaction
    call_logs.append({
        "call_sid": call_sid,
        "from_number": form_data.get("From"),
        "message": user_speech,
        "ai_response": ai_text,
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "conversation"
    })
    
    # Create TwiML response
    response = VoiceResponse()
    response.say(ai_text, voice="alice", language="en-US")
    
    # Ask if they want to continue
    gather = Gather(
        input='speech',
        action='/voice/continue',
        speech_timeout='auto',
        language='en-US',
        timeout=3
    )
    gather.say("Would you like to ask another question?", voice="alice")
    response.append(gather)
    
    # If no response, thank and hangup
    response.say("Thank you for using Bakame AI. Goodbye!", voice="alice")
    response.hangup()
    
    return Response(content=str(response), media_type="application/xml")

def check_intent(text: str, keywords: list) -> bool:
    """Check if any keyword matches as a whole word in the text"""
    text_lower = text.lower()
    pattern = r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b'
    return bool(re.search(pattern, text_lower))

@app.post("/voice/continue")
async def handle_continue(request: Request):
    """Handle user decision to continue or end call"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    user_speech = form_data.get("SpeechResult", "")
    
    # Log the continuation decision
    call_logs.append({
        "call_sid": call_sid,
        "from_number": form_data.get("From"),
        "message": f"Continue prompt response: {user_speech}",
        "ai_response": None,
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "continuation_decision"
    })
    
    response = VoiceResponse()
    
    # Check if user wants to continue using whole-word matching
    exit_keywords = ['no', 'nope', 'stop', 'goodbye', 'bye', 'quit', 'exit', 'done', 'finish', 'end']
    continue_keywords = ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'continue']
    
    if check_intent(str(user_speech), exit_keywords):
        # End the call
        if call_sid in call_sessions:
            session_length = len(call_sessions[call_sid])
            del call_sessions[call_sid]
            print(f"[SESSION] Ended conversation for {call_sid} ({session_length} messages)")
        
        # Update Twilio call details
        if call_sid in twilio_call_details:
            twilio_call_details[call_sid]["end_time"] = datetime.utcnow().isoformat()
            twilio_call_details[call_sid]["call_status"] = "completed"
        
        response.say("Thank you for using Bakame AI. Goodbye!", voice="alice")
        response.hangup()
    elif check_intent(str(user_speech), continue_keywords):
        # Continue with another question
        gather = Gather(
            input='speech',
            action='/voice/process',
            speech_timeout='auto',
            language='en-US'
        )
        gather.say("What would you like to know?", voice="alice")
        response.append(gather)
        response.redirect('/voice/incoming')
    else:
        # Unclear response, ask again
        gather = Gather(
            input='speech',
            action='/voice/continue',
            speech_timeout='auto',
            language='en-US',
            timeout=3
        )
        gather.say("I didn't quite catch that. Would you like to continue? Say yes or no.", voice="alice")
        response.append(gather)
        
        # Clear conversation history on timeout
        if call_sid in call_sessions:
            del call_sessions[call_sid]
            print(f"[SESSION] Ended conversation for {call_sid} (timeout)")
        
        if call_sid in twilio_call_details:
            twilio_call_details[call_sid]["end_time"] = datetime.utcnow().isoformat()
            twilio_call_details[call_sid]["call_status"] = "completed"
        
        response.say("Thank you for using Bakame AI. Goodbye!", voice="alice")
        response.hangup()
    
    return Response(content=str(response), media_type="application/xml")

@app.get("/api/calls")
async def get_call_logs():
    """Get all call logs for admin dashboard"""
    return {"calls": call_logs, "total": len(call_logs)}

@app.get("/api/openai-usage")
async def get_openai_usage():
    """Get OpenAI usage statistics"""
    total_tokens = sum(log["total_tokens"] for log in openai_usage_logs)
    total_cost = sum(log["estimated_cost"] for log in openai_usage_logs)
    
    return {
        "logs": openai_usage_logs,
        "summary": {
            "total_requests": len(openai_usage_logs),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "greeting_requests": len([l for l in openai_usage_logs if l["request_type"] == "greeting_generation"]),
            "conversation_requests": len([l for l in openai_usage_logs if l["request_type"] == "conversation_response"])
        }
    }

@app.get("/api/twilio-calls")
async def get_twilio_calls():
    """Get Twilio call details"""
    return {
        "calls": list(twilio_call_details.values()),
        "total": len(twilio_call_details)
    }

@app.get("/api/conversations/{call_sid}")
async def get_conversation(call_sid: str):
    """Get full conversation history for a specific call"""
    if call_sid in call_sessions:
        return {
            "call_sid": call_sid,
            "messages": call_sessions[call_sid],
            "message_count": len(call_sessions[call_sid])
        }
    return {"error": "Conversation not found or already ended"}

@app.get("/api/dashboard-stats")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    unique_callers = len(set(log.get("from_number") for log in call_logs if log.get("from_number")))
    total_conversations = len([log for log in call_logs if log.get("event_type") == "conversation"])
    active_sessions = len(call_sessions)
    
    # OpenAI stats
    total_tokens = sum(log["total_tokens"] for log in openai_usage_logs)
    total_cost = sum(log["estimated_cost"] for log in openai_usage_logs)
    
    return {
        "calls": {
            "total": len(call_logs),
            "unique_callers": unique_callers,
            "conversations": total_conversations,
            "active_sessions": active_sessions
        },
        "openai": {
            "total_requests": len(openai_usage_logs),
            "total_tokens": total_tokens,
            "estimated_cost": round(total_cost, 4)
        },
        "twilio": {
            "total_calls": len(twilio_call_details),
            "completed_calls": len([c for c in twilio_call_details.values() if c.get("call_status") == "completed"])
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "openai_configured": bool(os.getenv("OPENAI_API_KEY"))}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
