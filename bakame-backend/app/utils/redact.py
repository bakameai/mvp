import re
from typing import Dict, Any

class PIIRedactor:
    def __init__(self):
        self.phone_patterns = [
            r'\+\d{1,3}[-.\s]?\d{1,14}',  # International format
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # US format
            r'\b0\d{9}\b',  # Rwanda local format
            r'\+250[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{3}',  # Rwanda international
        ]
        
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ]
        
        self.compiled_phone_patterns = [re.compile(pattern) for pattern in self.phone_patterns]
        self.compiled_email_patterns = [re.compile(pattern) for pattern in self.email_patterns]
    
    def redact_text(self, text: str) -> str:
        """Redact PII from text content"""
        if not text:
            return text
            
        redacted = text
        
        for pattern in self.compiled_phone_patterns:
            redacted = pattern.sub('[PHONE_REDACTED]', redacted)
        
        for pattern in self.compiled_email_patterns:
            redacted = pattern.sub('[EMAIL_REDACTED]', redacted)
        
        return redacted
    
    def redact_dict(self, data: Dict[str, Any], preserve_keys: list = None) -> Dict[str, Any]:
        """Redact PII from dictionary values, preserving specified keys"""
        if preserve_keys is None:
            preserve_keys = ['phone_number', 'session_id', 'call_id']  # Keep for joining records
        
        redacted = {}
        for key, value in data.items():
            if key in preserve_keys:
                redacted[key] = value
            elif isinstance(value, str):
                redacted[key] = self.redact_text(value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_dict(value, preserve_keys)
            else:
                redacted[key] = value
        
        return redacted

pii_redactor = PIIRedactor()
