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
from redis_service import redis_service

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

def get_or_create_user(phone_number: str) -> Dict:
    """Get existing user or create new one"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM user_profiles WHERE phone_number = %s", (phone_number,))
                user = cur.fetchone()
                
                if user:
                    cur.execute("""
                        UPDATE user_profiles 
                        SET last_active = %s 
                        WHERE phone_number = %s
                    """, (datetime.utcnow(), phone_number))
                    conn.commit()
                    return dict(user)
                else:
                    cur.execute("""
                        INSERT INTO user_profiles (phone_number, profile_completed)
                        VALUES (%s, FALSE)
                        RETURNING *
                    """, (phone_number,))
                    new_user = cur.fetchone()
                    conn.commit()
                    return dict(new_user) if new_user else {"phone_number": phone_number, "profile_completed": False}
    except Exception as e:
        print(f"[DB ERROR] Failed to get/create user: {e}")
        return {"phone_number": phone_number, "profile_completed": False}

def update_user_profile(phone_number: str, name: Optional[str] = None, region: Optional[str] = None, school: Optional[str] = None):
    """Update user profile information"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                updates = []
                values = []
                
                if name:
                    updates.append("name = %s")
                    values.append(name)
                if region:
                    updates.append("region = %s")
                    values.append(region)
                if school:
                    updates.append("school = %s")
                    values.append(school)
                
                if updates:
                    updates.append("profile_completed = TRUE")
                    values.append(phone_number)
                    
                    query = f"UPDATE user_profiles SET {', '.join(updates)} WHERE phone_number = %s"
                    cur.execute(query, values)
                    conn.commit()
                    print(f"[USER] Updated profile for {phone_number}")
    except Exception as e:
        print(f"[DB ERROR] Failed to update user profile: {e}")

