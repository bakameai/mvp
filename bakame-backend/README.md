# BAKAME MVP - AI Learning Assistant

Comprehensive voice and SMS AI-powered learning assistant for feature phones, designed for emerging markets with focus on Rwanda. Features curriculum-based learning aligned with Bloom's Taxonomy, cultural integration, and pedagogically-sound educational content.

## 🎯 Overview

BAKAME transforms basic feature phones into powerful learning tools through AI-powered voice interactions. The system provides structured, culturally-aware education using Open Educational Resources (OER) and progressive learning methodologies.

## ✨ Key Features

### 🎓 Comprehensive Curriculum System
- **5 Specialized Learning Modules**: Grammar, Composition, Math, Debate, Comprehension
- **Bloom's Taxonomy Alignment**: 6 progressive stages per module (Remember → Create)
- **30 Curriculum Files**: Structured learning paths with clear progression
- **Cultural Integration**: Rwandan context throughout all content

### 🗣️ Voice-First Learning
- **Interactive Voice Lessons**: Phone call-based learning sessions
- **IVR-Optimized Prompts**: ≤10 second voice prompts for attention span
- **Accent-Tolerant Processing**: Designed for Rwandan English patterns
- **Emotion-Aware Responses**: Dynamic tone adjustment based on student progress

### 📚 Open Educational Resources (OER)
- **Grammar**: Speak English: 30 Days to Better English (Educational Use)
- **Composition**: Things Fall Apart by Chinua Achebe (Public Domain)
- **Math**: Secrets of Mental Math (Educational Use)
- **Debate**: Code of the Debater by Alfred Snider (Open Access)
- **Comprehension**: Art of Public Speaking (Public Domain)

### 🤖 AI-Powered Assessment
- **Multi-Factor Scoring**: Keyword (40%) + Structure (30%) + LLM (30%)
- **Adaptive Progression**: 3/5 passes → advance, 3 failures → support
- **Language Scaffolding**: Meaning-focused assessment with gentle grammar correction
- **Cultural Sensitivity**: Ubuntu philosophy integration in feedback

### 📊 Advanced Analytics
- **Student Progress Tracking**: Individual learning paths and advancement
- **Performance Analytics**: Detailed metrics and learning pattern analysis
- **Admin Dashboard**: Comprehensive management and monitoring tools
- **Real-time Insights**: Live session monitoring and intervention triggers

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for session management and user progression
- **AI Services**: Llama API (primary), OpenAI GPT-4 (fallback), ElevenLabs Conversational AI
- **Telephony**: Twilio Voice and SMS with Media Streams
- **Deployment**: Fly.io with auto-scaling

### Curriculum Structure
```
/docs/curriculum/
├── grammar/          # Technical language skills
│   ├── README.md     # Module overview and sources
│   ├── remember.md   # Basic grammar recognition
│   ├── understand.md # Grammar rule comprehension
│   ├── apply.md      # Grammar application
│   ├── analyze.md    # Error pattern analysis
│   ├── evaluate.md   # Grammar quality assessment
│   └── create.md     # Original sentence construction
├── composition/      # Creative writing and storytelling
├── math/            # Mental mathematics
├── debate/          # Critical thinking and argumentation
└── comprehension/   # Reading and communication skills
```

### RAG-Ready Content
- **Optimized Chunks**: <300 tokens per section for embedding
- **Clean Markdown**: Structured headers and consistent formatting
- **Semantic Organization**: Logical content flow for AI retrieval
- **Cross-References**: Clear relationships between modules and stages

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Poetry for dependency management
- PostgreSQL database
- Redis server
- Twilio account with phone number
- API keys: Llama, OpenAI, ElevenLabs

### Installation

1. **Clone and Setup**:
```bash
git clone https://github.com/bakameai/mvp.git
cd mvp/bakame-backend
poetry install
```

2. **Environment Configuration**:
```bash
cp .env.template .env
# Edit .env with your API keys and configuration
```

3. **Database Setup**:
```bash
# Database will be created automatically on startup
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Verify Installation**:
```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/admin/curriculum
```

## 📡 API Endpoints

### Core Endpoints
- **Voice Webhook**: `POST /webhook/call` - Twilio voice interactions
- **SMS Webhook**: `POST /webhook/sms` - Text-based learning
- **Media Stream**: `WS /webhook/media-stream` - Real-time audio processing
- **Health Check**: `GET /healthz` - Comprehensive system status

### Admin Dashboard
- **Curriculum**: `GET /admin/curriculum` - Complete curriculum structure
- **Student Progress**: `GET /admin/curriculum/student-progress` - Learning analytics
- **Statistics**: `GET /admin/stats` - System performance metrics
- **User Management**: `GET /admin/users` - Student administration

### Authentication
- **Login**: `POST /auth/login` - Admin authentication
- **Register**: `POST /auth/register` - User registration
- **Profile**: `GET /auth/profile` - User profile management

## 🎓 Learning Modules

### Grammar Module
**Focus**: Technical language instruction and error correction
- Verb tenses and subject-verb agreement
- Sentence structure and completeness
- Common grammar patterns in Rwandan English
- Progressive complexity from basic recognition to advanced construction

### Composition Module
**Focus**: Creative writing and cultural storytelling
- African storytelling traditions and narrative structure
- Creative expression and cultural context
- Character development and plot construction
- Ubuntu philosophy integration in creative work

### Math Module
**Focus**: Mental mathematics and practical applications
- Quick calculation techniques and shortcuts
- Number sense and pattern recognition
- Rwandan currency and market examples
- Real-world problem solving in local contexts

### Debate Module
**Focus**: Critical thinking and public speaking
- Logical argument construction and evaluation
- Evidence-based reasoning and analysis
- Respectful disagreement and dialogue
- Community decision-making and civic engagement

### Comprehension Module
**Focus**: Reading comprehension and communication
- Text analysis and interpretation skills
- Information processing and synthesis
- Critical reading and source evaluation
- Oral tradition and modern communication integration

## ⚙️ Configuration

### Environment Variables
```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number

