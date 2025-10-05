import os
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
    
    # Create TwiML response
    response = VoiceResponse()
    response.say("Welcome to Bakame AI. I'm your learning assistant. How can I help you today?", 
                 voice="alice", language="en-US")
    
    # Gather user speech
    gather = Gather(
        input='speech',
        action='/voice/process',
        speech_timeout='auto',
        language='en-US'
    )
    gather.say("Please tell me what you'd like to learn about.")
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
        ai_response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are Bakame AI, a friendly and helpful educational assistant. Provide clear, concise answers suitable for phone conversations. Keep responses under 50 words."},
                {"role": "user", "content": user_speech}
            ],
            max_completion_tokens=150
        )
        ai_text = ai_response.choices[0].message.content
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
    response.say("Would you like to ask anything else?", voice="alice")
    
    # Gather next input
    gather = Gather(
        input='speech',
        action='/voice/process',
        speech_timeout='auto',
        language='en-US'
    )
    gather.say("Say yes to continue, or no to end the call.")
    response.append(gather)
    
    response.say("Thank you for using Bakame AI. Goodbye!")
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
