import requests
from typing import List, Dict, Any
from app.config import settings
import random

class NewsAPIService:
    def __init__(self):
        self.api_key = settings.newsapi_key
        self.base_url = "https://eventregistry.org/api/v1/article/getArticles"
    
    async def get_trending_debate_topics(self, count: int = 5) -> List[str]:
        """Generate debate topics from trending news headlines using newsapi.ai"""
        try:
            print(f"DEBUG: NewsAPI.ai - API key: {self.api_key[:10]}...")
            print(f"DEBUG: NewsAPI.ai - Base URL: {self.base_url}")
            
            keywords = ["technology", "politics", "climate", "education", "healthcare", "economy"]
            all_headlines = []
            
            for keyword in keywords:
                print(f"DEBUG: NewsAPI.ai - Fetching keyword: {keyword}")
                
                payload = {
                    "action": "getArticles",
                    "keyword": keyword,
                    "articlesPage": 1,
                    "articlesCount": 10,
                    "articlesSortBy": "date",
                    "articlesSortByAsc": False,
                    "dataType": ["news"],
                    "forceMaxDataTimeWindow": 7,
                    "resultType": "articles",
                    "apiKey": self.api_key
                }
                
                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"DEBUG: NewsAPI.ai - Response status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", {}).get("results", [])
                    headlines = [article.get("title", "") for article in articles if article.get("title")]
                    print(f"DEBUG: NewsAPI.ai - Got {len(headlines)} headlines for {keyword}")
                    all_headlines.extend(headlines)
                else:
                    print(f"DEBUG: NewsAPI.ai - Error response: {response.text}")
            
            print(f"DEBUG: NewsAPI.ai - Total headlines: {len(all_headlines)}")
            debate_topics = self._convert_headlines_to_debate_topics(all_headlines)
            print(f"DEBUG: NewsAPI.ai - Generated topics: {len(debate_topics)}")
            
            if debate_topics:
                selected_topics = random.sample(debate_topics, min(count, len(debate_topics)))
                print(f"DEBUG: NewsAPI.ai - Selected topics: {selected_topics}")
                return selected_topics
            else:
                print("DEBUG: NewsAPI.ai - No topics generated, using fallback")
                return self._get_fallback_topics()
            
        except Exception as e:
            print(f"Error fetching trending topics from newsapi.ai: {e}")
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
