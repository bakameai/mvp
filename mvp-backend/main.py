import os
import re
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import json

app = FastAPI(title="Bakame AI MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory storage for call logs (for MVP)
call_logs = []

class CallLog(BaseModel):
    call_sid: Optional[str] = None
    from_number: Optional[str] = None
    message: Optional[str] = None
    ai_response: Optional[str] = None
    timestamp: str

@app.get("/")
async def root():
    return {"message": "Bakame AI MVP Backend", "status": "running"}

@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio voice calls"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    
    # Log the incoming call
    call_logs.append({
        "call_sid": call_sid,
        "from_number": from_number,
        "message": "Incoming call",
        "ai_response": None,
        "timestamp": str(form_data.get("Timestamp", ""))
    })
    
    # Create TwiML response - let GPT handle the greeting naturally
    response = VoiceResponse()
    
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

        print(f"[GPT CALL] User said: {user_speech}")
        ai_response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_speech}
            ],
            temperature=1.0,
            max_completion_tokens=150
        )
        ai_text = ai_response.choices[0].message.content
        print(f"[GPT RESPONSE] AI said: {ai_text}")
    except Exception as e:
        ai_text = "I'm having trouble processing that right now. Please try again later."
        print(f"OpenAI error: {e}")
    
    # Log the interaction
    call_logs.append({
        "call_sid": call_sid,
        "from_number": form_data.get("From"),
        "message": user_speech,
        "ai_response": ai_text,
        "timestamp": str(form_data.get("Timestamp", ""))
    })
    
    # Create TwiML response
    response = VoiceResponse()
    response.say(ai_text, voice="alice", language="en-US")
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
        "timestamp": str(form_data.get("Timestamp", ""))
    })
    
    response = VoiceResponse()
    
    # Check if user wants to continue using whole-word matching
    # Check exit keywords FIRST to prioritize stopping
    exit_keywords = ['no', 'nope', 'stop', 'goodbye', 'bye', 'quit', 'exit', 'done', 'finish', 'end']
    continue_keywords = ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'continue']
    
    if check_intent(user_speech, exit_keywords):
        # End the call (check this FIRST)
        response.say("Thank you for using Bakame AI. Goodbye!", voice="alice")
        response.hangup()
    elif check_intent(user_speech, continue_keywords):
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
        response.say("Thank you for using Bakame AI. Goodbye!", voice="alice")
        response.hangup()
    
    return Response(content=str(response), media_type="application/xml")

@app.get("/api/calls")
async def get_call_logs():
    """Get all call logs for admin dashboard"""
    return {"calls": call_logs, "total": len(call_logs)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "openai_configured": bool(os.getenv("OPENAI_API_KEY"))}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
