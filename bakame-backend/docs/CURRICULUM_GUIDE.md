# BAKAME Curriculum System - Complete Guide

## 📚 Overview

The BAKAME curriculum system represents a comprehensive educational framework designed specifically for voice-based learning in emerging markets. Built on pedagogical best practices and integrated with high-quality Open Educational Resources (OER), the system provides structured, culturally-aware learning experiences through feature phone interactions.

## 🎯 Pedagogical Foundation

### Bloom's Taxonomy Integration

The curriculum is structured around Bloom's Taxonomy, providing six progressive learning stages that build cognitive skills systematically:

1. **Remember** - Basic recall and recognition
2. **Understand** - Comprehension and explanation
3. **Apply** - Using knowledge in new situations
4. **Analyze** - Breaking down and examining relationships
5. **Evaluate** - Making judgments and assessments
6. **Create** - Producing original work and solutions

### Cultural Integration Principles

- **Ubuntu Philosophy**: Emphasis on community, interconnectedness, and collective learning
- **Rwandan Context**: Local examples, scenarios, and cultural references throughout
- **Oral Tradition**: Integration of storytelling and verbal communication patterns
- **Practical Application**: Real-world relevance to daily life in Rwanda

## 🏗️ Module Architecture

### Five Specialized Learning Domains

#### 1. Grammar Module
**Pedagogical Source**: "Speak English: 30 Days to Better English"
**License**: Educational Use
**Focus**: Technical language instruction and structural accuracy

**Learning Progression**:
- **Remember**: Basic grammar pattern recognition, verb tense identification
- **Understand**: Grammar rule comprehension, error explanation
- **Apply**: Correct grammar usage in new sentences
- **Analyze**: Grammar error analysis, pattern comparison
- **Evaluate**: Grammar quality assessment, style judgment
- **Create**: Original sentence construction with complex grammar

**Cultural Adaptations**:
- Common Rwandan English patterns and corrections
- Local context examples for grammar rules
- Gentle correction approach respecting cultural communication styles
- Integration with Kinyarwanda language patterns where appropriate

#### 2. Composition Module
**Pedagogical Source**: "Things Fall Apart" by Chinua Achebe
**License**: Public Domain
**Focus**: Creative writing and cultural storytelling

**Learning Progression**:
- **Remember**: Story element recognition, narrative vocabulary recall
- **Understand**: Narrative structure comprehension, character development
- **Apply**: Creative writing techniques in personal stories
- **Analyze**: Literary analysis, cultural theme examination
- **Evaluate**: Story quality assessment, cultural authenticity judgment
- **Create**: Original narrative creation with cultural elements

**Cultural Adaptations**:
- African storytelling traditions and techniques
- Ubuntu philosophy integration in character development
- Local folklore and oral tradition incorporation
- Community-centered narrative structures

#### 3. Math Module
**Pedagogical Source**: "Secrets of Mental Math"
**License**: Educational Use
**Focus**: Mental mathematics and practical problem-solving

**Learning Progression**:
- **Remember**: Basic number facts, mental math techniques recall
- **Understand**: Mathematical concepts comprehension, operation understanding
- **Apply**: Mental math application in new problems
- **Analyze**: Problem-solving strategy analysis, pattern recognition
- **Evaluate**: Solution method assessment, efficiency judgment
- **Create**: Original problem creation, new calculation strategies

**Cultural Adaptations**:
- Rwandan currency (RWF) examples and calculations
- Market scenarios and agricultural applications
- Community resource sharing problems
- Local business and entrepreneurship contexts

#### 4. Debate Module
**Pedagogical Source**: "Code of the Debater" by Alfred Snider
**License**: Open Access
**Focus**: Critical thinking and respectful argumentation

**Learning Progression**:
- **Remember**: Debate terminology, argument structure basics
- **Understand**: Logical reasoning comprehension, fallacy recognition
- **Apply**: Argument construction in new topics
- **Analyze**: Argument strength analysis, evidence evaluation
- **Evaluate**: Debate performance assessment, position judgment
- **Create**: Original argument development, debate strategy design

