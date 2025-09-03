import asyncio
import random
from typing import Callable, Any
from functools import wraps

class RetryConfig:
    def __init__(self, max_retries: int = 2, base_delay: float = 0.2, max_delay: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

def with_retry(config: RetryConfig = None):
    """Decorator to add retry logic with exponential backoff"""
    if config is None:
        config = RetryConfig()
        
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        break
                        
                    delay = min(
                        config.base_delay * (2 ** attempt),
                        config.max_delay
                    )
                    jitter = random.uniform(0, delay * 0.1)
                    total_delay = delay + jitter
                    
                    print(f"Retry attempt {attempt + 1}/{config.max_retries} after {total_delay:.2f}s: {e}")
                    await asyncio.sleep(total_delay)
            
            raise last_exception
        return wrapper
    return decorator

def is_transient_error(error: Exception) -> bool:
    """Determine if an error is transient and worth retrying"""
    error_str = str(error).lower()
    transient_indicators = [
        'timeout', 'connection', 'network', 'temporary', 
        'rate limit', 'service unavailable', '503', '502', '504'
    ]
    return any(indicator in error_str for indicator in transient_indicators)
