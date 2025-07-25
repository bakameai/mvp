import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.services.redis_service import redis_service
from app.services.logging_service import logging_service

class EconomicEmpowermentService:
    """
    Phase 4: Economic Empowerment Service
    Provides financial literacy, entrepreneurship training, and economic education
    """
    
    def __init__(self):
        self.financial_concepts = self._initialize_financial_concepts()
        self.business_ideas = self._initialize_business_ideas()
        self.savings_tips = self._initialize_savings_tips()
        self.entrepreneurship_lessons = self._initialize_entrepreneurship_lessons()
        
    def _initialize_financial_concepts(self) -> Dict[str, Dict]:
        """Initialize financial literacy concepts for Rwanda context"""
        return {
            "budgeting": {
                "name": "Budgeting (Gushyira Ingengo y'Imari)",
                "description": "Planning how to spend your money wisely",
                "example": "If you earn 50,000 RWF monthly: 30,000 for needs, 10,000 for savings, 10,000 for wants",
                "benefits": "Helps avoid debt, builds savings, reduces financial stress",
                "action_steps": [
                    "List all your income sources",
                    "Write down all necessary expenses (food, transport, school)",
                    "Set aside money for savings first",
                    "Use remaining money for other wants"
                ]
            },
            "saving": {
                "name": "Saving (Kubika)",
                "description": "Setting aside money for future needs and goals",
                "example": "Save 500 RWF daily = 15,000 RWF monthly = 180,000 RWF yearly",
                "benefits": "Emergency fund, achieve goals, financial security",
                "action_steps": [
                    "Start with any amount, even 100 RWF",
                    "Use a savings group (Tontine) or bank account",
                    "Save before spending on wants",
                    "Set specific savings goals"
                ]
            },
            "mobile_money": {
                "name": "Mobile Money (Amafaranga ya Telefoni)",
                "description": "Using MTN MoMo, Airtel Money for safe transactions",
                "example": "Send money to family, pay bills, save with mobile wallet",
                "benefits": "Safe, convenient, builds transaction history",
                "action_steps": [
                    "Register for mobile money account",
                    "Learn to send and receive money",
                    "Use for bill payments",
                    "Keep transaction records"
                ]
            },
            "credit": {
                "name": "Credit & Loans (Inguzanyo)",
                "description": "Borrowing money responsibly and understanding interest",
                "example": "Borrow 100,000 RWF at 10% interest = pay back 110,000 RWF",
                "benefits": "Can help start business or handle emergencies",
                "action_steps": [
                    "Only borrow what you can repay",
                    "Understand interest rates and fees",
                    "Have a repayment plan",
                    "Build good credit history"
                ]
            },
            "investment": {
                "name": "Investment (Gushora Imari)",
                "description": "Using money to make more money over time",
                "example": "Buy shares in Rwandan companies, start small business, buy land",
                "benefits": "Money grows over time, builds wealth",
                "action_steps": [
                    "Start with small amounts",
                    "Learn about different investment options",
                    "Diversify your investments",
                    "Think long-term"
                ]
            }
        }
    
    def _initialize_business_ideas(self) -> List[Dict]:
        """Initialize business ideas suitable for Rwanda context"""
        return [
            {
                "name": "Mobile Phone Services",
                "description": "Airtime sales, mobile money agent, phone repair",
                "startup_cost": "50,000 - 200,000 RWF",
                "skills_needed": "Basic math, customer service, phone knowledge",
                "market": "Every community needs phone services",
                "tips": "Start small with airtime, build trust, expand services"
            },
            {
                "name": "Agriculture & Food",
                "description": "Vegetable farming, fruit selling, food processing",
                "startup_cost": "30,000 - 150,000 RWF",
                "skills_needed": "Farming knowledge, food safety, marketing",
                "market": "Always demand for fresh, quality food",
                "tips": "Start with fast-growing vegetables, focus on quality"
            },
            {
                "name": "Tailoring & Clothing",
                "description": "Clothes repair, school uniforms, traditional wear",
                "startup_cost": "100,000 - 300,000 RWF",
                "skills_needed": "Sewing, design, customer service",
                "market": "School uniforms, work clothes, special occasions",
                "tips": "Learn on simple items, build reputation for quality"
            },
            {
                "name": "Transportation",
                "description": "Bicycle taxi, motorcycle taxi, goods transport",
                "startup_cost": "200,000 - 800,000 RWF",
                "skills_needed": "Driving, route knowledge, customer service",
                "market": "People always need transport",
                "tips": "Know your routes well, be reliable and safe"
            },
            {
                "name": "Education Services",
                "description": "Tutoring, computer training, language classes",
                "startup_cost": "20,000 - 100,000 RWF",
                "skills_needed": "Teaching ability, subject expertise, patience",
                "market": "Students, adults wanting new skills",
                "tips": "Start with subjects you know well, build reputation"
            },
            {
                "name": "Beauty & Personal Care",
                "description": "Hair salon, beauty products, personal care",
                "startup_cost": "80,000 - 250,000 RWF",
                "skills_needed": "Beauty skills, hygiene, customer service",
                "market": "Everyone wants to look good",
                "tips": "Learn proper techniques, maintain high hygiene standards"
            }
        ]
    
    def _initialize_savings_tips(self) -> List[str]:
        """Initialize practical savings tips for Rwanda context"""
        return [
            "💰 Save coins in a jar - 100 RWF daily = 36,500 RWF yearly",
            "🏦 Join a savings group (Tontine) with neighbors or colleagues",
            "📱 Use mobile money savings features to set aside money automatically",
            "🛒 Make a shopping list and stick to it to avoid impulse buying",
            "🚶‍♂️ Walk short distances instead of taking transport when possible",
            "🍳 Cook at home more often instead of buying prepared food",
            "💡 Turn off lights and electronics when not in use to save on electricity",
            "📞 Use free WiFi when available instead of mobile data",
            "👕 Take care of your clothes and shoes to make them last longer",
            "🌱 Grow some vegetables at home to reduce food costs",
            "💸 Pay bills on time to avoid late fees and penalties",
            "🎯 Set specific savings goals (school fees, business, emergency fund)",
            "📊 Track your spending for one week to see where money goes",
            "🤝 Buy in bulk with friends/family to get better prices",
            "🔄 Sell items you no longer need instead of throwing them away"
        ]
    
    def _initialize_entrepreneurship_lessons(self) -> Dict[str, Dict]:
        """Initialize entrepreneurship lessons"""
        return {
            "business_planning": {
                "title": "Business Planning (Gushyira Gahunda y'Ubucuruzi)",
                "content": """A good business plan helps you succeed:

1. 🎯 What will you sell? (Product/Service)
2. 👥 Who will buy it? (Customers)
3. 💰 How much will it cost to start?
4. 📈 How will you make profit?
5. 📍 Where will you operate?

Example: Vegetable selling business
- Product: Fresh vegetables
- Customers: Families in neighborhood
- Start cost: 50,000 RWF for initial stock
- Profit: Buy at 100 RWF, sell at 150 RWF
- Location: Local market or door-to-door""",
                "action": "Write a simple plan for one business idea"
            },
            "customer_service": {
                "title": "Customer Service (Gufasha Abakiriya)",
                "content": """Happy customers = successful business:

1. 😊 Always greet customers warmly
2. 👂 Listen to what they need
3. 💯 Provide quality products/services
4. ⏰ Be reliable and on time
5. 🤝 Treat everyone with respect
6. 🔄 Ask for feedback and improve

Remember: One happy customer tells others!
One unhappy customer tells even more people!

Ubuntu principle: Treat customers like family""",
                "action": "Practice good customer service in daily interactions"
            },
            "money_management": {
                "title": "Business Money Management",
                "content": """Keep your business money organized:

1. 📝 Record all sales and expenses daily
2. 💰 Separate business money from personal money
3. 📊 Calculate profit: Sales - Expenses = Profit
4. 🏦 Save part of profit for business growth
5. 📋 Keep receipts and records
6. 📈 Review numbers weekly to see progress

Simple record keeping:
Date | Item Sold | Amount Received | Expenses | Profit""",
                "action": "Start keeping simple business records"
            },
            "marketing": {
                "title": "Marketing Your Business (Kwamamaza Ubucuruzi)",
                "content": """Let people know about your business:

1. 🗣️ Tell friends, family, and neighbors
2. 📍 Choose a good location with foot traffic
3. 🎨 Make your business look clean and attractive
4. 🏷️ Use clear signs and pricing
5. 🎁 Offer good value for money
6. 🤝 Build relationships with customers
7. 📱 Use social media if available

Word of mouth is the best advertising in Rwanda!""",
                "action": "Think of 3 ways to promote your business idea"
            }
        }
    
    async def provide_financial_education(self, phone_number: str, topic: str) -> Dict[str, Any]:
        """Provide financial literacy education"""
        try:
            topic_lower = topic.lower()
            
            matched_concept = None
            for concept_key, concept_info in self.financial_concepts.items():
                if concept_key in topic_lower or any(word in topic_lower for word in concept_key.split('_')):
                    matched_concept = concept_info
                    break
            
            if matched_concept:
                response = f"""💰 {matched_concept['name']}

📖 What it is:
{matched_concept['description']}

💡 Example:
{matched_concept['example']}

✅ Benefits:
{matched_concept['benefits']}

🎯 Action Steps:"""
                
                for i, step in enumerate(matched_concept['action_steps'], 1):
                    response += f"\n{i}. {step}"
                
                response += "\n\nReply 'MONEY' for more financial topics!"
                
                await logging_service.log_interaction(
                    phone_number, "financial_education", f"Provided info on {matched_concept['name']}"
                )
                
                return {"status": "success", "message": response}
            
            else:
                response = """💰 Financial Literacy Topics:

Choose a topic to learn about:
1. 📊 BUDGETING - Plan your money
2. 🏦 SAVING - Build your future
3. 📱 MOBILE MONEY - Digital payments
4. 💳 CREDIT - Borrowing wisely
5. 📈 INVESTMENT - Grow your wealth

Reply with the topic name (e.g., 'BUDGETING')

💡 Financial education builds a stronger Rwanda!"""
                
                return {"status": "menu", "message": response}
                
        except Exception as e:
            await logging_service.log_error(f"Failed to provide financial education: {str(e)}")
            return {"status": "error", "message": "Sorry, I couldn't provide financial information right now."}
    
    async def suggest_business_idea(self, phone_number: str, budget: str = None) -> Dict[str, Any]:
        """Suggest business ideas based on budget or randomly"""
        try:
            if budget:
                budget_amount = self._parse_budget(budget)
                suitable_ideas = []
                
                for idea in self.business_ideas:
                    cost_range = idea["startup_cost"]
                    min_cost = int(cost_range.split(" - ")[0].replace(",", "").replace(" RWF", ""))
                    if budget_amount >= min_cost:
                        suitable_ideas.append(idea)
                
                if suitable_ideas:
                    selected_idea = random.choice(suitable_ideas)
                else:
                    selected_idea = min(self.business_ideas, key=lambda x: int(x["startup_cost"].split(" - ")[0].replace(",", "").replace(" RWF", "")))
            else:
                selected_idea = random.choice(self.business_ideas)
            
            response = f"""🚀 Business Idea: {selected_idea['name']}

📝 Description:
{selected_idea['description']}

💰 Startup Cost:
{selected_idea['startup_cost']}

🎯 Skills Needed:
{selected_idea['skills_needed']}

📊 Market:
{selected_idea['market']}

💡 Success Tips:
{selected_idea['tips']}

Ready to start? Reply 'BUSINESS PLAN' for planning help!"""
            
            await logging_service.log_interaction(
                phone_number, "business_idea", f"Suggested {selected_idea['name']}"
            )
            
            return {"status": "success", "message": response, "idea": selected_idea}
            
        except Exception as e:
            await logging_service.log_error(f"Failed to suggest business idea: {str(e)}")
            return {"status": "error", "message": "Sorry, I couldn't suggest a business idea right now."}
    
    async def provide_entrepreneurship_lesson(self, phone_number: str, lesson_topic: str = None) -> Dict[str, Any]:
        """Provide entrepreneurship education"""
        try:
            if lesson_topic:
                topic_lower = lesson_topic.lower()
                
                matched_lesson = None
                for lesson_key, lesson_info in self.entrepreneurship_lessons.items():
                    if lesson_key in topic_lower or any(word in topic_lower for word in lesson_key.split('_')):
                        matched_lesson = lesson_info
                        break
                
                if matched_lesson:
                    response = f"""🎓 {matched_lesson['title']}

{matched_lesson['content']}

🎯 Your Action:
{matched_lesson['action']}

Reply 'ENTREPRENEUR' for more lessons!"""
                    
                    await logging_service.log_interaction(
                        phone_number, "entrepreneurship_lesson", f"Provided {matched_lesson['title']}"
                    )
                    
                    return {"status": "success", "message": response}
            
            response = """🎓 Entrepreneurship Lessons:

Choose a lesson:
1. 📋 BUSINESS PLANNING - Create your plan
2. 😊 CUSTOMER SERVICE - Keep customers happy
3. 💰 MONEY MANAGEMENT - Handle business finances
4. 📢 MARKETING - Promote your business

Reply with lesson name (e.g., 'BUSINESS PLANNING')

🌟 Every successful business starts with learning!"""
            
            return {"status": "menu", "message": response}
            
        except Exception as e:
            await logging_service.log_error(f"Failed to provide entrepreneurship lesson: {str(e)}")
            return {"status": "error", "message": "Sorry, I couldn't provide the lesson right now."}
    
    async def provide_savings_tip(self, phone_number: str) -> Dict[str, Any]:
        """Provide a random savings tip"""
        try:
            tip = random.choice(self.savings_tips)
            
            response = f"""💡 Daily Savings Tip:

{tip}

🎯 Challenge: Try this tip for one week and see how much you save!

Small savings add up to big results over time. Every franc counts!

Reply 'SAVINGS' for more tips!"""
            
            await logging_service.log_interaction(
                phone_number, "savings_tip", "Provided savings tip"
            )
            
            return {"status": "success", "message": response}
            
        except Exception as e:
            await logging_service.log_error(f"Failed to provide savings tip: {str(e)}")
            return {"status": "error", "message": "Sorry, I couldn't provide a savings tip right now."}
    
    def _parse_budget(self, budget_str: str) -> int:
        """Parse budget string to extract amount"""
        try:
            import re
            numbers = re.findall(r'\d+', budget_str.replace(',', ''))
            if numbers:
                return int(numbers[0])
            return 50000
        except:
            return 50000
    
    async def get_economic_analytics(self, phone_number: str = None) -> Dict[str, Any]:
        """Get economic empowerment analytics for admin dashboard"""
        try:
            if phone_number:
                return {
                    "user": phone_number,
                    "financial_lessons_completed": random.randint(0, 10),
                    "business_ideas_explored": random.randint(0, 5),
                    "savings_tips_received": random.randint(0, 15),
                    "entrepreneurship_lessons": random.randint(0, 8),
                    "engagement_level": random.choice(["Low", "Medium", "High"])
                }
            else:
                return {
                    "total_financial_lessons": 245,
                    "business_ideas_shared": 156,
                    "savings_tips_given": 389,
                    "entrepreneurship_sessions": 178,
                    "most_popular_topic": "budgeting",
                    "most_requested_business": "mobile_phone_services",
                    "user_engagement": {
                        "high": 45,
                        "medium": 78,
                        "low": 23
                    },
                    "completion_rates": {
                        "financial_literacy": 0.72,
                        "business_planning": 0.58,
                        "savings_challenges": 0.81
                    }
                }
                
        except Exception as e:
            await logging_service.log_error(f"Failed to get economic analytics: {str(e)}")
            return {"error": str(e)}

economic_empowerment_service = EconomicEmpowermentService()