**Cultural Adaptations**:
- Rwandan social and political topics for practice
- Traditional conflict resolution and dialogue methods
- Community decision-making processes
- Respectful disagreement within cultural norms

#### 5. Comprehension Module
**Pedagogical Source**: "Art of Public Speaking"
**License**: Public Domain
**Focus**: Reading comprehension and communication skills

**Learning Progression**:
- **Remember**: Reading comprehension basics, text structure recognition
- **Understand**: Main idea identification, context comprehension
- **Apply**: Reading strategies in new texts
- **Analyze**: Text analysis, author intent examination
- **Evaluate**: Content quality assessment, source credibility judgment
- **Create**: Original text interpretation, summary creation

**Cultural Adaptations**:
- Rwandan literature and historical texts
- Oral tradition transcription and analysis
- Community communication patterns
- Information literacy in local contexts

## 📁 File Structure & Organization

### Curriculum Directory Structure
```
/docs/curriculum/
├── grammar/
│   ├── README.md           # Module overview and source attribution
│   ├── remember.md         # Basic grammar recognition stage
│   ├── understand.md       # Grammar rule comprehension stage
│   ├── apply.md           # Grammar application stage
│   ├── analyze.md         # Grammar analysis stage
│   ├── evaluate.md        # Grammar evaluation stage
│   └── create.md          # Grammar creation stage
├── composition/
│   ├── README.md
│   └── [6 Bloom's stages]
├── math/
│   ├── README.md
│   └── [6 Bloom's stages]
├── debate/
│   ├── README.md
│   └── [6 Bloom's stages]
└── comprehension/
    ├── README.md
    └── [6 Bloom's stages]
```

### Resource Directory Structure
```
/docs/resources/
├── grammar/
│   ├── README.md
│   └── speak_english_30_days.pdf
├── composition/
│   ├── README.md
│   └── things_fall_apart.pdf
├── math/
│   ├── README.md
│   └── secrets_mental_math.pdf
├── debate/
│   ├── README.md
│   └── code_of_debater.pdf
└── comprehension/
    ├── README.md
    └── art_of_public_speaking.pdf
```

## 📝 Curriculum File Template

Each curriculum stage file follows a standardized template optimized for both human readability and AI processing:

```markdown
# [Module] - [Stage] Stage (Bloom's Taxonomy)

## 🎯 Learning Goal
[Specific, measurable learning objective aligned with Bloom's stage]

## 📖 Source & Content
- **Primary Source**: [Book/Resource name]
- **Page/Chapter**: [Specific reference for content]
- **Supplementary**: [Additional context or adaptations]

## 🧩 Key Skills
[3-4 specific skills developed at this stage]

## 🗣️ Voice Prompts (≤10s each)
[5 IVR-friendly prompts designed for voice interaction]

## 🎤 Expected Student Responses
[Example responses and acceptable variations]

## ✅ Assessment Criteria (PASS/FAIL)
**PASS Requirements:**
[Specific criteria for successful completion]

**FAIL Indicators:**
[Clear patterns indicating need for additional support]

## 📊 Advancement Rules
[Progression logic: typically 3/5 passes → advance]
```

## 🎙️ IVR Optimization

### Voice Prompt Design Principles

**Length Constraints**:
- Maximum 10 seconds per prompt for attention span optimization
- Clear, simple sentence structures for TTS clarity
- Avoided complex punctuation that affects speech synthesis

**Cultural Sensitivity**:
- Language appropriate for Rwandan English patterns
- Respectful tone and encouraging feedback
- Integration of local expressions and communication styles

**Progressive Difficulty**:
- Scaffolded complexity across Bloom's stages
- Predictable interaction flows for voice UI
- Clear expectations for student responses

### Audio Considerations

