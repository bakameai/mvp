import aiohttp
import asyncio
from typing import Dict, Any, Optional
from app.config import settings

class MCPClient:
    def __init__(self):
        self.mcp_base_url = getattr(settings, 'mcp_server_url', 'http://localhost:8001')
        
    async def get_student_profile(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get student profile and progress from MCP server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.mcp_base_url}/students/{phone_number}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"MCP get_student_profile failed: {response.status}")
                        return None
        except Exception as e:
            print(f"Error getting student profile: {e}")
            return None
    
    async def update_student_progress(self, phone_number: str, module: str, stage: str, score: float, is_pass: bool) -> bool:
        """Update student progress via MCP server"""
        try:
            payload = {
                "phone_number": phone_number,
                "module": module,
                "stage": stage,
                "score": score,
                "is_pass": is_pass
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_base_url}/students/{phone_number}/progress",
                    json=payload
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        print(f"MCP update_progress failed: {response.status}")
                        return False
        except Exception as e:
            print(f"Error updating student progress: {e}")
            return False
    
    async def log_evaluation(self, phone_number: str, module: str, stage: str, user_input: str, 
                           overall_score: float, is_pass: bool, emotional_state: str, feedback: str) -> bool:
        """Log evaluation result via MCP server"""
        try:
            payload = {
                "phone_number": phone_number,
                "module": module,
                "stage": stage,
                "user_input": user_input,
                "overall_score": overall_score,
                "is_pass": is_pass,
                "emotional_state": emotional_state,
                "feedback": feedback
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_base_url}/students/{phone_number}/evaluation",
                    json=payload
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        print(f"MCP log_evaluation failed: {response.status}")
                        return False
        except Exception as e:
            print(f"Error logging evaluation: {e}")
            return False

mcp_client = MCPClient()
