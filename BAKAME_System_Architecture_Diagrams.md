# BAKAME AI - System Architecture Diagrams

## Overall System Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        P[📱 Phone Calls]
        S[📱 SMS Messages]
        W[🌐 Web Frontend]
        A[⚙️ Admin Dashboard]
    end
    
    subgraph "External Services"
        T[Twilio<br/>Voice/SMS Gateway]
        E[ElevenLabs<br/>ConvAI Engine]
        O[OpenAI<br/>GPT-4]
        R[Redis<br/>Cache Layer]
        DB[PostgreSQL<br/>Database]
    end
    
    subgraph "BAKAME Backend (FastAPI)"
        WS[WebSocket Bridge<br/>Audio Processing]
        API[REST API<br/>Core Services]
        
        subgraph "Services Layer"
            S1[OpenAI Service]
            S2[Twilio Service]
            S3[Redis Service]
            S4[ElevenLabs Service]
            S5[Logging Service]
            S6[Emotional Intelligence]
            S7[Gamification Service]
            S8[Multimodal Service]
            S9[Offline Service]
            S10[Deepgram Service]
            S11[LLaMA Service]
            S12[Audio Service]
            S13[SMS Service]
            S14[Voice Service]
            S15[Analytics Service]
            S16[Security Service]
            S17[Notification Service]
            S18[Content Service]
        end
        
        subgraph "Learning Modules"
            M1[English Module]
            M2[Math Module]
            M3[Comprehension Module]
            M4[Debate Module]
            M5[General Module]
        end
    end
    
    subgraph "Frontend Applications"
        F[React Frontend<br/>Vite + TypeScript]
        AD[Admin Dashboard<br/>React + TypeScript]
    end
    
    %% User Interface Connections
    P --> T
    S --> T
    
    %% External Service Connections
    T --> WS
    T --> API
    WS --> E
    API --> O
    API --> R
    API --> DB
    
    %% Frontend Connections
    W --> F
    A --> AD
    F --> API
    AD --> API
    
    %% Internal Service Connections
    API --> S1
    API --> S2
    API --> S3
    API --> S4
    API --> S5
    API --> S6
    API --> S7
    API --> S8
    API --> S9
    API --> S10
    API --> S11
    API --> S12
    API --> S13
    API --> S14
    API --> S15
    API --> S16
    API --> S17
    API --> S18
    
    %% Module Connections
    API --> M1
    API --> M2
    API --> M3
    API --> M4
    API --> M5
    
    %% Styling
    classDef userInterface fill:#e1f5fe
    classDef external fill:#f3e5f5
    classDef backend fill:#e8f5e8
    classDef frontend fill:#fff3e0
    
    class P,S,W,A userInterface
    class T,E,O,R,DB external
    class WS,API,S1,S2,S3,S4,S5,S6,S7,S8,S9,S10,S11,S12,S13,S14,S15,S16,S17,S18,M1,M2,M3,M4,M5 backend
    class F,AD frontend
