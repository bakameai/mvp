import asyncio
import json
import websockets
import os
from typing import Optional, AsyncGenerator

class DeepgramTTSClient:
    def __init__(self):
        self.ready = False
        self.conversation_active = False
        self.ws = None
        
    async def connect(self):
        """Initialize Deepgram TTS WebSocket connection."""
        try:
            print("[Deepgram TTS] Initializing client...", flush=True)
            
            api_key = os.environ.get("DEEPGRAM_API_KEY")
            if not api_key:
                print("[Deepgram TTS] ❌ DEEPGRAM_API_KEY not set", flush=True)
                return False
            
            url = "wss://api.deepgram.com/v1/speak?encoding=linear16&sample_rate=16000"
            
            self.ws = await websockets.connect(
                url,
                additional_headers={"Authorization": f"Token {api_key}"}
            )
            print("[Deepgram TTS] ✅ Connection successful", flush=True)
            self.ready = True
            return True
                
        except Exception as e:
            print(f"[Deepgram TTS] ❌ Connection error: {e}", flush=True)
            return False
    
    async def synthesize_response(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize AI response text to audio stream."""
        if not self.ready or not self.ws:
            print("[Deepgram TTS] Client not ready", flush=True)
            return
            
        try:
            message = {"type": "Speak", "text": text}
            await self.ws.send(json.dumps(message))
            
            flush_message = {"type": "Flush"}
            await self.ws.send(json.dumps(flush_message))
            print(f"[Deepgram TTS] Sent text and flush command for synthesis", flush=True)
            
            while True:
                try:
                    response = await asyncio.wait_for(self.ws.recv(), timeout=15.0)
                    
                    if isinstance(response, bytes):
                        yield response
                    else:
                        data = json.loads(response)
                        if data.get("type") == "SpeakFinished":
                            break
                            
                except asyncio.TimeoutError:
                    print("[Deepgram TTS] Timeout waiting for audio (15s), retrying...", flush=True)
                    try:
                        await self.ws.ping()
                        print("[Deepgram TTS] Connection still alive, continuing...", flush=True)
                        continue
                    except Exception as ping_error:
                        print(f"[Deepgram TTS] Connection lost during timeout: {ping_error}", flush=True)
                        break
                except Exception as e:
                    print(f"[Deepgram TTS] Error receiving audio: {e}", flush=True)
                    break
                    
        except Exception as e:
            print(f"[Deepgram TTS] Error synthesizing text: {e}", flush=True)
    
    async def is_connected(self):
        """Check if the WebSocket connection is still healthy."""
        try:
            if not self.ws or not self.ready:
                return False
            await self.ws.ping()
            return True
        except Exception:
            return False

    async def close(self):
        """Close Deepgram TTS connection."""
        self.ready = False
        self.conversation_active = False
        if self.ws:
            await self.ws.close()
        print("[Deepgram TTS] Connection closed", flush=True)

async def open_deepgram_tts():
    """Create and connect Deepgram TTS client."""
    client = DeepgramTTSClient()
    if await client.connect():
        return client
    else:
        raise RuntimeError("Failed to connect to Deepgram TTS")
