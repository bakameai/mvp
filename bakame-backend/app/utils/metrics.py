import time
import asyncio
from typing import Dict, Any, Optional
from functools import wraps
from app.services.logging_service import logging_service

class MetricsCollector:
    def __init__(self):
        self.current_metrics = {}
    
    def start_timer(self, metric_name: str):
        """Start timing a metric"""
        self.current_metrics[f"{metric_name}_start"] = time.time()
    
    def end_timer(self, metric_name: str) -> float:
        """End timing a metric and return duration in milliseconds"""
        start_key = f"{metric_name}_start"
        if start_key in self.current_metrics:
            duration_ms = (time.time() - self.current_metrics[start_key]) * 1000
            self.current_metrics[f"{metric_name}_ms"] = round(duration_ms, 2)
            del self.current_metrics[start_key]
            return duration_ms
        return 0.0
    
    def set_metric(self, key: str, value: Any):
        """Set a metric value"""
        self.current_metrics[key] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        return self.current_metrics.copy()
    
    def clear(self):
        """Clear all metrics"""
        self.current_metrics.clear()

def track_metrics(func):
    """Decorator to track metrics for IVR interactions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        metrics = MetricsCollector()
        
        if 'metrics' not in kwargs:
            kwargs['metrics'] = metrics
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            metrics.set_metric('error', str(e))
            raise
        finally:
            if hasattr(kwargs.get('metrics'), 'current_metrics'):
                await log_turn_metrics(kwargs['metrics'].get_metrics())
    
    return wrapper

async def log_turn_metrics(metrics: Dict[str, Any]):
    """Log per-turn metrics to database and CSV"""
    pass
