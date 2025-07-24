import requests
from typing import List, Dict, Any
from app.config import settings
import random

class NewsAPIService:
    def __init__(self):
        self.api_key = settings.newsapi_key
        self.base_url = "https://newsapi.org/v2"
    
    async def get_trending_debate_topics(self, count: int = 5) -> List[str]:
        """Generate debate topics from trending news headlines"""
        try:
            categories = ["general", "technology", "business", "health", "science"]
            all_headlines = []
            
            for category in categories:
                response = requests.get(
                    f"{self.base_url}/top-headlines",
                    params={
                        "apiKey": self.api_key,
                        "country": "us",
                        "category": category,
                        "pageSize": 10
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    headlines = [article["title"] for article in data.get("articles", [])]
                    all_headlines.extend(headlines)
            
            debate_topics = self._convert_headlines_to_debate_topics(all_headlines)
            return random.sample(debate_topics, min(count, len(debate_topics)))
            
        except Exception as e:
            print(f"Error fetching trending topics: {e}")
            return self._get_fallback_topics()
    
    def _convert_headlines_to_debate_topics(self, headlines: List[str]) -> List[str]:
        """Convert news headlines into debate-worthy questions"""
        debate_topics = []
        
        for headline in headlines:
            if "AI" in headline or "artificial intelligence" in headline.lower():
                debate_topics.append("Should artificial intelligence be regulated by governments?")
            elif "climate" in headline.lower() or "environment" in headline.lower():
                debate_topics.append("Is individual action or government policy more important for addressing climate change?")
            elif "social media" in headline.lower() or "facebook" in headline.lower() or "twitter" in headline.lower():
                debate_topics.append("Do social media platforms have too much influence on public opinion?")
            elif "education" in headline.lower() or "school" in headline.lower():
                debate_topics.append("Should education be completely free, including university?")
            elif "healthcare" in headline.lower() or "medical" in headline.lower():
                debate_topics.append("Should healthcare be a universal right or a market service?")
            elif "technology" in headline.lower() or "tech" in headline.lower():
                debate_topics.append("Is technology making us more connected or more isolated?")
            elif "work" in headline.lower() or "job" in headline.lower() or "employment" in headline.lower():
                debate_topics.append("Should there be a universal basic income?")
        
        return list(set(debate_topics))
    
    def _get_fallback_topics(self) -> List[str]:
        """Fallback topics if API fails"""
        return [
            "Should students be required to wear school uniforms?",
            "Is social media more helpful or harmful to society?",
            "Should homework be banned in elementary schools?",
            "Is it better to live in a city or in the countryside?",
            "Should everyone learn a second language?"
        ]

newsapi_service = NewsAPIService()
