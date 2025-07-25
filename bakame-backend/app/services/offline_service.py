import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.services.redis_service import redis_service
from app.services.logging_service import logging_service

class OfflineService:
    """
    Phase 4: Offline-First Architecture Service
    Manages content caching, progressive sync, and offline capabilities for feature phones
    """
    
    def __init__(self):
        self.cache_duration = timedelta(hours=24)  # Content cache duration
        self.max_sms_length = 160  # Standard SMS length
        self.sync_queue_key = "offline_sync_queue"
        
    async def cache_content_for_offline(self, phone_number: str, module_name: str, content: Dict[str, Any]) -> bool:
        """Cache educational content for offline access via SMS"""
        try:
            cache_key = f"offline_content:{phone_number}:{module_name}"
            
            compressed_content = await self._compress_content_for_sms(content)
            
            cache_data = {
                "content": compressed_content,
                "cached_at": datetime.utcnow().isoformat(),
                "module": module_name,
                "phone": phone_number,
                "chunks": len(compressed_content)
            }
            
            redis_service.set_with_expiry(cache_key, json.dumps(cache_data), self.cache_duration.total_seconds())
            
            await logging_service.log_interaction(
                phone_number, "offline_cache", f"Cached {module_name} content for offline access"
            )
            
            return True
            
        except Exception as e:
            await logging_service.log_error(f"Failed to cache offline content: {str(e)}")
            return False
    
    async def get_offline_content(self, phone_number: str, module_name: str) -> Optional[List[str]]:
        """Retrieve cached content for offline delivery via SMS"""
        try:
            cache_key = f"offline_content:{phone_number}:{module_name}"
            cached_data = redis_service.get(cache_key)
            
            if not cached_data:
                return None
                
            cache_info = json.loads(cached_data)
            return cache_info.get("content", [])
            
        except Exception as e:
            await logging_service.log_error(f"Failed to retrieve offline content: {str(e)}")
            return None
    
    async def _compress_content_for_sms(self, content: Dict[str, Any]) -> List[str]:
        """Compress educational content into SMS-sized chunks"""
        try:
            if content.get("type") == "lesson":
                text = content.get("text", "")
                title = content.get("title", "")
                
                sms_content = f"📚 {title}\n\n{text}"
                
            elif content.get("type") == "quiz":
                question = content.get("question", "")
                options = content.get("options", [])
                
                sms_content = f"❓ {question}\n"
                for i, option in enumerate(options[:4], 1):
                    sms_content += f"{i}. {option}\n"
                sms_content += "Reply with number (1-4)"
                
            elif content.get("type") == "exercise":
                instruction = content.get("instruction", "")
                example = content.get("example", "")
                
                sms_content = f"✏️ Exercise\n{instruction}\n\nExample: {example}"
                
            else:
                sms_content = str(content.get("text", "Content available"))
            
            chunks = []
            while len(sms_content) > 0:
                if len(sms_content) <= self.max_sms_length:
                    chunks.append(sms_content)
                    break
                else:
                    break_point = sms_content.rfind(' ', 0, self.max_sms_length)
                    if break_point == -1:
                        break_point = self.max_sms_length
                    
                    chunk = sms_content[:break_point]
                    if len(chunks) == 0:
                        chunk = f"📱 Part 1/{((len(sms_content) // self.max_sms_length) + 1)}\n{chunk}"
                    else:
                        chunk = f"📱 Part {len(chunks)+1}\n{chunk}"
                    
                    chunks.append(chunk)
                    sms_content = sms_content[break_point:].strip()
            
            return chunks
            
        except Exception as e:
            await logging_service.log_error(f"Failed to compress content for SMS: {str(e)}")
            return [f"📚 Content available for {content.get('title', 'lesson')}. Reply 'GET' for details."]
    
    async def queue_for_sync(self, phone_number: str, action: str, data: Dict[str, Any]) -> bool:
        """Queue actions for sync when connection is available"""
        try:
            sync_item = {
                "phone_number": phone_number,
                "action": action,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "id": hashlib.md5(f"{phone_number}{action}{datetime.utcnow()}".encode()).hexdigest()[:8]
            }
            
            redis_service.list_push(self.sync_queue_key, json.dumps(sync_item))
            
            await logging_service.log_interaction(
                phone_number, "sync_queue", f"Queued {action} for sync"
            )
            
            return True
            
        except Exception as e:
            await logging_service.log_error(f"Failed to queue sync item: {str(e)}")
            return False
    
    async def process_sync_queue(self) -> int:
        """Process queued items when connection is available"""
        try:
            processed = 0
            
            while True:
                sync_item_json = redis_service.list_pop(self.sync_queue_key)
                if not sync_item_json:
                    break
                
                sync_item = json.loads(sync_item_json)
                
                success = await self._process_sync_item(sync_item)
                
                if success:
                    processed += 1
                    await logging_service.log_interaction(
                        sync_item["phone_number"], "sync_processed", 
                        f"Synced {sync_item['action']}"
                    )
                else:
                    redis_service.list_push(self.sync_queue_key, sync_item_json)
                    break
            
            return processed
            
        except Exception as e:
            await logging_service.log_error(f"Failed to process sync queue: {str(e)}")
            return 0
    
    async def _process_sync_item(self, sync_item: Dict[str, Any]) -> bool:
        """Process individual sync item"""
        try:
            action = sync_item["action"]
            phone_number = sync_item["phone_number"]
            data = sync_item["data"]
            
            if action == "progress_update":
                progress_key = f"progress:{phone_number}"
                current_progress = redis_service.get(progress_key) or "{}"
                progress_data = json.loads(current_progress)
                progress_data.update(data)
                redis_service.set(progress_key, json.dumps(progress_data))
                
            elif action == "assessment_result":
                result_key = f"assessment:{phone_number}:{data.get('module')}"
                redis_service.set(result_key, json.dumps(data))
                
            elif action == "content_request":
                await self.cache_content_for_offline(
                    phone_number, data.get("module"), data.get("content", {})
                )
                
            return True
            
        except Exception as e:
            await logging_service.log_error(f"Failed to process sync item: {str(e)}")
            return False
    
    async def check_offline_capability(self, phone_number: str) -> Dict[str, Any]:
        """Check user's offline learning capabilities and cached content"""
        try:
            cached_modules = []
            for module in ["math", "english", "comprehension", "debate", "general"]:
                cache_key = f"offline_content:{phone_number}:{module}"
                if redis_service.get(cache_key):
                    cached_modules.append(module)
            
            sync_queue_size = redis_service.list_length(self.sync_queue_key)
            
            last_sync_key = f"last_sync:{phone_number}"
            last_sync = redis_service.get(last_sync_key)
            
            return {
                "cached_modules": cached_modules,
                "pending_sync_items": sync_queue_size,
                "last_sync": last_sync,
                "offline_ready": len(cached_modules) > 0,
                "recommendations": await self._get_offline_recommendations(phone_number, cached_modules)
            }
            
        except Exception as e:
            await logging_service.log_error(f"Failed to check offline capability: {str(e)}")
            return {"offline_ready": False, "error": str(e)}
    
    async def _get_offline_recommendations(self, phone_number: str, cached_modules: List[str]) -> List[str]:
        """Get recommendations for offline learning"""
        recommendations = []
        
        if not cached_modules:
            recommendations.append("📱 Cache some lessons for offline learning! Reply 'CACHE MATH' to start.")
        
        if len(cached_modules) < 3:
            available = set(["math", "english", "comprehension", "debate", "general"]) - set(cached_modules)
            if available:
                recommendations.append(f"💡 Try caching {list(available)[0].title()} lessons too!")
        
        if "math" in cached_modules:
            recommendations.append("🔢 Practice math problems offline - no internet needed!")
        
        if "english" in cached_modules:
            recommendations.append("📖 Improve English skills with cached vocabulary lessons!")
        
        return recommendations

offline_service = OfflineService()
