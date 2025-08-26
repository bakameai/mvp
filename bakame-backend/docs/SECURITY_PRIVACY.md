# BAKAME IVR Security & Privacy Guidelines

## PII Redaction Rules

### Automatically Redacted Data
- **Phone Numbers**: All formats (international, local, formatted)
  - `+250788123456` → `[PHONE_REDACTED]`
  - `0788123456` → `[PHONE_REDACTED]`
  - `+1-555-123-4567` → `[PHONE_REDACTED]`

- **Email Addresses**: All standard formats
  - `user@example.com` → `[EMAIL_REDACTED]`
  - `test.email+tag@domain.co.uk` → `[EMAIL_REDACTED]`

### Preserved Data for Operations
- **Phone Number Field**: Preserved in dedicated column for record joining
- **Session IDs**: Preserved for conversation tracking
- **Call IDs**: Preserved for Twilio integration
- **Timestamps**: Preserved for analytics

### Sample Redacted Log Entries
```csv
timestamp,phone_number,session_id,module_name,interaction_type,user_input,ai_response
2024-01-15T10:30:45.123Z,+250788123456,session_001,english,voice,"My number is [PHONE_REDACTED]","I understand you want to share contact info, but let's focus on English practice!"
2024-01-15T10:31:12.456Z,+250788123456,session_001,english,voice,"Email me at [EMAIL_REDACTED]","Let's practice speaking instead of writing today."
```

## Data Retention Policy

### Conversation Data
- **CSV Logs**: Retained for 90 days, then archived
- **Database Records**: Retained for 1 year for analytics
- **Redis Sessions**: TTL of 24 hours, auto-expire

### Audio Data
- **Temporary Files**: Deleted after 1 hour
- **Recordings**: Not stored permanently
- **TTS Cache**: Cleared daily

### Metrics Data
- **Performance Metrics**: Retained for 6 months
- **Error Logs**: Retained for 3 months
- **Health Checks**: Retained for 30 days

## Access Controls

### Admin Dashboard Access
- **Authentication Required**: Yes
- **Role-Based Access**: Admin, Operator, Viewer
- **Session Timeout**: 4 hours
- **MFA Recommended**: Yes

### API Access
- **Webhook Endpoints**: Twilio signature verification
- **Admin APIs**: Bearer token authentication
- **Health Checks**: Public (no sensitive data)

### Database Access
- **Application User**: Limited to CRUD operations
- **Admin User**: Full access for maintenance
- **Backup User**: Read-only for backups

## Compliance Considerations

### GDPR Compliance
- **Right to Erasure**: Implement user data deletion
- **Data Portability**: Export user conversation history
- **Consent Management**: Track user consent for data processing
- **Privacy by Design**: PII redaction by default

### Rwanda Data Protection
- **Local Data Storage**: Consider in-country hosting
- **Cross-Border Transfers**: Document API data flows
- **User Rights**: Implement access and correction mechanisms

## Security Best Practices

### API Security
- **HTTPS Only**: All communications encrypted
- **API Key Rotation**: Regular rotation schedule
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Sanitize all inputs

### Infrastructure Security
- **Environment Variables**: Never commit secrets
- **Database Encryption**: Encrypt at rest
- **Network Security**: VPC and firewall rules
- **Monitoring**: Log security events

### Incident Response
1. **Detection**: Monitor for unusual patterns
2. **Containment**: Isolate affected systems
3. **Investigation**: Analyze logs and metrics
4. **Recovery**: Restore normal operations
5. **Documentation**: Record lessons learned
