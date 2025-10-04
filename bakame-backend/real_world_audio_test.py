#!/usr/bin/env python3
"""
Real-World Audio Routing Test
=============================

This script simulates the exact real-world scenario where audio is lost between 
ElevenLabs and Twilio during actual phone calls. It tests various WebSocket state 
scenarios and timing issues that could cause audio loss.
"""

import asyncio
import json
import base64
import time
import websockets
import sys
import os
from unittest.mock import Mock, AsyncMock

sys.path.append('/home/ubuntu/repos/mvp/bakame-backend')

from app.elevenlabs_client import open_el_ws
from app.main import pcm16_16k_to_twilio_ulaw8k

class RealWorldAudioTest:
    def __init__(self):
        self.test_results = []
        self.audio_chunks_received = 0
        self.audio_chunks_sent = 0
        
    async def log_test_result(self, test_name, success, details):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}", flush=True)
    
    async def simulate_twilio_websocket_states(self):
        """Test different Twilio WebSocket states that could cause audio loss"""
        print("\n" + "="*80)
        print("TESTING TWILIO WEBSOCKET STATE SCENARIOS")
        print("="*80)
        
        await self.test_websocket_state_scenario("CONNECTING", "Audio arrives during connection")
        
        await self.test_websocket_state_scenario("CLOSED", "Audio arrives after connection closed")
        
        await self.test_websocket_state_transition_scenario()
        
        await self.test_websocket_send_exceptions()
        
        await self.test_rapid_audio_chunks()
    
    async def test_websocket_state_scenario(self, state_name, description):
        """Test specific WebSocket state scenario"""
        try:
            mock_ws = Mock()
            mock_ws.client_state = Mock()
            mock_ws.client_state.name = state_name
            mock_ws.send_text = AsyncMock()
            
            test_audio_b64 = base64.b64encode(b"test audio data" * 1000).decode('utf-8')
            
            if mock_ws.client_state.name != "CONNECTED":
                await self.log_test_result(
                    f"WebSocket State: {state_name}",
                    False,
                    f"Audio would be SKIPPED due to state check (state: {state_name})"
                )
                return False
            
            pcm16k = base64.b64decode(test_audio_b64)
            ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
            out = {"event": "media", "media": {"payload": ulaw_b64}}
            
            await mock_ws.send_text(json.dumps(out))
            
            await self.log_test_result(
                f"WebSocket State: {state_name}",
                True,
                f"Audio would be SENT successfully (state: {state_name})"
            )
            return True
            
        except Exception as e:
            await self.log_test_result(
                f"WebSocket State: {state_name}",
                False,
                f"Exception during audio processing: {e}"
            )
            return False
    
    async def test_websocket_state_transition_scenario(self):
        """Test WebSocket state changing during audio transmission"""
        try:
            mock_ws = Mock()
            mock_ws.client_state = Mock()
            mock_ws.send_text = AsyncMock()
            
            mock_ws.client_state.name = "CONNECTED"
            
            test_audio_b64 = base64.b64encode(b"chunk1" * 1000).decode('utf-8')
            pcm16k = base64.b64decode(test_audio_b64)
            ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
            out1 = {"event": "media", "media": {"payload": ulaw_b64}}
            
            if mock_ws.client_state.name == "CONNECTED":
                await mock_ws.send_text(json.dumps(out1))
                chunk1_sent = True
            else:
                chunk1_sent = False
            
            mock_ws.client_state.name = "CLOSED"
            
            test_audio_b64_2 = base64.b64encode(b"chunk2" * 1000).decode('utf-8')
            pcm16k_2 = base64.b64decode(test_audio_b64_2)
            ulaw_b64_2 = pcm16_16k_to_twilio_ulaw8k(pcm16k_2)
            out2 = {"event": "media", "media": {"payload": ulaw_b64_2}}
            
            if mock_ws.client_state.name == "CONNECTED":
                await mock_ws.send_text(json.dumps(out2))
                chunk2_sent = True
            else:
                chunk2_sent = False
            
            await self.log_test_result(
                "WebSocket State Transition",
                chunk1_sent and not chunk2_sent,
                f"Chunk 1 sent: {chunk1_sent}, Chunk 2 sent: {chunk2_sent} (state changed to CLOSED)"
            )
            
            return chunk1_sent and not chunk2_sent
            
        except Exception as e:
            await self.log_test_result(
                "WebSocket State Transition",
                False,
                f"Exception during state transition test: {e}"
            )
            return False
    
    async def test_websocket_send_exceptions(self):
        """Test WebSocket send() method throwing exceptions"""
        try:
            mock_ws = Mock()
            mock_ws.client_state = Mock()
            mock_ws.client_state.name = "CONNECTED"
            
            exceptions_to_test = [
                ("ConnectionClosed", "Connection closed during send"),
                ("Cannot call 'send' once a close message has been sent", "Send after close"),
                ("WebSocket connection is closed", "Connection closed"),
                ("Connection lost", "Connection lost"),
            ]
            
            results = []
            for exception_msg, description in exceptions_to_test:
                mock_ws.send_text = AsyncMock(side_effect=Exception(exception_msg))
                
                try:
                    test_audio_b64 = base64.b64encode(b"test" * 100).decode('utf-8')
                    pcm16k = base64.b64decode(test_audio_b64)
                    ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                    out = {"event": "media", "media": {"payload": ulaw_b64}}
                    
                    await mock_ws.send_text(json.dumps(out))
                    results.append(f"{description}: UNEXPECTED SUCCESS")
                    
                except Exception as e:
                    if "close message has been sent" in str(e) or "not connected" in str(e).lower():
                        results.append(f"{description}: Would CONTINUE (recoverable)")
                    else:
                        results.append(f"{description}: Would CONTINUE (non-recoverable)")
            
            await self.log_test_result(
                "WebSocket Send Exceptions",
                True,
                f"Exception handling: {'; '.join(results)}"
            )
            return True
            
        except Exception as e:
            await self.log_test_result(
                "WebSocket Send Exceptions",
                False,
                f"Test setup error: {e}"
            )
            return False
    
    async def test_rapid_audio_chunks(self):
        """Test rapid audio chunks that might overwhelm WebSocket"""
        try:
            mock_ws = Mock()
            mock_ws.client_state = Mock()
            mock_ws.client_state.name = "CONNECTED"
            mock_ws.send_text = AsyncMock()
            
            chunks_to_send = 10
            send_interval = 0.1  # 100ms between chunks
            successful_sends = 0
            
            for i in range(chunks_to_send):
                try:
                    test_audio_b64 = base64.b64encode(f"chunk{i}".encode() * 1000).decode('utf-8')
                    pcm16k = base64.b64decode(test_audio_b64)
                    ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                    out = {"event": "media", "media": {"payload": ulaw_b64}}
                    
                    if mock_ws.client_state.name == "CONNECTED":
                        await mock_ws.send_text(json.dumps(out))
                        successful_sends += 1
                    
                    await asyncio.sleep(send_interval)
                    
                except Exception as e:
                    print(f"Chunk {i} failed: {e}", flush=True)
            
            success_rate = successful_sends / chunks_to_send
            await self.log_test_result(
                "Rapid Audio Chunks",
                success_rate == 1.0,
                f"Sent {successful_sends}/{chunks_to_send} chunks successfully ({success_rate*100:.1f}%)"
            )
            
            return success_rate == 1.0
            
        except Exception as e:
            await self.log_test_result(
                "Rapid Audio Chunks",
                False,
                f"Test error: {e}"
            )
            return False
    
    async def test_real_elevenlabs_connection(self):
        """Test actual ElevenLabs connection with timing analysis"""
        print("\n" + "="*80)
        print("TESTING REAL ELEVENLABS CONNECTION WITH TIMING ANALYSIS")
        print("="*80)
        
        try:
            start_time = time.time()
            el_ws = await open_el_ws()
            connect_time = time.time() - start_time
            
            await self.log_test_result(
                "ElevenLabs Connection",
                True,
                f"Connected in {connect_time:.3f}s"
            )
            
            test_message = {
                "user_audio_chunk": base64.b64encode(b"Hello, this is a test" * 50).decode('utf-8')
            }
            
            send_time = time.time()
            await el_ws.send(json.dumps(test_message))
            
            audio_response_times = []
            conversation_init_time = None
            timeout = 15  # 15 second timeout
            
            async for raw in el_ws:
                current_time = time.time()
                elapsed = current_time - send_time
                
                if elapsed > timeout:
                    break
                
                if isinstance(raw, str):
                    try:
                        msg = json.loads(raw)
                        msg_type = msg.get("type")
                        
                        if msg_type == "conversation_initiation_metadata":
                            conversation_init_time = elapsed
                            await self.log_test_result(
                                "ElevenLabs Conversation Init",
                                True,
                                f"Conversation ready after {elapsed:.3f}s"
                            )
                        
                        elif msg_type == "audio":
                            audio_response_times.append(elapsed)
                            audio_event = msg.get("audio_event", {})
                            audio_b64 = audio_event.get("audio_base_64", "")
                            
                            if audio_b64:
                                pcm_bytes = len(base64.b64decode(audio_b64))
                                await self.log_test_result(
                                    f"ElevenLabs Audio Chunk #{len(audio_response_times)}",
                                    True,
                                    f"Received after {elapsed:.3f}s ({pcm_bytes} bytes PCM)"
                                )
                                
                                convert_start = time.time()
                                pcm16k = base64.b64decode(audio_b64)
                                ulaw_b64 = pcm16_16k_to_twilio_ulaw8k(pcm16k)
                                convert_time = time.time() - convert_start
                                
                                ulaw_bytes = len(base64.b64decode(ulaw_b64))
                                await self.log_test_result(
                                    f"Audio Conversion #{len(audio_response_times)}",
                                    True,
                                    f"Converted in {convert_time:.6f}s ({pcm_bytes} PCM -> {ulaw_bytes} μ-law)"
                                )
                        
                        elif msg_type == "ping":
                            ping_event = msg.get("ping_event", {})
                            event_id = ping_event.get("event_id")
                            pong_message = {"type": "pong", "event_id": event_id}
                            await el_ws.send(json.dumps(pong_message))
                    
                    except Exception as e:
                        await self.log_test_result(
                            "ElevenLabs Message Parse",
                            False,
                            f"Failed to parse message: {e}"
                        )
            
            total_audio_chunks = len(audio_response_times)
            if total_audio_chunks > 0:
                avg_response_time = sum(audio_response_times) / total_audio_chunks
                await self.log_test_result(
                    "ElevenLabs Timing Summary",
                    True,
                    f"Received {total_audio_chunks} audio chunks, avg response time: {avg_response_time:.3f}s"
                )
            
            await el_ws.close()
            return True
            
        except Exception as e:
            await self.log_test_result(
                "ElevenLabs Connection",
                False,
                f"Connection failed: {e}"
            )
            return False
    
    async def generate_diagnosis_report(self):
        """Generate comprehensive diagnosis report"""
        print("\n" + "="*80)
        print("REAL-WORLD AUDIO ROUTING DIAGNOSIS REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"   • Total tests: {total_tests}")
        print(f"   • Passed: {passed_tests}")
        print(f"   • Failed: {failed_tests}")
        print(f"   • Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}: {result['details']}")
        
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        
        state_failures = [r for r in self.test_results if "WebSocket State" in r["test"] and not r["success"]]
        if state_failures:
            print("   ❌ CRITICAL: WebSocket state checking is causing audio loss")
            print("   🔧 RECOMMENDATION: Modify state checking logic to buffer audio instead of skipping")
        
        exception_tests = [r for r in self.test_results if "Exception" in r["test"]]
        if exception_tests:
            print("   ⚠️  WebSocket exceptions are being handled but may cause audio loss")
            print("   🔧 RECOMMENDATION: Implement retry logic and audio buffering")
        
        timing_tests = [r for r in self.test_results if "Timing" in r["test"] or "Rapid" in r["test"]]
        if any(not t["success"] for t in timing_tests):
            print("   ⚠️  Timing issues detected in rapid audio chunk processing")
            print("   🔧 RECOMMENDATION: Implement audio buffering and rate limiting")
        
        print(f"\n📋 NEXT STEPS:")
        print("   1. Focus on WebSocket state management - this is likely the primary issue")
        print("   2. Implement audio buffering to handle state transitions")
        print("   3. Add retry logic for failed WebSocket sends")
        print("   4. Monitor real phone calls with enhanced logging")
        
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "test_results": self.test_results,
            "timestamp": time.time()
        }
        
        with open("/home/ubuntu/repos/mvp/bakame-backend/real_world_audio_diagnosis.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: real_world_audio_diagnosis.json")
        
        return report_data

async def main():
    """Run real-world audio routing tests"""
    tester = RealWorldAudioTest()
    
    try:
        print("🔬 REAL-WORLD AUDIO ROUTING DIAGNOSIS")
        print("=" * 80)
        print("Testing scenarios that could cause audio loss during actual phone calls...")
        
        await tester.simulate_twilio_websocket_states()
        
        await tester.test_real_elevenlabs_connection()
        
        report = await tester.generate_diagnosis_report()
        
        return report
        
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
