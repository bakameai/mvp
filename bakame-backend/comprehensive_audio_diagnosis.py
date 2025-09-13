#!/usr/bin/env python3
"""
Comprehensive Audio Routing Diagnosis
=====================================

This script performs a complete investigation of the ElevenLabs to Twilio audio routing issue.
It simulates the exact WebSocket message flow and identifies where audio is getting lost.
"""

import asyncio
import json
import base64
import time
import websockets
from websockets.exceptions import InvalidStatusCode
import os
import sys

sys.path.append('/home/ubuntu/repos/mvp/bakame-backend')

from app.elevenlabs_client import open_el_ws
from app.main import pcm16_16k_to_twilio_ulaw8k, twilio_ulaw8k_to_pcm16_16k

class AudioRoutingDiagnostic:
    def __init__(self):
        self.el_ws = None
        self.mock_twilio_ws = None
        self.audio_received_count = 0
        self.audio_sent_count = 0
        self.message_log = []
        self.timing_log = []
        
    async def log_message(self, source, message_type, details="", timestamp=None):
        """Log all WebSocket messages with timing"""
        if timestamp is None:
            timestamp = time.time()
        
        log_entry = {
            "timestamp": timestamp,
            "source": source,
            "message_type": message_type,
            "details": details
        }
        self.message_log.append(log_entry)
        print(f"[{timestamp:.3f}] {source}: {message_type} - {details}", flush=True)
    
    async def simulate_twilio_websocket(self):
        """Simulate Twilio WebSocket behavior"""
        class MockTwilioWebSocket:
            def __init__(self):
                self.client_state = type('obj', (object,), {'name': 'CONNECTED'})()
                self.sent_messages = []
                self.is_closed = False
            
            async def send_text(self, message):
                if self.is_closed:
                    raise Exception("Cannot call 'send' once a close message has been sent")
                
                self.sent_messages.append(message)
                data = json.loads(message)
                if data.get("event") == "media":
                    payload = data["media"]["payload"]
                    audio_bytes = base64.b64decode(payload)
                    await self.parent.log_message("MOCK_TWILIO", "AUDIO_RECEIVED", 
                                                 f"Received {len(audio_bytes)} bytes μ-law audio")
                    self.parent.audio_sent_count += 1
                    return True
                return False
            
            def close_connection(self):
                self.is_closed = True
                self.client_state.name = "CLOSED"
        
        mock_ws = MockTwilioWebSocket()
        mock_ws.parent = self
        return mock_ws
    
    async def test_elevenlabs_connection(self):
        """Test ElevenLabs WebSocket connection and message handling"""
        print("=" * 80)
        print("COMPREHENSIVE AUDIO ROUTING DIAGNOSIS")
        print("=" * 80)
        
        try:
            await self.log_message("DIAGNOSTIC", "CONNECTION_TEST", "Testing ElevenLabs WebSocket connection")
            self.el_ws = await open_el_ws()
            await self.log_message("DIAGNOSTIC", "CONNECTION_SUCCESS", "ElevenLabs WebSocket connected successfully")
            
            self.mock_twilio_ws = await self.simulate_twilio_websocket()
            await self.log_message("DIAGNOSTIC", "MOCK_TWILIO_READY", "Mock Twilio WebSocket created")
            
            test_message = {
                "user_audio_chunk": base64.b64encode(b"test audio data" * 100).decode('utf-8')
            }
            await self.el_ws.send(json.dumps(test_message))
            await self.log_message("DIAGNOSTIC", "TEST_AUDIO_SENT", "Sent test audio to ElevenLabs")
            
            await self.simulate_pump_function()
            
        except Exception as e:
            await self.log_message("DIAGNOSTIC", "ERROR", f"Connection test failed: {e}")
            return False
        
        return True
    
    async def simulate_pump_function(self):
        """Simulate the exact pump_el_to_twilio function behavior"""
        await self.log_message("DIAGNOSTIC", "PUMP_SIMULATION", "Starting pump_el_to_twilio simulation")
        
        timeout_duration = 30  # 30 second timeout
        start_time = time.time()
        
        try:
            async for raw in self.el_ws:
                current_time = time.time()
                
                if current_time - start_time > timeout_duration:
                    await self.log_message("DIAGNOSTIC", "TIMEOUT", f"Stopping after {timeout_duration} seconds")
                    break
                
                msg = None
                if isinstance(raw, (bytes, bytearray)):
                    ws_state = self.mock_twilio_ws.client_state.name
                    await self.log_message("EL_BINARY", "AUDIO_RECEIVED", 
                                         f"Binary audio: {len(raw)} bytes, Twilio state: {ws_state}")
                    
                    if ws_state != "CONNECTED":
                        await self.log_message("EL_BINARY", "STATE_CHECK_FAIL", 
                                             f"Twilio not connected (state: {ws_state}), would CONTINUE")
                        continue
                    
                    pcm16k = bytes(raw)
                    ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                    out = {"event": "media", "media": {"payload": ulaw_b64}}
                    
                    success = await self.mock_twilio_ws.send_text(json.dumps(out))
                    if success:
                        await self.log_message("EL_BINARY", "AUDIO_FORWARDED", 
                                             f"Successfully forwarded {len(pcm16k)} bytes PCM")
                
                else:
                    try:
                        msg = json.loads(raw)
                    except Exception as e:
                        await self.log_message("EL_JSON", "PARSE_ERROR", f"Failed to parse JSON: {e}")
                        continue
                    
                    if msg:
                        msg_type = msg.get("type")
                        await self.log_message("EL_JSON", "MESSAGE_RECEIVED", f"Type: {msg_type}")
                        
                        if msg_type == "conversation_initiation_metadata":
                            await self.log_message("EL_JSON", "CONVERSATION_INIT", "ElevenLabs conversation ready")
                        
                        elif msg_type == "audio":
                            audio_event = msg.get("audio_event", {})
                            audio_base64 = audio_event.get("audio_base_64", "")
                            
                            if audio_base64:
                                self.audio_received_count += 1
                                ws_state = self.mock_twilio_ws.client_state.name
                                
                                await self.log_message("EL_AUDIO", "STRUCTURED_AUDIO", 
                                                     f"Audio #{self.audio_received_count}: {len(audio_base64)} chars base64, Twilio state: {ws_state}")
                                
                                try:
                                    if ws_state != "CONNECTED":
                                        await self.log_message("EL_AUDIO", "STATE_CHECK_FAIL", 
                                                             f"Twilio not connected (state: {ws_state}), would CONTINUE")
                                        continue
                                    
                                    pcm16k = base64.b64decode(audio_base64)
                                    ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                                    out = {"event": "media", "media": {"payload": ulaw_b64}}
                                    
                                    await self.log_message("EL_AUDIO", "CONVERSION_SUCCESS", 
                                                         f"Converted {len(pcm16k)} bytes PCM -> {len(base64.b64decode(ulaw_b64))} bytes μ-law")
                                    
                                    success = await self.mock_twilio_ws.send_text(json.dumps(out))
                                    if success:
                                        await self.log_message("EL_AUDIO", "FORWARDING_SUCCESS", 
                                                             f"✅ Successfully forwarded audio chunk #{self.audio_received_count}")
                                    else:
                                        await self.log_message("EL_AUDIO", "FORWARDING_FAILED", 
                                                             f"❌ Failed to forward audio chunk #{self.audio_received_count}")
                                
                                except Exception as e:
                                    await self.log_message("EL_AUDIO", "PROCESSING_ERROR", 
                                                         f"❌ Error processing audio: {e}")
                                    await self.log_message("EL_AUDIO", "ERROR_STATE", 
                                                         f"WebSocket state during error: {ws_state}")
                            else:
                                await self.log_message("EL_AUDIO", "NO_AUDIO_DATA", "Received audio message but no audio_base_64 data")
                        
                        elif msg_type == "ping":
                            ping_event = msg.get("ping_event", {})
                            event_id = ping_event.get("event_id")
                            pong_message = {"type": "pong", "event_id": event_id}
                            await self.el_ws.send(json.dumps(pong_message))
                            await self.log_message("EL_PING", "PONG_SENT", f"Responded to ping with event_id: {event_id}")
                        
                        elif "audio" in msg and msg_type != "audio":
                            ws_state = self.mock_twilio_ws.client_state.name
                            await self.log_message("EL_LEGACY", "LEGACY_AUDIO", 
                                                 f"Legacy format audio, Twilio state: {ws_state}")
                            
                            try:
                                if ws_state != "CONNECTED":
                                    await self.log_message("EL_LEGACY", "STATE_CHECK_FAIL", 
                                                         f"Twilio not connected (state: {ws_state}), would CONTINUE")
                                    continue
                                
                                pcm16k = base64.b64decode(msg["audio"])
                                ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                                out = {"event": "media", "media": {"payload": ulaw_b64}}
                                
                                success = await self.mock_twilio_ws.send_text(json.dumps(out))
                                if success:
                                    await self.log_message("EL_LEGACY", "LEGACY_FORWARDED", 
                                                         f"✅ Successfully forwarded legacy audio")
                            
                            except Exception as e:
                                await self.log_message("EL_LEGACY", "LEGACY_ERROR", 
                                                     f"❌ Error processing legacy audio: {e}")
        
        except Exception as e:
            await self.log_message("DIAGNOSTIC", "PUMP_ERROR", f"Pump simulation error: {e}")
    
    async def generate_diagnosis_report(self):
        """Generate comprehensive diagnosis report"""
        print("\n" + "=" * 80)
        print("DIAGNOSIS REPORT")
        print("=" * 80)
        
        print(f"\n📊 STATISTICS:")
        print(f"   • Audio messages received from ElevenLabs: {self.audio_received_count}")
        print(f"   • Audio messages sent to Twilio: {self.audio_sent_count}")
        print(f"   • Total WebSocket messages logged: {len(self.message_log)}")
        
        print(f"\n🔍 MESSAGE FLOW ANALYSIS:")
        for entry in self.message_log:
            timestamp = entry["timestamp"]
            source = entry["source"]
            msg_type = entry["message_type"]
            details = entry["details"]
            print(f"   [{timestamp:.3f}] {source:15} | {msg_type:20} | {details}")
        
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        if self.audio_received_count == 0:
            print("   ❌ CRITICAL: No audio messages received from ElevenLabs")
            print("   🔧 RECOMMENDATION: Check ElevenLabs agent configuration and WebSocket authentication")
        elif self.audio_sent_count == 0:
            print("   ❌ CRITICAL: Audio received but not forwarded to Twilio")
            print("   🔧 RECOMMENDATION: Check WebSocket state management and error handling")
        elif self.audio_received_count != self.audio_sent_count:
            print(f"   ⚠️  WARNING: Audio loss detected ({self.audio_received_count} received, {self.audio_sent_count} sent)")
            print("   🔧 RECOMMENDATION: Check WebSocket state timing and error recovery")
        else:
            print("   ✅ SUCCESS: All audio messages successfully routed")
            print("   🔧 RECOMMENDATION: Issue may be in real Twilio WebSocket implementation")
        
        print(f"\n📋 NEXT STEPS:")
        print("   1. Run this diagnostic during an actual phone call")
        print("   2. Compare results with real Twilio WebSocket behavior")
        print("   3. Monitor Fly logs for WebSocket state changes during calls")
        print("   4. Test with different WebSocket state scenarios")
        
        return {
            "audio_received": self.audio_received_count,
            "audio_sent": self.audio_sent_count,
            "message_count": len(self.message_log),
            "success_rate": self.audio_sent_count / max(1, self.audio_received_count)
        }

async def main():
    """Run comprehensive audio routing diagnosis"""
    diagnostic = AudioRoutingDiagnostic()
    
    try:
        success = await diagnostic.test_elevenlabs_connection()
        
        if success:
            results = await diagnostic.generate_diagnosis_report()
            
            with open("/home/ubuntu/repos/mvp/bakame-backend/audio_diagnosis_log.json", "w") as f:
                json.dump({
                    "results": results,
                    "message_log": diagnostic.message_log,
                    "timestamp": time.time()
                }, f, indent=2)
            
            print(f"\n💾 Detailed log saved to: audio_diagnosis_log.json")
        
        else:
            print("❌ Diagnostic failed to complete")
    
    except KeyboardInterrupt:
        print("\n🛑 Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n💥 Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if diagnostic.el_ws:
            try:
                await diagnostic.el_ws.close()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