```

## Enhanced Audio Processing Pipeline

```mermaid
sequenceDiagram
    participant C as 📞 Caller
    participant T as Twilio<br/>Gateway
    participant WS as WebSocket<br/>Bridge
    participant E as ElevenLabs<br/>ConvAI
    participant B as Audio<br/>Buffer
    
    Note over C,E: Call Initiation & Setup
    C->>T: Initiates Phone Call
    T->>WS: WebSocket Connection
    Note over WS: Capture connection details
    WS->>E: Establish ConvAI Connection
    Note over E: Agent authentication
    
    Note over C,E: Audio Stream Start
    T->>WS: {"event": "start", "streamSid": "..."}
    Note over WS: Capture streamSid for all outbound frames
    WS->>E: Send conversation start signal
    
    Note over C,E: Voice Input Processing
    C->>T: Voice Input (μ-law@8kHz)
    T->>WS: Audio Stream
    WS->>E: Forward Audio to ConvAI
    Note over E: AI processes voice input
    
    Note over C,E: AI Response Generation
    E->>WS: AI Response (PCM16@16kHz)
    Note over WS: Audio Processing Pipeline:
    Note over WS: 1. Convert PCM16@16k → μ-law@8k
    Note over WS: 2. Slice into 20ms frames (160 bytes)
    Note over WS: 3. Add streamSid to each frame
    Note over WS: 4. Buffer frames if needed
    
    loop For each 20ms frame
        WS->>B: Queue frame with streamSid
        B->>WS: Retrieve frame for sending
        WS->>T: {"event": "media", "streamSid": "...", "media": {"payload": "..."}}
        Note over WS: Wait 20ms (50fps pacing)
    end
    
    T->>C: AI Voice Response
    
    Note over C,E: Conversation Continues
    Note over WS: Maintain WebSocket connections
    Note over WS: Handle reconnections if needed
    
    Note over C,E: Call Termination
    C->>T: Hangs up
    T->>WS: {"event": "stop"}
    WS->>E: Close ConvAI connection
    Note over WS: Clean up resources
```

## Service Dependency Graph

```mermaid
graph TD
    subgraph "Core Services"
        API[FastAPI Main App]
        WS[WebSocket Bridge]
        CONFIG[Configuration Service]
    end
    
    subgraph "AI & Language Services"
        OPENAI[OpenAI Service]
        LLAMA[LLaMA Service]
        EL[ElevenLabs Service]
        DEEPGRAM[Deepgram Service]
        EMO[Emotional Intelligence]
    end
    
    subgraph "Communication Services"
        TWILIO[Twilio Service]
        SMS[SMS Service]
        VOICE[Voice Service]
        AUDIO[Audio Service]
    end
    
    subgraph "Data & Storage Services"
        REDIS[Redis Service]
        LOG[Logging Service]
        OFFLINE[Offline Service]
        CONTENT[Content Service]
    end
    
    subgraph "User Experience Services"
        GAMIFY[Gamification Service]
        MULTI[Multimodal Service]
        ANALYTICS[Analytics Service]
        NOTIFY[Notification Service]
    end
    
    subgraph "Security & Infrastructure"
        SECURITY[Security Service]
    end
    
    subgraph "Learning Modules"
        ENGLISH[English Module]
        MATH[Math Module]
        COMP[Comprehension Module]
        DEBATE[Debate Module]
        GENERAL[General Module]
    end
    
    %% Core Dependencies
    API --> CONFIG
    WS --> CONFIG
    
    %% AI Service Dependencies
    OPENAI --> CONFIG
    LLAMA --> CONFIG
    EL --> CONFIG
    DEEPGRAM --> CONFIG
    EMO --> OPENAI
    EMO --> REDIS
    
    %% Communication Dependencies
    TWILIO --> CONFIG
    SMS --> TWILIO
    VOICE --> TWILIO
    AUDIO --> DEEPGRAM
    WS --> EL
    WS --> AUDIO
    
    %% Data Dependencies
    REDIS --> CONFIG
    LOG --> REDIS
    OFFLINE --> REDIS
    CONTENT --> REDIS
    
    %% User Experience Dependencies
    GAMIFY --> REDIS
    MULTI --> OPENAI
    MULTI --> DEEPGRAM
    ANALYTICS --> LOG
    NOTIFY --> TWILIO
    
    %% Security Dependencies
    SECURITY --> CONFIG
    SECURITY --> REDIS
    
    %% Module Dependencies
    ENGLISH --> OPENAI
    ENGLISH --> LLAMA
    ENGLISH --> EMO
    ENGLISH --> GAMIFY
    ENGLISH --> MULTI
    
    MATH --> OPENAI
    MATH --> LLAMA
    MATH --> EMO
    MATH --> GAMIFY
    
    COMP --> OPENAI
    COMP --> LLAMA
    COMP --> EMO
    COMP --> GAMIFY
    
    DEBATE --> OPENAI
    DEBATE --> LLAMA
    DEBATE --> EMO
    DEBATE --> GAMIFY
    
    GENERAL --> OPENAI
    GENERAL --> LLAMA
    GENERAL --> EMO
    GENERAL --> GAMIFY
    
    %% API Router Dependencies
    API --> TWILIO
    API --> OPENAI
    API --> REDIS
    API --> LOG
    API --> ENGLISH
    API --> MATH
    API --> COMP
    API --> DEBATE
    API --> GENERAL
    
    %% Styling
    classDef core fill:#e3f2fd
    classDef ai fill:#f3e5f5
    classDef comm fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef ux fill:#fce4ec
    classDef security fill:#ffebee
    classDef modules fill:#e0f2f1
    
    class API,WS,CONFIG core
    class OPENAI,LLAMA,EL,DEEPGRAM,EMO ai
    class TWILIO,SMS,VOICE,AUDIO comm
    class REDIS,LOG,OFFLINE,CONTENT data
    class GAMIFY,MULTI,ANALYTICS,NOTIFY ux
    class SECURITY security
    class ENGLISH,MATH,COMP,DEBATE,GENERAL modules