# AI Services (Llama primary, OpenAI fallback)
LLAMA_API_KEY=your_llama_key
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# Database & Cache
DATABASE_URL=postgresql://user:pass@localhost/bakame
REDIS_URL=redis://localhost:6379

# Application Settings
SECRET_KEY=your_secret_key
DEBUG=false
USE_LLAMA=true
ENVIRONMENT=production
```

### Curriculum Customization
```python
# Module configuration in curriculum_service.py
MODULES = ["grammar", "composition", "math", "debate", "comprehension"]
BLOOM_STAGES = ["remember", "understand", "apply", "analyze", "evaluate", "create"]

# Assessment weights (customizable per module)
ASSESSMENT_WEIGHTS = {
    "keyword_matching": 0.4,
    "sentence_structure": 0.3,
    "llm_evaluation": 0.3
}
```

## 🧪 Development

### Testing
```bash
# Run curriculum system tests
poetry run python test_curriculum_restructure.py

# Run full test suite
poetry run pytest

# Test specific module
poetry run pytest tests/test_curriculum_service.py
```

### Code Quality
```bash
poetry run black .
poetry run isort .
poetry run flake8
```

### Local Development
```bash
# Start with hot reload
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test curriculum loading
curl http://localhost:8000/admin/curriculum

# Test voice webhook (requires Twilio setup)
curl -X POST http://localhost:8000/webhook/call \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=%2B250123456789&CallSid=test123&SpeechResult=I want to learn grammar"
```

## 🚀 Deployment

### Production Deployment (Fly.io)
```bash
# Deploy to production
fly deploy

# Check deployment status
fly status

# View logs
fly logs
```

### Environment Setup
```bash
# Set production secrets
fly secrets set TWILIO_ACCOUNT_SID=your_sid
fly secrets set LLAMA_API_KEY=your_key
fly secrets set DATABASE_URL=your_db_url

# Scale for production
fly scale count 2
fly scale memory 1024
```

### Health Monitoring
```bash
# Check system health
curl https://app-lfzepwvu.fly.dev/healthz

# Monitor curriculum system
curl https://app-lfzepwvu.fly.dev/admin/curriculum
```

## 📈 Performance & Monitoring

### Key Metrics
- **Response Time**: <2 seconds for voice interactions
- **Assessment Accuracy**: Multi-factor scoring with 60% pass threshold
- **Student Progression**: 3/5 success rate for advancement
- **System Uptime**: 99.9% availability with circuit breaker protection

### Analytics Dashboard
- Real-time student progress tracking
- Module-specific performance metrics
- Cultural adaptation effectiveness
- Learning pattern analysis and insights

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-module`
3. Implement changes with tests
4. Update documentation
5. Submit pull request with detailed description

### Adding New Modules
1. Create module folder: `/docs/curriculum/new_module/`
2. Add README.md with source attribution
3. Create 6 Bloom's taxonomy stage files
4. Update `curriculum_service.py` module list
5. Add module-specific assessment logic
6. Test with `test_curriculum_restructure.py`

### Content Guidelines
- All content must be culturally appropriate for Rwandan learners
- Voice prompts limited to ≤10 seconds for IVR compatibility
- Markdown sections optimized for <300 tokens (RAG-ready)
- Clear attribution for all OER sources
- Ubuntu philosophy integration where appropriate

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- **Migration Notes**: `/docs/MIGRATION_NOTES.md` - Complete change history
- **Curriculum Guide**: `/docs/CURRICULUM_GUIDE.md` - Comprehensive curriculum documentation
- **OER Sources**: `/docs/OER_SOURCES.md` - Educational resource documentation
- **System Architecture**: `/docs/system_architecture.md` - Technical overview

### Contact & Community
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact the BAKAME team for partnership inquiries
- **Documentation**: Comprehensive guides in `/docs/` directory

### Production Support
- **Health Monitoring**: `/healthz` endpoint for system status
- **Admin Dashboard**: Real-time monitoring and management
- **Error Tracking**: Comprehensive logging with PII redaction
- **Performance Metrics**: Detailed analytics and reporting

---

**BAKAME MVP** - Transforming education through AI-powered voice learning for emerging markets. Built with ❤️ for Rwanda and beyond.
