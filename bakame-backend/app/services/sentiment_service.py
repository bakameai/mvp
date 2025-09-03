import re
from typing import Dict, Literal, Optional
from dataclasses import dataclass

@dataclass
class SentimentResult:
    sentiment: Literal["calm", "engaged", "frustrated"]
    confidence: float
    indicators: list[str]

class SentimentService:
    def __init__(self):
        self.frustration_patterns = [
            r'\b(no|not|can\'t|cannot|don\'t|won\'t)\b',
            r'\b(difficult|hard|confusing|confused)\b',
            r'\b(help|stuck|lost|wrong)\b',
            r'\b(again|repeat|what)\b',
            r'\b(tired|frustrated|annoyed)\b'
        ]
        
        self.engagement_patterns = [
            r'\b(yes|okay|good|great|nice)\b',
            r'\b(understand|got it|makes sense)\b',
            r'\b(thank you|thanks|please)\b',
            r'\b(try|want|like|love)\b'
        ]
    
    def analyze_sentiment(self, 
                         transcript: str, 
                         speech_confidence: float = 1.0,
                         response_time: float = 0.0) -> SentimentResult:
        """
        Analyze sentiment from ASR transcript and speech metrics
        
        Args:
            transcript: The transcribed speech text
            speech_confidence: ASR confidence score (0.0-1.0)
            response_time: Time taken to respond (seconds)
        """
        transcript_lower = transcript.lower()
        indicators = []
        
        frustration_score = 0
        for pattern in self.frustration_patterns:
            matches = len(re.findall(pattern, transcript_lower))
            if matches > 0:
                frustration_score += matches
                indicators.append(f"frustration_pattern: {pattern}")
        
        engagement_score = 0
        for pattern in self.engagement_patterns:
            matches = len(re.findall(pattern, transcript_lower))
            if matches > 0:
                engagement_score += matches
                indicators.append(f"engagement_pattern: {pattern}")
        
        if speech_confidence < 0.6:
            frustration_score += 1
            indicators.append(f"low_speech_confidence: {speech_confidence}")
        
        if response_time < 1.0 and len(transcript.split()) < 3:
            frustration_score += 1
            indicators.append(f"quick_short_response: {response_time}s")
        
        if response_time > 8.0:
            frustration_score += 0.5
            indicators.append(f"long_pause: {response_time}s")
        
        if frustration_score >= 2:
            sentiment = "frustrated"
            confidence = min(0.9, 0.5 + (frustration_score * 0.1))
        elif engagement_score >= 2:
            sentiment = "engaged"
            confidence = min(0.9, 0.6 + (engagement_score * 0.1))
        else:
            sentiment = "calm"
            confidence = 0.7
        
        return SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            indicators=indicators
        )
    
    def get_encouraging_response(self, sentiment: str) -> str:
        """Get encouraging response based on detected sentiment"""
        if sentiment == "frustrated":
            return "That was a good try. Let's do it together. You're doing great — let's try once more."
        elif sentiment == "engaged":
            return "Excellent! You're really getting the hang of this."
        else:
            return "Good work! Let's continue."

sentiment_service = SentimentService()
