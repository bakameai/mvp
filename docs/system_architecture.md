# BAKAME System Architecture

## High-Level System Architecture

```mermaid
graph TB
    subgraph "User Interface"
        Phone[Feature Phone Users]
        Admin[Admin Dashboard]
    end
    
    subgraph "Communication Layer"
        Twilio[Twilio Voice/SMS API]
    end
    
    subgraph "Core Application"
        Backend[FastAPI Backend<br/>Python Application]
        Frontend[React Admin Dashboard<br/>TypeScript]
    end
    
    subgraph "AI Services"
        Whisper[OpenAI Whisper<br/>Speech-to-Text]
        GPT[OpenAI GPT-3.5<br/>Conversation AI]
    end
    
    subgraph "Data Layer"
        Redis[Redis Cache<br/>Session Context]
        Supabase[Supabase PostgreSQL<br/>Persistent Storage]
    end
    
    subgraph "AI Processing"
        GPTAssistant[AI Learning Assistant<br/>Natural Conversation<br/>All Subjects]
    end
    
    Phone -->|Voice Calls| Twilio
    Phone -->|SMS Messages| Twilio
    Twilio -->|Webhooks| Backend
    Backend -->|API Calls| Whisper
    Backend -->|API Calls| GPT
    Backend -->|Session Data| Redis
    Backend -->|Analytics| Supabase
    Backend -->|AI Processing| GPTAssistant
    Admin -->|HTTP/HTTPS| Frontend
    Frontend -->|API Calls| Backend
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User as Feature Phone User
    participant Twilio as Twilio Service
    participant Backend as FastAPI Backend
    participant AI as OpenAI Services
    participant Cache as Redis Cache
    participant DB as Supabase DB
    participant Admin as Admin Dashboard
    
    User->>Twilio: Voice Call/SMS
    Twilio->>Backend: Webhook (audio/text)
    Backend->>AI: Speech-to-Text (Whisper)
    Backend->>Cache: Get conversation context
    Backend->>AI: Generate response (GPT-3.5)
    Backend->>Cache: Update conversation context
    Backend->>DB: Log session data
    Backend->>Twilio: Response (TwiML)
    Twilio->>User: Voice/SMS response
    
    Admin->>Backend: Request analytics
    Backend->>DB: Query session data
    Backend->>Admin: Return analytics data
```

## Infrastructure Components

### Core Services
- **FastAPI Backend**: Python-based REST API handling all business logic
- **React Admin Dashboard**: TypeScript frontend for analytics and management
- **Twilio Integration**: Voice and SMS communication gateway
- **OpenAI Services**: AI-powered speech processing and conversation

### Data Storage
- **Redis Cache**: Real-time session context and conversation memory
- **Supabase PostgreSQL**: Persistent storage for user sessions and analytics

### AI Processing
- **AI Learning Assistant**: Natural conversational AI for educational support across all subjects
- **Fresh Sessions**: Each call starts new without persistent memory
- **Simplified Architecture**: Direct GPT processing without module routing

### Deployment Infrastructure
- **Backend Hosting**: Fly.io cloud deployment
- **Frontend Hosting**: Static site deployment
- **Database**: Supabase managed PostgreSQL
- **Cache**: Redis cloud service
