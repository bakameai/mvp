import csv
import os
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.database import UserSession, ModuleUsage, get_db
from app.config import settings

class LoggingService:
    def __init__(self):
        self.csv_file_path = "user_sessions.csv"
        self._ensure_csv_headers()
    
    def _ensure_csv_headers(self):
        """Ensure CSV file exists with proper headers"""
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp', 'phone_number', 'session_id', 'module_name',
                    'interaction_type', 'user_input', 'ai_response', 'session_duration',
                    'emotional_data', 'gamification_data', 'call_id', 'turn', 
                    'asr_ms', 'llm_ms', 'tts_ms', 'total_ms', 'tokens_in', 
                    'tokens_out', 'asr_confidence', 'error'
                ])
    
    async def log_interaction(self, 
                            phone_number: str,
                            session_id: str,
                            module_name: str,
                            interaction_type: str,
                            user_input: str,
                            ai_response: str,
                            session_duration: float = None,
                            emotional_data: Dict[str, Any] = None,
                            gamification_data: Dict[str, Any] = None):
        """Log user interaction to both PostgreSQL and CSV"""
        
        timestamp = datetime.utcnow()
        
        try:
            db = next(get_db())
            
            session_record = UserSession(
                phone_number=phone_number,
                session_id=session_id,
                module_name=module_name,
                interaction_type=interaction_type,
                user_input=user_input,
                ai_response=ai_response,
                timestamp=timestamp,
                session_duration=session_duration
            )
            
            db.add(session_record)
            
            module_usage = db.query(ModuleUsage).filter(
                ModuleUsage.phone_number == phone_number,
                ModuleUsage.module_name == module_name
            ).first()
            
            if module_usage:
                module_usage.usage_count += 1
                module_usage.last_used = timestamp
                if session_duration:
                    module_usage.total_duration += session_duration
            else:
                module_usage = ModuleUsage(
                    phone_number=phone_number,
                    module_name=module_name,
                    usage_count=1,
                    last_used=timestamp,
                    total_duration=session_duration or 0.0
                )
                db.add(module_usage)
            
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"Error logging to PostgreSQL: {e}")
        
        try:
            from app.utils.redact import pii_redactor
            
            redacted_user_input = pii_redactor.redact_text(user_input)
            redacted_ai_response = pii_redactor.redact_text(ai_response)
            
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp.isoformat(),
                    phone_number,  # Keep for record joining
                    session_id,
                    module_name,
                    interaction_type,
                    redacted_user_input,
                    redacted_ai_response,
                    session_duration,
                    str(emotional_data) if emotional_data else "",
                    str(gamification_data) if gamification_data else "",
                    "",  # call_id
                    "",  # turn
                    "",  # asr_ms
                    "",  # llm_ms
                    "",  # tts_ms
                    "",  # total_ms
                    "",  # tokens_in
                    "",  # tokens_out
                    "",  # asr_confidence
                    ""   # error
                ])
        except Exception as e:
            print(f"Error logging to CSV: {e}")
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for admin dashboard"""
        try:
            db = next(get_db())
            
            total_sessions = db.query(UserSession).count()
            
            unique_users = db.query(UserSession.phone_number).distinct().count()
            
            module_stats = {}
            for module_usage in db.query(ModuleUsage).all():
                module_name = module_usage.module_name
                if module_name not in module_stats:
                    module_stats[module_name] = {
                        'total_usage': 0,
                        'unique_users': 0,
                        'total_duration': 0.0
                    }
                
                module_stats[module_name]['total_usage'] += module_usage.usage_count
                module_stats[module_name]['unique_users'] += 1
                module_stats[module_name]['total_duration'] += module_usage.total_duration
            
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_sessions = db.query(UserSession).filter(
                UserSession.timestamp >= yesterday
            ).count()
            
            db.close()
            
            return {
                'total_sessions': total_sessions,
                'unique_users': unique_users,
                'recent_sessions_24h': recent_sessions,
                'module_statistics': module_stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting usage statistics: {e}")
            return {
                'total_sessions': 0,
                'unique_users': 0,
                'recent_sessions_24h': 0,
                'module_statistics': {},
                'last_updated': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def export_csv_data(self) -> str:
        """Return path to CSV file for download"""
        return self.csv_file_path
    
    def get_user_sessions(self, phone_number: str = None, limit: int = 100) -> List[Dict]:
        """Get user sessions for admin dashboard"""
        try:
            db = next(get_db())
            
            query = db.query(UserSession)
            if phone_number:
                query = query.filter(UserSession.phone_number == phone_number)
            
            sessions = query.order_by(UserSession.timestamp.desc()).limit(limit).all()
            
            result = []
            for session in sessions:
                result.append({
                    'id': session.id,
                    'phone_number': session.phone_number,
                    'session_id': session.session_id,
                    'module_name': session.module_name,
                    'interaction_type': session.interaction_type,
                    'user_input': session.user_input,
                    'ai_response': session.ai_response,
                    'timestamp': session.timestamp.isoformat(),
                    'session_duration': session.session_duration
                })
            
            db.close()
            return result
            
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
    
    async def log_turn_metrics(self,
                              call_id: str,
                              turn: int,
                              phone_number: str,
                              asr_ms: float = 0,
                              llm_ms: float = 0,
                              tts_ms: float = 0,
                              tokens_in: int = 0,
                              tokens_out: int = 0,
                              asr_confidence: float = 0,
                              error: str = None):
        """Log per-turn metrics for observability"""
        
        timestamp = datetime.utcnow()
        total_ms = asr_ms + llm_ms + tts_ms
        
        try:
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp.isoformat(),
                    phone_number,
                    call_id,
                    "metrics",  # module_name
                    "turn_metrics",  # interaction_type
                    "",  # user_input
                    "",  # ai_response
                    total_ms / 1000,  # session_duration in seconds
                    "",  # emotional_data
                    "",  # gamification_data
                    call_id,
                    turn,
                    asr_ms,
                    llm_ms,
                    tts_ms,
                    total_ms,
                    tokens_in,
                    tokens_out,
                    asr_confidence,
                    error or ""
                ])
        except Exception as e:
            print(f"Error logging turn metrics: {e}")

logging_service = LoggingService()
