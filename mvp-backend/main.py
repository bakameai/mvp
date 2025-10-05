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
import psycopg2
from psycopg2.extras import RealDictCursor

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

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Create a new database connection"""
    return psycopg2.connect(DATABASE_URL)

# Session storage: conversation history per call (still in-memory for active sessions)
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
    estimated_cost = estimate_cost(model, usage.prompt_tokens, usage.completion_tokens)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO openai_usage_logs 
                    (call_sid, model, prompt_tokens, completion_tokens, total_tokens, estimated_cost, request_type, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (call_sid, model, usage.prompt_tokens, usage.completion_tokens, 
                      usage.total_tokens, estimated_cost, request_type, datetime.utcnow()))
                conn.commit()
        print(f"[OPENAI USAGE] {request_type}: {usage.total_tokens} tokens, ~${estimated_cost}")
    except Exception as e:
        print(f"[DB ERROR] Failed to log OpenAI usage: {e}")
    
    return {
        "call_sid": call_sid,
        "model": model,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "estimated_cost": estimated_cost,
        "request_type": request_type
    }

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
    
    # Store Twilio call details in database
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO twilio_call_logs 
                    (call_sid, from_number, to_number, call_status, direction, from_city, from_state, from_country, start_time, interactions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (call_sid) DO NOTHING
                """, (call_sid, from_number, form_data.get("To"), call_status, form_data.get("Direction"),
                      form_data.get("FromCity"), form_data.get("FromState"), form_data.get("FromCountry"), 
                      datetime.utcnow(), 0))
                conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to log Twilio call: {e}")
    
    # Initialize conversation history for this call
    if call_sid not in call_sessions:
        call_sessions[call_sid] = []
        print(f"[SESSION] Started new conversation for {call_sid}")
    
    # Log the incoming call
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO call_logs 
                    (call_sid, from_number, message, ai_response, timestamp, event_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (call_sid, from_number, "Incoming call", None, datetime.utcnow(), "call_started"))
                conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to log call: {e}")
    
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
    
    # Update Twilio call details - increment interactions
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE twilio_call_logs 
                    SET interactions = interactions + 1
                    WHERE call_sid = %s
                """, (call_sid,))
                conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to update interactions: {e}")
    
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
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO call_logs 
                    (call_sid, from_number, message, ai_response, timestamp, event_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (call_sid, form_data.get("From"), user_speech, ai_text, datetime.utcnow(), "conversation"))
                conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to log conversation: {e}")
    
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
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO call_logs 
                    (call_sid, from_number, message, ai_response, timestamp, event_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (call_sid, form_data.get("From"), f"Continue prompt response: {user_speech}", 
                      None, datetime.utcnow(), "continuation_decision"))
                conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to log continuation decision: {e}")
    
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
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE twilio_call_logs 
                        SET end_time = %s, call_status = 'completed'
                        WHERE call_sid = %s
                    """, (datetime.utcnow(), call_sid))
                    conn.commit()
        except Exception as e:
            print(f"[DB ERROR] Failed to update call end time: {e}")
        
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
        
        # Update Twilio call details
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE twilio_call_logs 
                        SET end_time = %s, call_status = 'completed'
                        WHERE call_sid = %s
                    """, (datetime.utcnow(), call_sid))
                    conn.commit()
        except Exception as e:
            print(f"[DB ERROR] Failed to update call end time: {e}")
        
        response.say("Thank you for using Bakame AI. Goodbye!", voice="alice")
        response.hangup()
    
    return Response(content=str(response), media_type="application/xml")

@app.get("/api/calls")
async def get_call_logs():
    """Get all call logs for admin dashboard"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM call_logs ORDER BY timestamp DESC")
                calls = cur.fetchall()
                calls_list = [dict(call) for call in calls]
                return {"calls": calls_list, "total": len(calls_list)}
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch call logs: {e}")
        return {"calls": [], "total": 0}

@app.get("/api/openai-usage")
async def get_openai_usage():
    """Get OpenAI usage statistics"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM openai_usage_logs ORDER BY timestamp DESC")
                logs = cur.fetchall()
                logs_list = [dict(log) for log in logs]
                total_tokens = sum(log["total_tokens"] for log in logs_list)
                total_cost = sum(float(log["estimated_cost"]) for log in logs_list)
                
                return {
                    "logs": logs_list,
                    "summary": {
                        "total_requests": len(logs_list),
                        "total_tokens": total_tokens,
                        "total_cost": round(total_cost, 4),
                        "greeting_requests": len([l for l in logs_list if l["request_type"] == "greeting_generation"]),
                        "conversation_requests": len([l for l in logs_list if l["request_type"] == "conversation_response"])
                    }
                }
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch OpenAI usage: {e}")
        return {"logs": [], "summary": {"total_requests": 0, "total_tokens": 0, "total_cost": 0, "greeting_requests": 0, "conversation_requests": 0}}

@app.get("/api/twilio-calls")
async def get_twilio_calls():
    """Get Twilio call details"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM twilio_call_logs ORDER BY start_time DESC")
                calls = cur.fetchall()
                calls_list = [dict(call) for call in calls]
                return {"calls": calls_list, "total": len(calls_list)}
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch Twilio calls: {e}")
        return {"calls": [], "total": 0}

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
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get call stats
                cur.execute("SELECT COUNT(*) as total FROM call_logs")
                total_calls = cur.fetchone()["total"]
                
                cur.execute("SELECT COUNT(DISTINCT from_number) as unique FROM call_logs WHERE from_number IS NOT NULL")
                unique_callers = cur.fetchone()["unique"]
                
                cur.execute("SELECT COUNT(*) as conversations FROM call_logs WHERE event_type = 'conversation'")
                total_conversations = cur.fetchone()["conversations"]
                
                # Get OpenAI stats
                cur.execute("SELECT COUNT(*) as total, COALESCE(SUM(total_tokens), 0) as tokens, COALESCE(SUM(estimated_cost), 0) as cost FROM openai_usage_logs")
                openai_stats = cur.fetchone()
                
                # Get Twilio stats
                cur.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN call_status = 'completed' THEN 1 END) as completed FROM twilio_call_logs")
                twilio_stats = cur.fetchone()
                
                return {
                    "calls": {
                        "total": total_calls,
                        "unique_callers": unique_callers,
                        "conversations": total_conversations,
                        "active_sessions": len(call_sessions)
                    },
                    "openai": {
                        "total_requests": openai_stats["total"],
                        "total_tokens": int(openai_stats["tokens"]),
                        "estimated_cost": round(float(openai_stats["cost"]), 4)
                    },
                    "twilio": {
                        "total_calls": twilio_stats["total"],
                        "completed_calls": twilio_stats["completed"]
                    }
                }
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch dashboard stats: {e}")
        return {
            "calls": {"total": 0, "unique_callers": 0, "conversations": 0, "active_sessions": 0},
            "openai": {"total_requests": 0, "total_tokens": 0, "estimated_cost": 0},
            "twilio": {"total_calls": 0, "completed_calls": 0}
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "openai_configured": bool(os.getenv("OPENAI_API_KEY"))}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