```

## API Endpoint Flow

```mermaid
graph LR
    subgraph "Incoming Requests"
        CALL[📞 /call<br/>Voice Webhook]
        SMS_REQ[📱 /sms<br/>SMS Webhook]
        HEALTH[🏥 /health<br/>Health Check]
        ADMIN[⚙️ /admin/*<br/>Admin Routes]
        AUTH[🔐 /auth/*<br/>Auth Routes]
        CONTENT[📚 /content/*<br/>Content Routes]
    end
    
    subgraph "WebSocket Endpoints"
        WS_STREAM[🔄 /twilio-stream<br/>Audio WebSocket]
    end
    
    subgraph "Processing Logic"
        VOICE_HANDLER[Voice Call Handler]
        SMS_HANDLER[SMS Message Handler]
        WS_HANDLER[WebSocket Handler]
        MODULE_ROUTER[Module Router]
    end
    
    subgraph "Learning Modules"
        ENG[English Module]
        MATH_MOD[Math Module]
        COMP_MOD[Comprehension Module]
        DEB[Debate Module]
        GEN[General Module]
    end
    
    subgraph "External Integrations"
        TWILIO_OUT[Twilio Response]
        ELEVENLABS[ElevenLabs ConvAI]
        OPENAI_API[OpenAI GPT-4]
    end
    
    %% Request Flow
    CALL --> VOICE_HANDLER
    SMS_REQ --> SMS_HANDLER
    WS_STREAM --> WS_HANDLER
    
    %% Processing Flow
    VOICE_HANDLER --> TWILIO_OUT
    SMS_HANDLER --> MODULE_ROUTER
    WS_HANDLER --> ELEVENLABS
    
    %% Module Routing
    MODULE_ROUTER --> ENG
    MODULE_ROUTER --> MATH_MOD
    MODULE_ROUTER --> COMP_MOD
    MODULE_ROUTER --> DEB
    MODULE_ROUTER --> GEN
    
    %% AI Integration
    ENG --> OPENAI_API
    MATH_MOD --> OPENAI_API
    COMP_MOD --> OPENAI_API
    DEB --> OPENAI_API
    GEN --> OPENAI_API
    
    %% Response Flow
    OPENAI_API --> MODULE_ROUTER
    MODULE_ROUTER --> SMS_HANDLER
    SMS_HANDLER --> TWILIO_OUT
    
    %% WebSocket Flow
    ELEVENLABS --> WS_HANDLER
    WS_HANDLER --> TWILIO_OUT
    
    %% Styling
    classDef endpoint fill:#e1f5fe
    classDef websocket fill:#e8f5e8
    classDef processing fill:#fff3e0
    classDef modules fill:#f3e5f5
    classDef external fill:#ffebee
    
    class CALL,SMS_REQ,HEALTH,ADMIN,AUTH,CONTENT endpoint
    class WS_STREAM websocket
    class VOICE_HANDLER,SMS_HANDLER,WS_HANDLER,MODULE_ROUTER processing
    class ENG,MATH_MOD,COMP_MOD,DEB,GEN modules
    class TWILIO_OUT,ELEVENLABS,OPENAI_API external
```

## Frontend Component Architecture

```mermaid
graph TB
    subgraph "Frontend Application (React/Vite)"
        APP[App.tsx<br/>Main Application]
        
        subgraph "Pages (20+)"
            INDEX[Index.tsx]
            ABOUT[About.tsx]
            IVR[IVR.tsx]
            MODULES[LearningModules.tsx]
            ADMIN_DASH[AdminDashboard.tsx]
            EARLY[EarlyAccess.tsx]
            CONTACT[Contact.tsx]
            BLOG[Blog.tsx]
            TEAM[Team.tsx]
            SUPPORT[Support.tsx]
        end
        
        subgraph "Components (80+)"
            MODAL[EarlyAccessModal.tsx]
            TEAM_CARD[TeamMemberCard.tsx]
            DASHBOARD[DashboardLayout.tsx]
            USER_MGMT[UserManagement.tsx]
            PERF_MON[PerformanceMonitoring.tsx]
            AUDIT[AuditLogs.tsx]
        end
        
        subgraph "UI Components (40+)"
            BUTTON[button.tsx]
            CARD[card.tsx]
            DIALOG[dialog.tsx]
            SELECT[select.tsx]
            CHART[chart.tsx]
            CAROUSEL[carousel.tsx]
        end
        
        subgraph "Hooks (12+)"
            PAGINATION[usePagination.ts]
            IVR_CLIENT[useIVRClient.ts]
            RESOURCES[useResources.ts]
            TOAST[use-toast.ts]
            MOBILE[use-mobile.tsx]
            RATE_LIMIT[useRateLimit.ts]
        end
        
        subgraph "Utils (8+)"
            REALTIME[RealtimeChat.ts]
            AUDIO[BakameRealtimeAudio.ts]
            SECURITY[security.ts]
            LLAMA_AUDIO[BakameLlamaAudio.ts]
        end
    end
    
    subgraph "External Dependencies"
        RADIX[Radix UI Components]
        REACT_QUERY[TanStack Query]
        ROUTER[React Router]
        AXIOS[Axios HTTP Client]
        SUPABASE[Supabase Client]
        RECHARTS[Recharts]
    end
    
    subgraph "Backend API"
        API_ENDPOINTS[REST API Endpoints]
        WS_ENDPOINTS[WebSocket Endpoints]
    end
    
    %% Component Relationships
    APP --> INDEX
    APP --> ABOUT
    APP --> IVR
    APP --> MODULES
    APP --> ADMIN_DASH
    APP --> EARLY
    APP --> CONTACT
    APP --> BLOG
    APP --> TEAM
    APP --> SUPPORT
    
    %% Component Dependencies
    INDEX --> MODAL
    TEAM --> TEAM_CARD
    ADMIN_DASH --> DASHBOARD
    ADMIN_DASH --> USER_MGMT
    ADMIN_DASH --> PERF_MON
    ADMIN_DASH --> AUDIT
    
    %% UI Component Usage
    MODAL --> BUTTON
    MODAL --> DIALOG
    DASHBOARD --> CARD
    USER_MGMT --> SELECT
    PERF_MON --> CHART
    AUDIT --> CAROUSEL
    
    %% Hook Usage
    INDEX --> PAGINATION
    IVR --> IVR_CLIENT
    MODULES --> RESOURCES
    APP --> TOAST
    APP --> MOBILE
    API_ENDPOINTS --> RATE_LIMIT
    
    %% Utility Usage
    IVR --> REALTIME
    IVR --> AUDIO
    APP --> SECURITY
    AUDIO --> LLAMA_AUDIO
    
    %% External Dependencies
    APP --> RADIX
    API_ENDPOINTS --> REACT_QUERY
    APP --> ROUTER
    API_ENDPOINTS --> AXIOS
    APP --> SUPABASE
    PERF_MON --> RECHARTS
    
    %% Backend Integration
    AXIOS --> API_ENDPOINTS
    REALTIME --> WS_ENDPOINTS
    AUDIO --> WS_ENDPOINTS
    
    %% Styling
    classDef pages fill:#e3f2fd
    classDef components fill:#f3e5f5
    classDef ui fill:#e8f5e8
    classDef hooks fill:#fff3e0
    classDef utils fill:#fce4ec
    classDef external fill:#ffebee
    classDef backend fill:#e0f2f1
    
    class INDEX,ABOUT,IVR,MODULES,ADMIN_DASH,EARLY,CONTACT,BLOG,TEAM,SUPPORT pages
    class MODAL,TEAM_CARD,DASHBOARD,USER_MGMT,PERF_MON,AUDIT components
    class BUTTON,CARD,DIALOG,SELECT,CHART,CAROUSEL ui
    class PAGINATION,IVR_CLIENT,RESOURCES,TOAST,MOBILE,RATE_LIMIT hooks
    class REALTIME,AUDIO,SECURITY,LLAMA_AUDIO utils
    class RADIX,REACT_QUERY,ROUTER,AXIOS,SUPABASE,RECHARTS external
    class API_ENDPOINTS,WS_ENDPOINTS backend
```

## Admin Dashboard Architecture

```mermaid
graph TB
    subgraph "Admin Dashboard (React/TypeScript)"
        ADMIN_APP[Admin App.tsx]
        
        subgraph "Core UI Components"
            BUTTON_A[button.tsx]
            CARD_A[card.tsx]
            DIALOG_A[dialog.tsx]
            TABLE_A[table.tsx]
            FORM_A[form.tsx]
            SELECT_A[select.tsx]
            TABS_A[tabs.tsx]
            CHART_A[chart.tsx]
        end
        
        subgraph "Layout Components"
            SIDEBAR_A[sidebar.tsx]
            NAV_A[navigation-menu.tsx]
            BREADCRUMB_A[breadcrumb.tsx]
            SHEET_A[sheet.tsx]
        end
        
        subgraph "Data Components"
            PAGINATION_A[pagination.tsx]
            PROGRESS_A[progress.tsx]
            BADGE_A[badge.tsx]
            ALERT_A[alert.tsx]
        end
        
        subgraph "Input Components"
            INPUT_A[input.tsx]
            TEXTAREA_A[textarea.tsx]
            CHECKBOX_A[checkbox.tsx]
            RADIO_A[radio-group.tsx]
            SLIDER_A[slider.tsx]
            SWITCH_A[switch.tsx]
        end
        
        subgraph "Feedback Components"
            TOAST_A[toast.tsx]
            TOASTER_A[toaster.tsx]
            SONNER_A[sonner.tsx]
            TOOLTIP_A[tooltip.tsx]
            POPOVER_A[popover.tsx]
        end
        
        subgraph "Utility Hooks"
            TOAST_HOOK_A[use-toast.ts]
            MOBILE_HOOK_A[use-mobile.tsx]
        end
    end
    
    subgraph "Admin Features"
        USER_ADMIN[User Management]
        CONTENT_ADMIN[Content Management]
        ANALYTICS_ADMIN[Analytics Dashboard]
        SYSTEM_ADMIN[System Monitoring]
        CONFIG_ADMIN[Configuration]
    end
    
    subgraph "Backend Integration"
        ADMIN_API[Admin API Endpoints]
        AUTH_API[Authentication API]
        ANALYTICS_API[Analytics API]
    end
    
    %% Component Relationships
    ADMIN_APP --> SIDEBAR_A
    ADMIN_APP --> NAV_A
    ADMIN_APP --> BREADCRUMB_A
    
    %% Feature Implementation
    USER_ADMIN --> TABLE_A
    USER_ADMIN --> FORM_A
    USER_ADMIN --> DIALOG_A
    
    CONTENT_ADMIN --> CARD_A
    CONTENT_ADMIN --> TABS_A
    CONTENT_ADMIN --> INPUT_A
    
    ANALYTICS_ADMIN --> CHART_A
    ANALYTICS_ADMIN --> PROGRESS_A
    ANALYTICS_ADMIN --> BADGE_A
    
    SYSTEM_ADMIN --> ALERT_A
    SYSTEM_ADMIN --> TOAST_A
    SYSTEM_ADMIN --> PAGINATION_A
    
    CONFIG_ADMIN --> SELECT_A
    CONFIG_ADMIN --> SWITCH_A
    CONFIG_ADMIN --> SLIDER_A
    
    %% Hook Usage
    TOAST_A --> TOAST_HOOK_A
    ADMIN_APP --> MOBILE_HOOK_A
    
    %% Backend Integration
    USER_ADMIN --> ADMIN_API
    CONTENT_ADMIN --> ADMIN_API
    ANALYTICS_ADMIN --> ANALYTICS_API
    ADMIN_APP --> AUTH_API
    
    %% Styling
    classDef core fill:#e3f2fd
    classDef layout fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef input fill:#fff3e0
    classDef feedback fill:#fce4ec
    classDef hooks fill:#ffebee
    classDef features fill:#e0f2f1
    classDef backend fill:#f1f8e9
    
    class BUTTON_A,CARD_A,DIALOG_A,TABLE_A,FORM_A,SELECT_A,TABS_A,CHART_A core
    class SIDEBAR_A,NAV_A,BREADCRUMB_A,SHEET_A layout
    class PAGINATION_A,PROGRESS_A,BADGE_A,ALERT_A data
    class INPUT_A,TEXTAREA_A,CHECKBOX_A,RADIO_A,SLIDER_A,SWITCH_A input
    class TOAST_A,TOASTER_A,SONNER_A,TOOLTIP_A,POPOVER_A feedback
    class TOAST_HOOK_A,MOBILE_HOOK_A hooks
    class USER_ADMIN,CONTENT_ADMIN,ANALYTICS_ADMIN,SYSTEM_ADMIN,CONFIG_ADMIN features
    class ADMIN_API,AUTH_API,ANALYTICS_API backend
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Fly.io Infrastructure"
            FLY_BACKEND[Backend App<br/>bakame-elevenlabs-mcp<br/>fra region]
            FLY_FRONTEND[Frontend App<br/>app-pyzfduqr<br/>Static hosting]
        end
        
        subgraph "Devin Apps"
            DEVIN_ADMIN[Admin Dashboard<br/>project-handling-app-jiwikt4q<br/>React deployment]
        end
        
        subgraph "External Services"
            TWILIO_PROD[Twilio Production<br/>Voice/SMS Gateway]
            ELEVENLABS_PROD[ElevenLabs Production<br/>ConvAI Service]
            OPENAI_PROD[OpenAI Production<br/>GPT-4 API]
            REDIS_PROD[Redis Cloud<br/>Session Storage]
            POSTGRES_PROD[PostgreSQL<br/>Primary Database]
        end
    end
    
    subgraph "Development Environment"
        LOCAL_BACKEND[Local Backend<br/>uvicorn dev server]
        LOCAL_FRONTEND[Local Frontend<br/>Vite dev server]
        LOCAL_ADMIN[Local Admin<br/>Vite dev server]
        LOCAL_DB[Local PostgreSQL]
        LOCAL_REDIS[Local Redis]
    end
    
    subgraph "CI/CD Pipeline"
        GIT_REPO[Git Repository<br/>mvp branch]
        BUILD_BACKEND[Backend Build<br/>Docker + Poetry]
        BUILD_FRONTEND[Frontend Build<br/>Vite + TypeScript]
        BUILD_ADMIN[Admin Build<br/>TypeScript + Vite]
        DEPLOY_FLY[Fly.io Deployment]
        DEPLOY_DEVIN[Devin Apps Deployment]
    end
    
    %% Production Connections
    FLY_BACKEND --> TWILIO_PROD
    FLY_BACKEND --> ELEVENLABS_PROD
    FLY_BACKEND --> OPENAI_PROD
    FLY_BACKEND --> REDIS_PROD
    FLY_BACKEND --> POSTGRES_PROD
    
    FLY_FRONTEND --> FLY_BACKEND
    DEVIN_ADMIN --> FLY_BACKEND
    
    %% Development Connections
    LOCAL_BACKEND --> LOCAL_DB
    LOCAL_BACKEND --> LOCAL_REDIS
    LOCAL_FRONTEND --> LOCAL_BACKEND
    LOCAL_ADMIN --> LOCAL_BACKEND
    
    %% CI/CD Flow
    GIT_REPO --> BUILD_BACKEND
    GIT_REPO --> BUILD_FRONTEND
    GIT_REPO --> BUILD_ADMIN
    
    BUILD_BACKEND --> DEPLOY_FLY
    BUILD_FRONTEND --> DEPLOY_FLY
    BUILD_ADMIN --> DEPLOY_DEVIN
    
    DEPLOY_FLY --> FLY_BACKEND
    DEPLOY_FLY --> FLY_FRONTEND
    DEPLOY_DEVIN --> DEVIN_ADMIN
    
    %% Styling
    classDef production fill:#e8f5e8
    classDef development fill:#fff3e0
    classDef cicd fill:#e3f2fd
    classDef external fill:#ffebee
    
    class FLY_BACKEND,FLY_FRONTEND,DEVIN_ADMIN production
    class LOCAL_BACKEND,LOCAL_FRONTEND,LOCAL_ADMIN,LOCAL_DB,LOCAL_REDIS development
    class GIT_REPO,BUILD_BACKEND,BUILD_FRONTEND,BUILD_ADMIN,DEPLOY_FLY,DEPLOY_DEVIN cicd
    class TWILIO_PROD,ELEVENLABS_PROD,OPENAI_PROD,REDIS_PROD,POSTGRES_PROD external
```

## Audio Processing State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Connecting : Incoming Call
    Connecting --> Connected : WebSocket Established
    Connected --> StreamReady : streamSid Captured
    
    StreamReady --> Processing : Audio Received
    Processing --> Converting : PCM16@16k Input
    Converting --> Framing : μ-law@8k Output
    Framing --> Buffering : 20ms Frames (160 bytes)
    Buffering --> Sending : Frame Queue Ready
    Sending --> Pacing : Send to Twilio
    Pacing --> Processing : Wait 20ms (50fps)
    
    Processing --> Silence : No Audio Input
    Silence --> SilenceFrames : Generate Padding
    SilenceFrames --> Sending : Maintain Pipeline
    
    StreamReady --> Reconnecting : Connection Lost
    Processing --> Reconnecting : WebSocket Error
    Reconnecting --> Connected : Reconnection Success
    Reconnecting --> Failed : Max Retries Exceeded
    
    Sending --> Stopping : Call End Signal
    Stopping --> Cleanup : Flush Buffers
    Cleanup --> Idle : Resources Released
    
    Failed --> Cleanup : Error Handling
    
    note right of Converting
        Audio Conversion:
        - Downsample 16kHz → 8kHz
        - Convert PCM → μ-law
        - Maintain audio quality
    end note
    
    note right of Framing
        Frame Processing:
        - Slice into 20ms chunks
        - Exactly 160 bytes per frame
        - Include streamSid in metadata
    end note
    
    note right of Pacing
        Timing Control:
        - 50 frames per second
        - asyncio.sleep(0.02)
        - Real-time delivery
    end note
```

This comprehensive set of diagrams illustrates the complete BAKAME AI system architecture, from high-level component relationships to detailed audio processing workflows. Each diagram focuses on a specific aspect of the system while maintaining consistency with the overall architecture.
