# BAKAME AI - Visual Architecture Diagrams

## 🏗️ System Architecture Diagram

```mermaid
graph TB
    subgraph "User Layer"
        U1[Feature Phone Users<br/>Voice Calls]
        U2[Feature Phone Users<br/>SMS Messages]
        U3[Web Admin Users<br/>Dashboard]
    end
    
    subgraph "Communication Layer"
        T1[Twilio Voice API]
        T2[Twilio SMS API]
        W1[Web Interface]
    end
    
    subgraph "API Gateway"
        F1[FastAPI Backend<br/>app-pyzfduqr.fly.dev]
    end
    
    subgraph "Learning Modules"
        M1[English Module<br/>Grammar, Pronunciation]
        M2[Math Module<br/>Mental Math, RWF Context]
        M3[Comprehension Module<br/>Stories, Q&A]
        M4[Debate Module<br/>Critical Thinking]
        M5[General Module<br/>Entry Point, Routing]
    end
    
    subgraph "AI Processing"
        A1[OpenAI GPT-4o-mini<br/>Text Generation]
        A2[OpenAI Whisper<br/>Speech-to-Text]
        A3[Llama LLM<br/>Alternative AI]
        A4[Deepgram<br/>Alternative STT]
    end
    
    subgraph "Data Layer"
        D1[PostgreSQL<br/>User Data, Sessions]
        D2[Redis<br/>Session Management]
        D3[File System<br/>Audio, Logs]
    end
    
    subgraph "Advanced Services"
        S1[Emotional Intelligence]
        S2[Gamification Engine]
        S3[Predictive Analytics]
        S4[Community Features]
        S5[Teacher Dashboard]
    end
    
    U1 --> T1
    U2 --> T2
    U3 --> W1
    
    T1 --> F1
    T2 --> F1
    W1 --> F1
    
    F1 --> M1
    F1 --> M2
    F1 --> M3
    F1 --> M4
    F1 --> M5
    
    M1 --> A1
    M2 --> A1
    M3 --> A1
    M4 --> A1
    M5 --> A1
    
    F1 --> A2
    F1 --> A3
    F1 --> A4
    
    F1 --> D1
    F1 --> D2
    F1 --> D3
    
    F1 --> S1
    F1 --> S2
    F1 --> S3
    F1 --> S4
    F1 --> S5
    
    style U1 fill:#e1f5fe
    style U2 fill:#e1f5fe
    style U3 fill:#e1f5fe
    style F1 fill:#f3e5f5
    style A1 fill:#fff3e0
    style A2 fill:#fff3e0
    style D1 fill:#e8f5e8
    style D2 fill:#e8f5e8
```

## 🔄 Data Flow Architecture

```mermaid
sequenceDiagram
    participant User as Feature Phone User
    participant Twilio as Twilio API
    participant API as FastAPI Backend
    participant Redis as Redis Cache
    participant AI as OpenAI/Llama
    participant DB as PostgreSQL
    participant Module as Learning Module
    
    User->>Twilio: Voice Call/SMS
    Twilio->>API: Webhook Request
    API->>Redis: Get User Context
    Redis-->>API: User Session Data
    
    alt Voice Call
        API->>AI: Transcribe Audio (Whisper)
        AI-->>API: Text Input
    end
    
    API->>Module: Process Learning Input
    Module->>AI: Generate Educational Response
    AI-->>Module: AI Response
    Module-->>API: Formatted Response
    
    API->>Redis: Update Session Context
    API->>DB: Log Interaction
    API->>Twilio: TwiML Response
    Twilio->>User: Voice/SMS Response
```

## 🎓 Learning Module Flow

```mermaid
flowchart TD
    A[User Input] --> B{Input Type?}
    B -->|Voice| C[Whisper STT]
    B -->|SMS| D[Direct Text]
    
    C --> E[Text Processing]
    D --> E
    
    E --> F{Module Detection}
    F -->|english| G[English Module]
    F -->|math| H[Math Module]
    F -->|comprehension| I[Comprehension Module]
    F -->|debate| J[Debate Module]
    F -->|general| K[General Module]
    
    G --> L[Grammar/Pronunciation Processing]
    H --> M[Math Problem Generation]
    I --> N[Story Generation/Analysis]
    J --> O[Debate Topic Processing]
    K --> P[General Q&A/Routing]
    
    L --> Q[AI Response Generation]
    M --> Q
    N --> Q
    O --> Q
    P --> Q
    
    Q --> R[Cultural Context Integration]
    R --> S[Emotional Intelligence]
    S --> T[Gamification Updates]
    T --> U[Response Formatting]
    
    U --> V{Output Type?}
    V -->|Voice| W[TwiML Voice Response]
    V -->|SMS| X[TwiML SMS Response]
    
    W --> Y[User Receives Audio]
    X --> Z[User Receives Text]
    
    style A fill:#e3f2fd
    style Q fill:#fff3e0
    style R fill:#f1f8e9
    style S fill:#fce4ec
    style T fill:#e8eaf6
```

