
import { rateLimitAPI } from '@/services/api';

export interface RateLimitOptions {
  limit?: number;
  windowMinutes?: number;
}

export interface SecurityEvent {
  event_type: string;
  user_id?: string;
  ip_address?: string;
  user_agent?: string;
  details?: Record<string, any>;
  severity?: 'low' | 'medium' | 'high' | 'critical';
}

// Rate limiting function
export const checkRateLimit = async (
  action: string, 
  identifier: string, 
  options: RateLimitOptions = {}
): Promise<boolean> => {
  const { limit = 5 } = options;
  
  try {
    return await rateLimitAPI.checkRateLimit(action, limit);
  } catch (error) {
    console.error('Rate limit check failed:', error);
    return true;
  }
};

// Security event logging
export const logSecurityEvent = async (event: SecurityEvent): Promise<void> => {
  try {
    console.log('Security Event:', {
      event_type: event.event_type,
      user_id: event.user_id,
      ip_address: event.ip_address,
      user_agent: event.user_agent || (typeof navigator !== 'undefined' ? navigator.userAgent : null),
      details: event.details,
      severity: event.severity || 'info',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Failed to log security event:', error);
  }
};

// Enhanced input sanitization and validation with comprehensive XSS protection
export const sanitizeInput = (input: string, maxLength: number = 1000): string => {
  if (!input || typeof input !== 'string') return '';
  
  return input
    .trim()
    .slice(0, maxLength)
    // Remove script tags and content
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    // Remove iframe, object, embed tags
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi, '')
    .replace(/<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi, '')
    // Remove event handlers
    .replace(/on\w+\s*=\s*["'][^"']*["']/gi, '')
    // Remove javascript: and data: protocols
    .replace(/javascript:/gi, '')
    .replace(/data:\s*text\/html/gi, '')
    // Remove vbscript: protocol
    .replace(/vbscript:/gi, '')
    // Remove dangerous HTML entities
    .replace(/&lt;script/gi, '')
    .replace(/&lt;\/script/gi, '')
    // Remove potential HTML tags but allow some safe formatting
    .replace(/<(?!\/?(b|i|em|strong|p|br)\b)[^>]*>/gi, '');
};

// Enhanced HTML sanitization for rich content
export const sanitizeHtml = (html: string): string => {
  if (!html || typeof html !== 'string') return '';

  // Allow only safe HTML tags and attributes
  const allowedTags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li'];
  const allowedAttributes = ['class'];

  let sanitized = html;

  // Remove all tags except allowed ones
  sanitized = sanitized.replace(/<\/?([a-zA-Z0-9]+)[^>]*>/g, (match, tag) => {
    if (allowedTags.includes(tag.toLowerCase())) {
      return match;
    }
    return '';
  });

  // Sanitize attributes (remove all except allowed ones)
  sanitized = sanitized.replace(/(\w+)=["']([^"']*)["']/g, (match, attr, value) => {
    if (allowedAttributes.includes(attr.toLowerCase())) {
      return match;
    }
    return '';
  });

  return sanitized;
};

// Enhanced email validation with comprehensive checks
export const validateEmail = (email: string): boolean => {
  if (!email || typeof email !== 'string') return false;
  
  // RFC 5322 compliant email regex
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  
  // Check basic format
  if (!emailRegex.test(email)) return false;
  
  // Check length limits (RFC 5321)
  if (email.length > 254) return false;
  
  // Check for dangerous patterns
  if (email.includes('<') || email.includes('>') || email.includes('"') || email.includes('\\')) {
    return false;
  }
  
  return true;
};

// Enhanced phone validation
export const validatePhone = (phone: string): boolean => {
  if (!phone) return true; // Phone is optional
  
  // Remove all non-digit characters for validation
  const digitsOnly = phone.replace(/\D/g, '');
  
  // Check if it's a reasonable length (7-15 digits)
  return digitsOnly.length >= 7 && digitsOnly.length <= 15;
};

// Input length validation helper
export const validateInputLength = (input: string, maxLength: number, fieldName: string): boolean => {
  if (!input) return true; // Empty is okay unless required
  
  if (input.length > maxLength) {
    console.warn(`${fieldName} exceeds maximum length of ${maxLength} characters`);
    return false;
  }
  
  return true;
};

// Enhanced client identifier with better entropy
export const getClientIdentifier = (): string => {
  // Use multiple factors for better identification
  const userAgent = typeof navigator !== 'undefined' ? navigator.userAgent : '';
  const language = typeof navigator !== 'undefined' ? navigator.language : '';
  const platform = typeof navigator !== 'undefined' ? navigator.platform : '';
  const timestamp = Date.now().toString();
  const random = Math.random().toString(36);
  
  const combined = userAgent + language + platform + timestamp + random;
  return btoa(combined).slice(0, 32);
};

// Authentication state cleanup utility for preventing limbo states
export const cleanupAuthState = () => {
  try {
    // Remove FastAPI auth tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
  } catch (error) {
    console.warn('Failed to cleanup auth state:', error);
  }
};

// Content Security Policy headers helper
export const getSecurityHeaders = () => ({
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' http://localhost:8000;",
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
});
