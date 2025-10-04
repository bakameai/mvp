# BAKAME MVP - IP Registration Documentation

## Infrastructure IP Registration Requirements

### Production Deployment Endpoints

#### Backend API Infrastructure
- **Primary Backend**: `https://app-pyzfduqr.fly.dev/`
- **Hosting Provider**: Fly.io
- **IP Range**: Dynamic (Fly.io managed)
- **SSL/TLS**: Required for all endpoints
- **Webhook Endpoints**: `/webhook/voice`, `/webhook/sms`

#### Frontend Admin Dashboard
- **Primary Frontend**: `https://project-handling-app-jiwikt4q.devinapps.com/`
- **Hosting Provider**: Static site deployment
- **IP Range**: CDN distributed
- **SSL/TLS**: Required

### External Service Integration IPs

#### Twilio Service Integration
- **Webhook Destinations**: Backend API endpoints
- **Required IP Allowlisting**: 
  - Twilio webhook source IPs (region-specific)
  - Backend server IPs for outbound API calls
- **Ports**: 443 (HTTPS), 80 (HTTP redirect)
- **Authentication**: Webhook signature validation

#### OpenAI API Integration
- **Service Endpoints**: 
  - `https://api.openai.com/v1/audio/transcriptions` (Whisper)
  - `https://api.openai.com/v1/chat/completions` (GPT-3.5)
- **Required Access**: Outbound HTTPS (443) from backend servers
- **Authentication**: API key based
- **Rate Limiting**: Per API key limits

#### Supabase Database
- **Connection Endpoint**: `db.pttxlvbyvhgvwbakabyc.supabase.co:5432`
- **Protocol**: PostgreSQL over SSL
- **IP Allowlisting**: Backend server IPs
- **Authentication**: Username/password with SSL certificates
- **Connection Pooling**: Direct connection (non-pooler)

#### Redis Cache Service
- **Connection**: Redis cloud service or self-hosted
- **Port**: 6379 (standard Redis port)
- **IP Allowlisting**: Backend server IPs only
- **Authentication**: Password-based or certificate-based

### Security Configuration

#### SSL/TLS Requirements
- **All HTTP Traffic**: Redirect to HTTPS
- **Certificate Management**: Automated renewal
- **Cipher Suites**: Modern TLS 1.2+ only
- **HSTS**: Enabled for all domains

#### Firewall Rules
- **Inbound Rules**:
  - Port 443: HTTPS traffic from anywhere
  - Port 80: HTTP redirect only
  - Port 22: SSH access (admin IPs only)
- **Outbound Rules**:
  - Port 443: HTTPS to external APIs
  - Port 5432: PostgreSQL to Supabase
  - Port 6379: Redis connections

#### API Security
- **Rate Limiting**: Per-endpoint limits
- **CORS Configuration**: Specific origin allowlisting
- **API Key Management**: Secure environment variables
- **Webhook Validation**: Signature verification

### Monitoring and Logging

#### IP Access Logging
- **Web Server Logs**: All HTTP requests with source IPs
- **Database Connections**: Connection source tracking
- **API Calls**: External service request logging
- **Security Events**: Failed authentication attempts

#### Network Monitoring
- **Uptime Monitoring**: Endpoint availability
- **Performance Metrics**: Response time tracking
- **Error Tracking**: Failed requests and exceptions
- **Capacity Planning**: Traffic pattern analysis

### Deployment Considerations

#### Staging Environment
- **Staging Backend**: Separate IP range
- **Testing Database**: Isolated Supabase project
- **External Services**: Sandbox/test API keys
- **Access Control**: Development team IPs only

#### Production Environment
- **Load Balancing**: Multiple server instances
- **Geographic Distribution**: Multi-region deployment
- **Backup Systems**: Database and file backups
- **Disaster Recovery**: Cross-region failover

### Compliance Requirements

#### Data Protection
- **GDPR Compliance**: EU data handling requirements
- **Data Encryption**: At rest and in transit
- **Access Logging**: User data access tracking
- **Data Retention**: Configurable retention policies

#### Educational Standards
- **COPPA Compliance**: Children's privacy protection
- **FERPA Alignment**: Educational record privacy
- **Accessibility**: WCAG 2.1 compliance
- **Content Filtering**: Age-appropriate content

### IP Registration Checklist

#### Pre-Deployment
- [ ] Register production domain names
- [ ] Configure DNS records with proper TTL
- [ ] Set up SSL certificates for all domains
- [ ] Configure firewall rules for all services
- [ ] Test external service connectivity
- [ ] Verify webhook endpoint accessibility

#### Service Configuration
- [ ] Whitelist backend IPs in Supabase
- [ ] Configure Twilio webhook URLs
- [ ] Set up OpenAI API access
- [ ] Configure Redis connection security
- [ ] Test all external integrations
- [ ] Verify SSL certificate chain

#### Monitoring Setup
- [ ] Configure uptime monitoring
- [ ] Set up log aggregation
- [ ] Enable security event alerts
- [ ] Test backup and recovery procedures
- [ ] Document incident response procedures
- [ ] Train operations team on procedures

#### Documentation
- [ ] Network topology diagrams
- [ ] IP address inventory
- [ ] Service dependency mapping
- [ ] Security configuration guide
- [ ] Troubleshooting procedures
- [ ] Contact information for all services