## 🧠 AI Processing Pipeline

```mermaid
graph LR
    subgraph "Input Processing"
        I1[Voice Input] --> STT[Speech-to-Text<br/>Whisper/Deepgram]
        I2[SMS Input] --> TXT[Text Input]
        STT --> TXT
    end
    
    subgraph "Context Management"
        TXT --> CTX[Context Retrieval<br/>Redis Session]
        CTX --> HIST[Conversation History]
        CTX --> STATE[User State]
    end
    
    subgraph "Module Processing"
        HIST --> MOD[Module Selection<br/>English/Math/etc.]
        STATE --> MOD
        MOD --> LOGIC[Module Logic<br/>Educational Processing]
    end
    
    subgraph "AI Generation"
        LOGIC --> PROMPT[Prompt Engineering<br/>Cultural Context]
        PROMPT --> LLM[LLM Processing<br/>GPT-4o-mini/Llama]
        LLM --> RESP[AI Response]
    end
    
    subgraph "Enhancement Services"
        RESP --> EMO[Emotional Intelligence<br/>Mood Detection]
        EMO --> GAM[Gamification<br/>Points/Achievements]
        GAM --> CULT[Cultural Adaptation<br/>Kinyarwanda Integration]
    end
    
    subgraph "Output Generation"
        CULT --> FMT[Response Formatting]
        FMT --> VOICE[TwiML Voice]
        FMT --> SMS[TwiML SMS]
    end
    
    style STT fill:#ffecb3
    style LLM fill:#ffecb3
    style EMO fill:#f8bbd9
    style GAM fill:#c8e6c9
    style CULT fill:#dcedc8
```

## 🏢 Database Schema Visualization

```mermaid
erDiagram
    USERS {
        int id PK
        string phone_number UK
        string user_type
        string name
        string region
        string school
        string grade_level
        boolean is_active
        datetime created_at
        datetime last_active
        int total_points
        string current_level
    }
    
    USER_SESSIONS {
        int id PK
        string phone_number FK
        string session_id
        string module_name
        string interaction_type
        text user_input
        text ai_response
        datetime timestamp
        float session_duration
    }
    
    MODULE_USAGE {
        int id PK
        string phone_number FK
        string module_name
        int usage_count
        datetime last_used
        float total_duration
    }
    
    LEARNING_GROUPS {
        int id PK
        string name
        text description
        string group_type
        string region
        string school
        string grade_level
        string subject
        string teacher_phone FK
        boolean is_active
        datetime created_at
        int max_members
    }
    
    GROUP_MEMBERSHIPS {
        int id PK
        int group_id FK
        string user_phone FK
        string role
        datetime joined_at
        boolean is_active
    }
    
    PEER_CONNECTIONS {
        int id PK
        string user1_phone FK
        string user2_phone FK
        string connection_type
        string status
        datetime created_at
        datetime last_interaction
    }
    
    PEER_LEARNING_SESSIONS {
        int id PK
        string session_id UK
        int group_id FK
        int connection_id FK
        string module_name
        string topic
        text participants
        datetime started_at
        datetime ended_at
        text session_summary
    }
    
    WEB_USERS {
        int id PK
        string email UK
        string full_name
        string hashed_password
        string role
        string organization
        boolean is_active
        datetime created_at
    }
    
    USERS ||--o{ USER_SESSIONS : "has sessions"
    USERS ||--o{ MODULE_USAGE : "uses modules"
    USERS ||--o{ GROUP_MEMBERSHIPS : "joins groups"
    USERS ||--o{ PEER_CONNECTIONS : "connects with"
    LEARNING_GROUPS ||--o{ GROUP_MEMBERSHIPS : "contains members"
    LEARNING_GROUPS ||--o{ PEER_LEARNING_SESSIONS : "hosts sessions"
    PEER_CONNECTIONS ||--o{ PEER_LEARNING_SESSIONS : "enables sessions"
```

## 🌐 Deployment Architecture

```mermaid
graph TB
    subgraph "External Services"
        EXT1[Twilio<br/>Voice/SMS API]
        EXT2[OpenAI<br/>GPT + Whisper]
        EXT3[Llama API<br/>Alternative LLM]
        EXT4[NewsAPI<br/>Current Events]
        EXT5[Deepgram<br/>Alternative STT]
    end
    
    subgraph "Cloud Infrastructure"
        subgraph "Fly.io Platform"
            APP[FastAPI Backend<br/>app-pyzfduqr.fly.dev]
            DB[PostgreSQL<br/>Database]
        end
        
        subgraph "Devin Apps Platform"
            ADMIN[Admin Dashboard<br/>project-handling-app-jiwikt4q.devinapps.com]
        end
        
        subgraph "Redis Cloud"
            REDIS[Redis Cache<br/>Session Management]
        end
    end
    
    subgraph "User Access Points"
        PHONE[Feature Phones<br/>Voice/SMS]
        WEB[Web Browsers<br/>Admin Interface]
    end
    
    PHONE --> EXT1
    EXT1 --> APP
    WEB --> ADMIN
    ADMIN --> APP
    
    APP --> DB
    APP --> REDIS
    APP --> EXT2
    APP --> EXT3
    APP --> EXT4
    APP --> EXT5
    
    style APP fill:#e1f5fe
    style ADMIN fill:#f3e5f5
    style DB fill:#e8f5e8
    style REDIS fill:#ffecb3
    style EXT1 fill:#fff3e0
    style EXT2 fill:#fff3e0
```

