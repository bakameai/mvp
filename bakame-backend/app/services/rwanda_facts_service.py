import random
from typing import List

class RwandaFactsService:
    def __init__(self):
        self.facts = [
            "Did you know Rwanda is called the land of a thousand hills?",
            "Did you know Rwanda banned plastic bags in 2008?",
            "Did you know Rwanda has the cleanest capital city in Africa - Kigali?",
            "Did you know Rwanda plants millions of trees every year?",
            "Did you know Rwanda was the first country to have a majority female parliament?",
            "Did you know Rwanda uses drones to deliver medical supplies to remote areas?",
            "Did you know Rwanda has four official languages: Kinyarwanda, French, English, and Swahili?",
            "Did you know Rwanda celebrates Unity and Reconciliation Week every year?",
            "Did you know Rwanda has over 670 bird species?",
            "Did you know Rwanda's economy has grown by over 7% per year for the past decade?",
            "Did you know Rwanda is one of only three countries where you can see mountain gorillas?",
            "Did you know every last Saturday is Umuganda - national community service day?",
            "Did you know Rwanda aims to be carbon neutral by 2050?",
            "Did you know traditional Rwandan dance includes the famous Intore warrior dance?",
            "Did you know Rwanda is known for beautiful handwoven baskets called Agaseke?",
            "Did you know Rwanda has one of the fastest internet speeds in East Africa?",
            "Did you know mobile money is widely used in Rwanda?",
            "Did you know Rwanda has three national parks: Volcanoes, Akagera, and Nyungwe Forest?",
            "Did you know Lake Kivu is one of Africa's Great Lakes?",
            "Did you know Rwanda's national motto is Unity, Work, Progress?"
        ]
        
        self.used_facts = set()
    
    def get_random_fact(self) -> str:
        """Get a random Rwanda fact, avoiding recently used ones"""
        available_facts = [fact for fact in self.facts if fact not in self.used_facts]
        
        if not available_facts:
            self.used_facts.clear()
            available_facts = self.facts
        
        fact = random.choice(available_facts)
        self.used_facts.add(fact)
        
        return fact
    
    async def get_creative_fact(self, llama_service) -> str:
        """Get a creatively presented Rwanda fact using high temperature"""
        fact = self.get_random_fact()
        
        messages = [{"role": "user", "content": f"Present this Rwanda fact in a fun, engaging way for kids: {fact}"}]
        
        try:
            return await llama_service.generate_response(messages, "general", "rwanda_fact")
        except Exception as e:
            print(f"Error generating creative fact: {e}")
            return fact

rwanda_facts_service = RwandaFactsService()