**Technical Optimization**:
- Optimized for telephony audio quality (8kHz, μ-law encoding)
- Clear pronunciation guides for TTS systems
- Consistent pacing and rhythm across prompts

**Accessibility Features**:
- Multiple response formats accepted (voice, DTMF)
- Repeat options for unclear audio
- Graceful degradation for poor connection quality

## 🤖 RAG (Retrieval-Augmented Generation) Preparation

### Content Optimization

**Chunk Size Management**:
- All content sections optimized to <300 tokens
- Logical breaking points for semantic coherence
- Overlap strategies for context preservation

**Markdown Structure**:
- Consistent header hierarchy for parsing
- Clear section boundaries with emoji markers
- Structured lists and bullet points for extraction

**Metadata Integration**:
- Rich semantic tags for improved retrieval
- Cross-reference links between related concepts
- Difficulty level indicators for adaptive selection

### AI Integration Features

**Semantic Organization**:
- Logical content flow for better retrieval accuracy
- Clear relationships between modules and stages
- Contextual connections across learning domains

**Dynamic Content Selection**:
- Adaptive difficulty based on student performance
- Personalized content recommendations
- Cultural context matching for relevance

## 📊 Assessment System

### Multi-Factor Scoring

**Component Weights**:
- **Keyword Matching (40%)**: Content-specific term recognition
- **Sentence Structure (30%)**: Grammar and organization assessment
- **LLM Evaluation (30%)**: Contextual understanding and creativity

**Scoring Methodology**:
```python
def calculate_assessment_score(response, module, stage):
    keyword_score = assess_keywords(response, module, stage)
    structure_score = assess_structure(response)
    llm_score = llm_evaluate(response, module, stage)
    
    overall_score = (
        keyword_score * 0.4 +
        structure_score * 0.3 +
        llm_score * 0.3
    )
    
    return {
        'overall_score': overall_score,
        'is_pass': overall_score >= 0.6,
        'component_scores': {
            'keyword': keyword_score,
            'structure': structure_score,
            'llm': llm_score
        }
    }
```

### Progression Logic

**Advancement Rules**:
- **Promote to Next Stage**: 3 successful assessments out of last 5 attempts
- **Stay at Current Stage**: Less than 60% success rate
- **Provide Extra Support**: 3 consecutive failures trigger intervention

**Cultural Considerations**:
- Meaning prioritized over perfect grammar
- Cultural context considered in evaluation
- Encouraging feedback regardless of performance level

## 🌍 Cultural Integration Framework

### Ubuntu Philosophy Integration

**Core Principles**:
- "I am because we are" - community-centered learning
- Collective responsibility for learning success
- Interconnectedness of knowledge domains
- Respect for diverse perspectives and experiences

**Implementation Strategies**:
- Group learning scenarios in individual sessions
- Community problem-solving examples
- Collaborative storytelling techniques
- Shared cultural references and values

### Rwandan Context Adaptation

**Language Considerations**:
- Kinyarwanda influence on English patterns
- Common translation challenges addressed
- Local expressions and idioms incorporated
- Respectful code-switching acknowledgment

**Cultural Content**:
- Historical references and national pride
- Traditional values and modern applications
- Local geography and environmental context
- Economic and social development themes

## 🔧 Technical Implementation

### Service Layer Architecture

**Curriculum Service** (`curriculum_service.py`):
```python
class CurriculumService:
    def __init__(self):
        self.modules = ["grammar", "composition", "math", "debate", "comprehension"]
        self.bloom_stages = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        self.curriculum_data = self._load_curriculum_data()
    
    def _load_curriculum_data(self):
        """Load curriculum from nested folder structure"""
        curriculum = {}
        for module in self.modules:
            curriculum[module] = {}
            for stage in self.bloom_stages:
                file_path = f"/docs/curriculum/{module}/{stage}.md"
                curriculum[module][stage] = self._parse_curriculum_file(file_path)
        return curriculum
```