## 🎮 Gamification System Architecture

```mermaid
mindmap
  root((Gamification Engine))
    Achievement System
      Ubuntu Spirit
        Community values
        Helping others
      Hill Climber
        Overcoming challenges
        Persistence
      Knowledge Seeker
        Learning streaks
        Curiosity
      Unity Builder
        Respectful debate
        Collaboration
      Subject Masters
        Math Champion
        Story Master
        English Explorer
        Resilience Warrior
    
    Progress Tracking
      Point System
        Module completion
        Correct answers
        Engagement time
      Level Progression
        Beginner
        Learner
        Achiever
        Expert
        Master
      Difficulty Adaptation
        Performance-based
        Automatic scaling
        Cultural context
    
    Cultural Integration
      Rwanda Context
        RWF calculations
        Local geography
        Community values
      Kinyarwanda Phrases
        Motivational messages
        Cultural greetings
        Success celebrations
      Ubuntu Philosophy
        Community support
        Shared learning
        Collective growth
```

## 🔒 Security Architecture

```mermaid
graph TD
    subgraph "User Authentication"
        A1[Phone-Based Identity<br/>No Registration Required]
        A2[Web Admin Authentication<br/>JWT + Role-Based Access]
    end
    
    subgraph "Data Protection"
        B1[HTTPS/TLS Encryption<br/>All Communications]
        B2[Database Encryption<br/>Sensitive Data Protection]
        B3[Session TTL Management<br/>Automatic Cleanup]
    end
    
    subgraph "Access Control"
        C1[Role-Based Permissions<br/>Admin/Super Admin]
        C2[Organization Isolation<br/>Multi-Tenant Support]
        C3[API Rate Limiting<br/>Abuse Prevention]
    end
    
    subgraph "Privacy Compliance"
        D1[Data Minimization<br/>Only Necessary Data]
        D2[User Consent<br/>Transparent Processing]
        D3[Data Export/Deletion<br/>User Rights]
    end
    
    A1 --> B1
    A2 --> B1
    B1 --> C1
    B2 --> C2
    B3 --> C3
    C1 --> D1
    C2 --> D2
    C3 --> D3
    
    style A1 fill:#e3f2fd
    style A2 fill:#e3f2fd
    style B1 fill:#f1f8e9
    style B2 fill:#f1f8e9
    style B3 fill:#f1f8e9
    style C1 fill:#fff3e0
    style C2 fill:#fff3e0
    style C3 fill:#fff3e0
    style D1 fill:#fce4ec
    style D2 fill:#fce4ec
    style D3 fill:#fce4ec
```

## 📊 Analytics & Monitoring Flow

```mermaid
graph LR
    subgraph "Data Collection"
        DC1[User Interactions<br/>Voice/SMS Logs]
        DC2[Module Usage<br/>Learning Analytics]
        DC3[Performance Metrics<br/>Response Times]
        DC4[Error Tracking<br/>System Health]
    end
    
    subgraph "Processing"
        P1[Real-time Analytics<br/>Live Dashboard]
        P2[Batch Processing<br/>Historical Analysis]
        P3[Predictive Models<br/>Learning Patterns]
    end
    
    subgraph "Storage"
        S1[PostgreSQL<br/>Structured Data]
        S2[Redis<br/>Real-time Cache]
        S3[File System<br/>Logs & Audio]
    end
    
    subgraph "Visualization"
        V1[Admin Dashboard<br/>Usage Statistics]
        V2[Teacher Portal<br/>Student Progress]
        V3[Export Tools<br/>CSV Reports]
    end
    
    DC1 --> P1
    DC2 --> P2
    DC3 --> P1
    DC4 --> P1
    
    P1 --> S2
    P2 --> S1
    P3 --> S1
    
    S1 --> V1
    S2 --> V1
    S1 --> V2
    S1 --> V3
    
    style DC1 fill:#e3f2fd
    style DC2 fill:#e3f2fd
    style P1 fill:#fff3e0
    style P2 fill:#fff3e0
    style P3 fill:#fff3e0
    style V1 fill:#f1f8e9
    style V2 fill:#f1f8e9
    style V3 fill:#f1f8e9
```

---

**Diagram Version:** 1.0  
**Last Updated:** September 6, 2025  
**Status:** Complete Architecture Visualization  
**Tools:** Mermaid.js for dynamic diagrams