def log_learning_history(phone_number: str, topic: str, duration_seconds: int = 0):
    """Log learning interaction to history"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO learning_history (phone_number, topic, duration_seconds)
                    VALUES (%s, %s, %s)
                """, (phone_number, topic, duration_seconds))
                conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to log learning history: {e}")

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
    call_sid = str(form_data.get("CallSid", ""))
    from_number = str(form_data.get("From", ""))
    call_status = str(form_data.get("CallStatus", ""))
    
    # Get or create user profile
    user = get_or_create_user(from_number)
    print(f"[USER] Identified user: {from_number}, Profile completed: {user.get('profile_completed', False)}")
    
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
    
    # Initialize conversation history for this call (keyed by call_sid)
    if call_sid not in call_sessions:
        call_sessions[call_sid] = []
        print(f"[SESSION] Started new conversation for {call_sid}")
    
    # Store phone number mapping for this call
    call_sessions[f"{call_sid}_phone"] = from_number
    
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
    
    # Generate greeting based on user status
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

        # Build context for ChatGPT
        profile_context = ""
        
        if not user.get('profile_completed'):
            # New user - ChatGPT needs to collect: name, region, school
            profile_state = redis_service.get_user_context(from_number).get('user_state', {})
            missing_info = []
            if not profile_state.get('name_collected'):
                missing_info.append("name")
            if not profile_state.get('region_collected'):
                missing_info.append("location/region")
            if not profile_state.get('school_collected'):
                missing_info.append("school")
            
            profile_context = f"\n\nIMPORTANT: This is a new student. During this call, naturally find out their {', '.join(missing_info)} if they haven't shared it yet. Be conversational and friendly - don't interrogate them."
            print(f"[GREETING] New user - needs: {', '.join(missing_info)}")
        else:
            # Returning user - provide their context
            user_name = user.get('name', 'friend')
            user_context = redis_service.get_user_context(from_number)
            
            profile_context = f"\n\nStudent name: {user_name}"
            if user_context.get('topics_discussed'):
                recent_topics = user_context['topics_discussed'][-3:]
                profile_context += f"\nPreviously discussed: {', '.join(recent_topics)}"
            
            print(f"[GREETING] Returning user: {user_name}")
        
        enhanced_system_prompt = system_prompt + profile_context
        
        greeting_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": "Generate a warm greeting for the student calling."}
            ],
            temperature=1.0
        )
        greeting = greeting_response.choices[0].message.content
        log_openai_usage(str(call_sid), "gpt-4o", greeting_response.usage, "greeting_generation")
        
        print(f"[GREETING] GPT-4o greeting: {greeting}")
    except Exception as e:
        print(f"[GREETING] Error generating greeting: {e}")
    
    # Create TwiML response with dynamic greeting
    response = VoiceResponse()
    response.say(greeting, voice="alice", language="en-US")
    
    # Gather user speech - High timeout allows unlimited thinking time
    gather = Gather(
        input='speech',
        action='/voice/process',
        speech_timeout='auto',
        timeout=3600,  # 1 hour - allows students to think as long as needed
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
    call_sid = str(form_data.get("CallSid", ""))
    from_number = str(form_data.get("From", ""))
    user_speech = str(form_data.get("SpeechResult", ""))
    
    if not user_speech:
        response = VoiceResponse()
        response.say("I didn't catch that. Let's try again.")
        response.redirect('/voice/incoming')
        return Response(content=str(response), media_type="application/xml")
    
    # Get phone number for this call
    if f"{call_sid}_phone" not in call_sessions:
        call_sessions[f"{call_sid}_phone"] = from_number
    
    phone_number = call_sessions.get(f"{call_sid}_phone", from_number)
    
    # Initialize session if needed
    if call_sid not in call_sessions:
        call_sessions[call_sid] = []
    
    # Get user profile
    user = get_or_create_user(phone_number)
    user_context = redis_service.get_user_context(phone_number)
    
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
    
    # Check if user wants to end the call - ONLY user can hang up
    exit_keywords = ['goodbye', 'bye', 'stop talking', 'hang up', 'end call', 'finish']
    if check_intent(str(user_speech), exit_keywords):
        # User explicitly wants to end call
        if call_sid in call_sessions:
            session_length = len(call_sessions[call_sid])
            del call_sessions[call_sid]
            print(f"[SESSION] User ended conversation for {call_sid} ({session_length} messages)")
        
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
        
        response = VoiceResponse()
        response.say("Thank you for learning with Bakame AI. Keep up the great work! Goodbye!", voice="alice")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    # Add user message to conversation history
    call_sessions[call_sid].append({"role": "user", "content": user_speech})
    print(f"[GPT-4o CALL] User said: {user_speech}")
    print(f"[SESSION] Conversation history length: {len(call_sessions[call_sid])} messages")
    
    # Get AI response from OpenAI
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

        # Handle profile collection for new users
        if not user.get('profile_completed'):
            profile_state = user_context.get('user_state', {})
            
            # Detect if user shared profile information
            user_speech_lower = str(user_speech).lower()
            
            # Check for name (if not collected)
            if not profile_state.get('name_collected'):
                # Assume first response is their name, or extract it intelligently
                profile_state['name_collected'] = True
                profile_state['user_name'] = str(user_speech).strip()
                user_context['user_state'] = profile_state
                redis_service.set_user_context(phone_number, user_context)
                print(f"[PROFILE] Name collected: {user_speech.strip()}")
                
            # Check for region/location
            elif not profile_state.get('region_collected'):
                profile_state['region_collected'] = True
                profile_state['user_region'] = str(user_speech).strip()
                user_context['user_state'] = profile_state
                redis_service.set_user_context(phone_number, user_context)
                print(f"[PROFILE] Region collected: {user_speech.strip()}")
                
            # Check for school
            elif not profile_state.get('school_collected'):
                profile_state['school_collected'] = True
                profile_state['user_school'] = str(user_speech).strip()
                user_context['user_state'] = profile_state
                redis_service.set_user_context(phone_number, user_context)
                print(f"[PROFILE] School collected: {user_speech.strip()}")
                
                # Save to database
                update_user_profile(
                    phone_number,
                    name=profile_state.get('user_name'),
                    region=profile_state.get('user_region'),
                    school=profile_state.get('user_school')
                )
                print(f"[PROFILE] Profile completed for {phone_number}")
            
            # Build context for ChatGPT about what's still needed
            missing_info = []
            if not profile_state.get('name_collected'):
                missing_info.append("name")
            if not profile_state.get('region_collected'):
                missing_info.append("location/region")
            if not profile_state.get('school_collected'):
                missing_info.append("school")
            
            profile_goal = ""
            if missing_info:
                profile_goal = f"\n\nGOAL: Naturally find out their {', '.join(missing_info)} during this conversation. Be conversational - don't make it feel like a form."
            
            enhanced_prompt = system_prompt + profile_goal
            messages = [{"role": "system", "content": enhanced_prompt}] + call_sessions[call_sid]
            
            completion = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=1.0
            )
            
            ai_text = completion.choices[0].message.content
            log_openai_usage(str(call_sid), "gpt-4o", completion.usage, "conversation_response")
        else:
            # Normal learning conversation for users with completed profiles
            user_name = user.get('name', 'friend')
            
            # Extract topic from conversation
            topic_keywords = ['math', 'science', 'english', 'reading', 'history', 'geography']
            detected_topic = None
            for keyword in topic_keywords:
                if keyword in str(user_speech).lower():
                    detected_topic = keyword
                    redis_service.add_topic(phone_number, keyword)
                    log_learning_history(phone_number, keyword)
                    break
            
            # Build context for ChatGPT
            context_parts = [f"Student name: {user_name}"]
            
            if user_context.get('topics_discussed'):
                recent_topics = user_context['topics_discussed'][-3:]
                context_parts.append(f"Previous topics: {', '.join(recent_topics)}")
            
            context_message = "\n".join(context_parts)
            enhanced_prompt = system_prompt + f"\n\n{context_message}"
            messages = [{"role": "system", "content": enhanced_prompt}] + call_sessions[call_sid]
            
            completion = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=1.0
            )
            
            ai_text = completion.choices[0].message.content
            log_openai_usage(str(call_sid), "gpt-4o", completion.usage, "conversation_response")
        
        print(f"[GPT-4o RESPONSE] AI said: {ai_text}")
        
        # Add assistant response to conversation history
        call_sessions[call_sid].append({"role": "assistant", "content": ai_text})
        
        # Store in Redis for long-term context
        redis_service.add_to_conversation_history(phone_number, str(user_speech), str(ai_text))
        
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
                """, (call_sid, from_number, user_speech, ai_text, datetime.utcnow(), "conversation"))
                conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to log conversation: {e}")
    
    # Create TwiML response - Keep conversation flowing naturally
    response = VoiceResponse()
    response.say(ai_text, voice="alice", language="en-US")
    
    # Continue listening for next question - High timeout allows unlimited thinking
    gather = Gather(
        input='speech',
        action='/voice/process',
        speech_timeout='auto',
        timeout=3600,  # 1 hour - students can pause to think as long as needed
        language='en-US'
    )
    response.append(gather)
    
    # If no speech detected after timeout, loop back to keep listening
    response.redirect('/voice/process')
    
    return Response(content=str(response), media_type="application/xml")

def check_intent(text: str, keywords: list) -> bool:
    """Check if any keyword matches as a whole word in the text"""
    text_lower = text.lower()
    pattern = r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b'
    return bool(re.search(pattern, text_lower))

@app.post("/voice/continue")
async def handle_continue(request: Request):
    """Handle user decision to continue or end call - This endpoint is now unused but kept for compatibility"""
    form_data = await request.form()
    call_sid = str(form_data.get("CallSid", ""))
    
    # Redirect back to main conversation flow
    response = VoiceResponse()
    response.redirect('/voice/process')
    
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
                total_calls_result = cur.fetchone()
                total_calls = total_calls_result["total"] if total_calls_result else 0
                
                cur.execute("SELECT COUNT(DISTINCT from_number) as unique FROM call_logs WHERE from_number IS NOT NULL")
                unique_callers_result = cur.fetchone()
                unique_callers = unique_callers_result["unique"] if unique_callers_result else 0
                
                cur.execute("SELECT COUNT(*) as conversations FROM call_logs WHERE event_type = 'conversation'")
                total_conversations_result = cur.fetchone()
                total_conversations = total_conversations_result["conversations"] if total_conversations_result else 0
                
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
                        "total_requests": openai_stats["total"] if openai_stats else 0,
                        "total_tokens": int(openai_stats["tokens"]) if openai_stats else 0,
                        "estimated_cost": round(float(openai_stats["cost"]), 4) if openai_stats else 0
                    },
                    "twilio": {
                        "total_calls": twilio_stats["total"] if twilio_stats else 0,
                        "completed_calls": twilio_stats["completed"] if twilio_stats else 0
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