**Module Routing** (`english_module.py`):
```python
async def process_user_input(self, user_input, user_context):
    if any(word in user_input.lower() for word in ["grammar", "correct", "fix"]):
        return await self._grammar_tutoring(user_input, user_context, "grammar")
    elif any(word in user_input.lower() for word in ["story", "write", "create"]):
        return await self._composition_tutoring(user_input, user_context, "composition")
    else:
        return await self._general_english_support(user_input, user_context)
```

### Database Schema

**Student Progress Tracking**:
```sql
CREATE TABLE student_progress (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    module VARCHAR(50) NOT NULL,
    current_stage VARCHAR(20) NOT NULL,
    assessment_history JSONB,
    last_session TIMESTAMP,
    total_sessions INTEGER DEFAULT 0,
    advancement_count INTEGER DEFAULT 0
);
```

**Assessment Logging**:
```sql
CREATE TABLE assessment_logs (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    module VARCHAR(50) NOT NULL,
    stage VARCHAR(20) NOT NULL,
    user_input TEXT,
    assessment_score DECIMAL(3,2),
    component_scores JSONB,
    is_pass BOOLEAN,
    feedback TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

## 📈 Performance Monitoring

### Key Metrics

**Learning Effectiveness**:
- Student progression rates across modules
- Assessment score distributions by stage
- Cultural adaptation success indicators
- Engagement and retention metrics

**Technical Performance**:
- Response time for curriculum loading
- Assessment processing latency
- Voice prompt generation speed
- System availability and reliability

**Quality Assurance**:
- Content accuracy and cultural appropriateness
- Assessment fairness and consistency
- Student feedback and satisfaction
- Educational outcome achievement

### Analytics Dashboard

**Student Progress Visualization**:
- Individual learning paths and milestones
- Module completion rates and timelines
- Difficulty progression and adaptation
- Cultural context effectiveness

**System Performance Monitoring**:
- Real-time curriculum system health
- Assessment accuracy and reliability
- Content delivery optimization
- User experience quality metrics

## 🚀 Future Enhancements

### Planned Improvements

**Content Expansion**:
- Additional subject modules (Science, History, Civics)
- Advanced level content for continuing learners
- Specialized tracks for different age groups
- Professional development and skills training

**Technology Integration**:
- Advanced RAG implementation for dynamic content
- Multilingual support for local languages
- AI-powered content generation and adaptation
- Integration with formal education systems

**Cultural Adaptation**:
- Regional customization for different African contexts
- Community-driven content contributions
- Local educator collaboration and training
- Cultural competency assessment and improvement

### Research Opportunities

**Educational Research**:
- Learning effectiveness studies in voice-based education
- Cultural adaptation impact on learning outcomes
- Optimal progression pacing for different learner types
- Community learning vs. individual learning effectiveness

**Technical Research**:
- Voice recognition optimization for African accents
- Low-bandwidth content delivery optimization
- Offline learning capability development
- AI bias detection and mitigation in educational content

## 📚 Resources & References

### Educational Sources
- Bloom, B. S. (1956). Taxonomy of Educational Objectives
- Freire, P. (1970). Pedagogy of the Oppressed
- Vygotsky, L. S. (1978). Mind in Society
- Gardner, H. (1983). Frames of Mind: The Theory of Multiple Intelligences

### Cultural References
- Achebe, C. (1958). Things Fall Apart
- Ramose, M. B. (1999). African Philosophy through Ubuntu
- Nyerere, J. K. (1968). Education for Self-Reliance
- Wa Thiong'o, N. (1986). Decolonising the Mind

### Technical Documentation
- OpenAI API Documentation
- Twilio Voice API Reference
- FastAPI Framework Documentation
- PostgreSQL Performance Tuning Guide

---

This comprehensive curriculum guide serves as the foundation for understanding, implementing, and extending the BAKAME educational system. It represents a synthesis of pedagogical best practices, cultural sensitivity, and technical innovation designed to democratize quality education through accessible technology.
