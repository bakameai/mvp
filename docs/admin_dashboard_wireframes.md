# BAKAME Admin Dashboard Wireframes

## Main Dashboard Layout

```mermaid
graph TB
    subgraph "Header Navigation"
        Logo[BAKAME Logo]
        Nav[Dashboard | Analytics | Sessions | Export | Settings]
        User[Admin User Profile]
    end
    
    subgraph "Main Content Area"
        subgraph "Key Metrics Row"
            Metric1[Active Users<br/>Today: 245]
            Metric2[Total Sessions<br/>This Week: 1,847]
            Metric3[Popular Module<br/>Math: 34%]
            Metric4[Avg Session<br/>Duration: 8.5m]
        end
        
        subgraph "Charts Section"
            Chart1[Daily Active Users<br/>Line Chart]
            Chart2[Module Usage<br/>Pie Chart]
        end
        
        subgraph "Recent Activity"
            Activity[Live Session Feed<br/>Real-time Updates]
        end
    end
    
    subgraph "Sidebar"
        QuickStats[Quick Stats<br/>Summary Cards]
        Alerts[System Alerts<br/>Notifications]
    end
```

## Analytics Dashboard Wireframe

```mermaid
flowchart TD
    subgraph "Analytics Page Layout"
        subgraph "Filter Controls"
            DateRange[Date Range Picker]
            ModuleFilter[Module Filter]
            RegionFilter[Region Filter]
            ExportBtn[Export Data]
        end
        
        subgraph "Performance Metrics"
            UserGrowth[User Growth Chart<br/>Monthly Trend]
            Engagement[Engagement Metrics<br/>Session Duration, Frequency]
            Completion[Completion Rates<br/>By Module]
        end
        
        subgraph "Usage Analytics"
            HeatMap[Usage Heatmap<br/>Time of Day vs Day of Week]
            Geographic[Geographic Distribution<br/>User Locations]
            DeviceType[Device Type<br/>Feature Phone vs Smartphone]
        end
        
        subgraph "Learning Outcomes"
            Progress[Learning Progress<br/>User Advancement]
            Retention[User Retention<br/>Cohort Analysis]
            Satisfaction[User Satisfaction<br/>Feedback Scores]
        end
    end
```

## Session Management Interface

```mermaid
graph TB
    subgraph "Session Management Page"
        subgraph "Session List Controls"
            Search[Search Sessions<br/>Phone, Module, Date]
            Filter[Filter Options<br/>Active, Completed, Failed]
            Sort[Sort Options<br/>Time, Duration, Module]
        end
        
        subgraph "Session Table"
            Headers[Phone | Module | Type | Duration | Status | Actions]
            Row1[+1234567890 | Math | Voice | 12:34 | Active | View Details]
            Row2[+1234567891 | English | SMS | 08:45 | Completed | View Details]
            Row3[+1234567892 | Reading | Voice | 15:22 | Completed | View Details]
            Pagination[← Previous | 1 2 3 4 5 | Next →]
        end
        
        subgraph "Session Details Modal"
            SessionInfo[Session Information<br/>Start Time, End Time, Module]
            Conversation[Conversation History<br/>User Input → AI Response]
            Metadata[Session Metadata<br/>Device Info, Location, Performance]
        end
    end
```

## Data Export Interface

```mermaid
flowchart TD
    subgraph "Export Page Layout"
        subgraph "Export Configuration"
            DataType[Data Type Selection<br/>☑ User Sessions<br/>☑ Module Usage<br/>☐ System Logs]
            DateRange2[Date Range<br/>From: [Date Picker]<br/>To: [Date Picker]]
            Format[Export Format<br/>○ CSV ● Excel ○ JSON]
            Filters[Additional Filters<br/>Module, Region, User Type]
        end
        
        subgraph "Export Options"
            Schedule[Scheduled Exports<br/>Daily, Weekly, Monthly]
            Email[Email Delivery<br/>Send to: admin@bakame.org]
            Compression[Compression<br/>☑ ZIP Archive]
        end
        
        subgraph "Export History"
            Recent[Recent Exports<br/>Download Links & Status]
            Queue[Export Queue<br/>Pending Exports]
        end
        
        subgraph "Actions"
            Preview[Preview Data]
            Generate[Generate Export]
            Download[Download Ready Files]
        end
    end
```

## System Settings Interface

