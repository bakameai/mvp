# BAKAME Database Schema Visualization

## Supabase PostgreSQL Schema

```mermaid
erDiagram
    UserSession {
        int id PK
        string phone_number
        string session_id
        string module_name
        string interaction_type
        text user_input
        text ai_response
        timestamp created_at
        json metadata
    }
    
    ModuleUsage {
        int id PK
        string module_name
        int usage_count
        date date
        json performance_metrics
        timestamp created_at
        timestamp updated_at
    }
    
    UserSession ||--o{ ModuleUsage : "aggregates_to"
```

## Table Definitions

### UserSession Table
```sql
CREATE TABLE UserSession (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    module_name VARCHAR(50) NOT NULL,
    interaction_type VARCHAR(20) NOT NULL, -- 'voice' or 'sms'
    user_input TEXT,
    ai_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX idx_user_session_phone ON UserSession(phone_number);
CREATE INDEX idx_user_session_module ON UserSession(module_name);
CREATE INDEX idx_user_session_created ON UserSession(created_at);
CREATE INDEX idx_user_session_session_id ON UserSession(session_id);
```

### ModuleUsage Table
```sql
CREATE TABLE ModuleUsage (
    id SERIAL PRIMARY KEY,
    module_name VARCHAR(50) NOT NULL,
    usage_count INTEGER DEFAULT 0,
    date DATE NOT NULL,
    performance_metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for analytics
CREATE INDEX idx_module_usage_module ON ModuleUsage(module_name);
CREATE INDEX idx_module_usage_date ON ModuleUsage(date);
CREATE UNIQUE INDEX idx_module_usage_unique ON ModuleUsage(module_name, date);
```

## Data Flow Diagram

```mermaid
flowchart TD
    subgraph "User Interaction"
        Voice[Voice Call]
        SMS[SMS Message]
    end
    
    subgraph "Application Layer"
        Backend[FastAPI Backend]
        Modules[Learning Modules]
    end
    
    subgraph "Data Storage"
        Redis[(Redis Cache<br/>Session Context)]
        Supabase[(Supabase PostgreSQL<br/>Persistent Storage)]
    end
    
    subgraph "Analytics"
        Admin[Admin Dashboard]
        Reports[Usage Reports]
    end
    
    Voice --> Backend
    SMS --> Backend
    Backend --> Modules
    Backend --> Redis
    Backend --> Supabase
    
    Supabase --> UserSession
    Supabase --> ModuleUsage
    
    UserSession --> Admin
    ModuleUsage --> Admin
    Admin --> Reports
    
    Redis -.->|Session Context| Backend
    Backend -.->|Log Interaction| UserSession
    Backend -.->|Update Stats| ModuleUsage
```

## Redis Cache Schema

```mermaid
graph TB
    subgraph "Redis Key Structure"
        SessionKey["session:{phone_number}"]
        ContextKey["context:{session_id}"]
        ModuleKey["module:{phone_number}:{module}"]
        ProgressKey["progress:{phone_number}"]
    end
    
    subgraph "Data Types"
        SessionData["{<br/>  current_module: string,<br/>  last_interaction: timestamp,<br/>  conversation_state: object<br/>}"]
        ContextData["{<br/>  messages: array,<br/>  user_level: number,<br/>  preferences: object<br/>}"]
        ModuleData["{<br/>  current_lesson: number,<br/>  difficulty_level: number,<br/>  completion_status: boolean<br/>}"]
        ProgressData["{<br/>  modules_completed: array,<br/>  total_sessions: number,<br/>  achievements: array<br/>}"]
    end
    
    SessionKey --> SessionData
    ContextKey --> ContextData
    ModuleKey --> ModuleData
    ProgressKey --> ProgressData
```

## Analytics Query Patterns

### Common Analytics Queries

```sql
-- Daily active users
SELECT DATE(created_at) as date, 
       COUNT(DISTINCT phone_number) as active_users
FROM UserSession 
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;

-- Module popularity
SELECT module_name, 
       COUNT(*) as total_interactions,
       COUNT(DISTINCT phone_number) as unique_users
FROM UserSession 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY module_name
ORDER BY total_interactions DESC;

-- User engagement patterns
SELECT phone_number,
       COUNT(*) as session_count,
       COUNT(DISTINCT module_name) as modules_used,
       MAX(created_at) as last_activity
FROM UserSession 
GROUP BY phone_number
HAVING COUNT(*) > 1
ORDER BY session_count DESC;

-- Performance metrics by module
SELECT m.module_name,
       m.usage_count,
       m.performance_metrics->>'avg_session_duration' as avg_duration,
       m.performance_metrics->>'completion_rate' as completion_rate
FROM ModuleUsage m
WHERE m.date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY m.usage_count DESC;
```

## Data Retention and Archival

```mermaid
timeline
    title Data Lifecycle Management
    
    section Active Data
        0-30 days : Hot storage in Supabase
                  : Full query performance
                  : Real-time analytics
    
    section Warm Data
        30-365 days : Compressed storage
                    : Reduced query frequency
                    : Historical reporting
    
    section Cold Data
        1+ years : Archive to object storage
                 : Compliance retention
                 : Backup only access
    
    section Purged Data
        7+ years : Secure deletion
                 : Compliance requirements
                 : Audit trail maintained
```

## Security and Privacy

### Data Encryption
- **At Rest**: AES-256 encryption in Supabase
- **In Transit**: TLS 1.3 for all connections
- **Application Level**: Sensitive fields encrypted before storage

### Access Control
- **Row Level Security**: Enabled on all tables
- **API Authentication**: JWT tokens for admin access
- **Database Roles**: Separate read/write permissions

### Privacy Compliance
- **Phone Number Hashing**: One-way hash for analytics
- **Data Minimization**: Only necessary fields stored
- **Right to Deletion**: Automated purge procedures
- **Audit Logging**: All data access tracked