```mermaid
graph TB
    subgraph "Settings Page"
        subgraph "API Configuration"
            TwilioSettings[Twilio Settings<br/>Account SID, Auth Token<br/>Phone Numbers]
            OpenAISettings[OpenAI Settings<br/>API Key, Model Selection<br/>Rate Limits]
            DatabaseSettings[Database Settings<br/>Connection String<br/>Pool Size]
        end
        
        subgraph "Application Settings"
            ModuleConfig[Module Configuration<br/>Enable/Disable Modules<br/>Difficulty Settings]
            LanguageSettings[Language Settings<br/>Supported Languages<br/>Default Language]
            SessionSettings[Session Settings<br/>Timeout Duration<br/>Max Session Length]
        end
        
        subgraph "Security Settings"
            UserManagement[User Management<br/>Admin Users<br/>Permissions]
            APIKeys[API Key Management<br/>Generate, Revoke<br/>Access Logs]
            AuditLog[Audit Log<br/>System Changes<br/>User Actions]
        end
        
        subgraph "Monitoring"
            Alerts2[Alert Configuration<br/>Error Thresholds<br/>Notification Settings]
            Health[System Health<br/>Service Status<br/>Performance Metrics]
            Backup[Backup Settings<br/>Schedule, Retention<br/>Recovery Options]
        end
    end
```

## Mobile Responsive Design

```mermaid
graph TB
    subgraph "Desktop Layout (1200px+)"
        DesktopHeader[Full Navigation Bar]
        DesktopSidebar[Sidebar with Quick Stats]
        DesktopMain[Main Content Area - 3 Column Grid]
        DesktopCharts[Large Charts and Tables]
    end
    
    subgraph "Tablet Layout (768px - 1199px)"
        TabletHeader[Condensed Navigation]
        TabletMain[Main Content - 2 Column Grid]
        TabletSidebar[Collapsible Sidebar]
        TabletCharts[Medium Charts, Scrollable Tables]
    end
    
    subgraph "Mobile Layout (< 768px)"
        MobileHeader[Hamburger Menu]
        MobileMain[Single Column Stack]
        MobileCards[Card-based Layout]
        MobileCharts[Simplified Charts, Swipe Tables]
    end
```

## User Experience Flow

```mermaid
journey
    title Admin Dashboard User Journey
    section Login
      Access Dashboard: 5: Admin
      Authenticate: 4: Admin
      Load Main View: 5: Admin
    section Daily Monitoring
      Check Key Metrics: 5: Admin
      Review Active Sessions: 4: Admin
      Monitor System Health: 4: Admin
    section Weekly Analysis
      Generate Reports: 3: Admin
      Analyze Trends: 4: Admin
      Export Data: 3: Admin
    section Issue Response
      Receive Alert: 2: Admin
      Investigate Problem: 3: Admin
      Take Corrective Action: 4: Admin
    section Configuration
      Update Settings: 3: Admin
      Manage Users: 3: Admin
      Schedule Backups: 4: Admin
```

## Component Library

### Dashboard Cards
```
┌─────────────────────────┐
│ Active Users            │
│ 245                     │
│ +12% from yesterday     │
└─────────────────────────┘
```

### Data Tables
```
┌─────────────┬──────────┬──────────┬─────────┐
│ Phone       │ Module   │ Duration │ Status  │
├─────────────┼──────────┼──────────┼─────────┤
│ +1234567890 │ Math     │ 12:34    │ Active  │
│ +1234567891 │ English  │ 08:45    │ Done    │
│ +1234567892 │ Reading  │ 15:22    │ Done    │
└─────────────┴──────────┴──────────┴─────────┘
```

### Chart Containers
```
┌─────────────────────────────────────────┐
│ Daily Active Users                      │
│ ┌─────────────────────────────────────┐ │
│ │     Line Chart Area                 │ │
│ │                                     │ │
│ │     Interactive Tooltips            │ │
│ │     Zoom & Pan Controls             │ │
│ └─────────────────────────────────────┘ │
│ Date Range: Last 30 Days               │
└─────────────────────────────────────────┘
```

### Modal Dialogs
```
┌─────────────────────────────────────────┐
│ Session Details                    ✕    │
├─────────────────────────────────────────┤
│ Phone: +1234567890                      │
│ Module: Math                            │
│ Duration: 12:34                         │
│ ─────────────────────────────────────── │
│ Conversation History:                   │
│ User: "Help me with fractions"          │
│ AI: "Let's start with basic fractions..." │
│ ─────────────────────────────────────── │
│ [Close] [Export Conversation]           │
└─────────────────────────────────────────┘
```
