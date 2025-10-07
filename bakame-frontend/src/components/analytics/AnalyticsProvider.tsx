
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authAPI } from '@/services/api';

interface AnalyticsContextType {
  trackEvent: (eventType: string, eventData?: any) => void;
  trackPageView: (pagePath: string) => void;
  sessionId: string;
}

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};

interface AnalyticsProviderProps {
  children: ReactNode;
}

export const AnalyticsProvider = ({ children }: AnalyticsProviderProps) => {
  const [sessionId] = useState(() => crypto.randomUUID());

  const trackEvent = async (eventType: string, eventData: any = {}) => {
    try {
      let userId = null;
      try {
        const user = await authAPI.getCurrentUser();
        userId = user?.id || null;
      } catch {
        // Auth not available - continue without user ID
      }
      
      console.log('Analytics event:', {
        event_type: eventType,
        event_data: eventData,
        user_id: userId,
        session_id: sessionId,
        page_path: window.location.pathname,
        user_agent: navigator.userAgent,
      });
    } catch (error) {
      console.error('Analytics tracking error:', error);
    }
  };

  const trackPageView = async (pagePath: string) => {
    try {
      let userId = null;
      try {
        const user = await authAPI.getCurrentUser();
        userId = user?.id || null;
      } catch {
        // Auth not available - continue without user ID
      }
      
      console.log('Page view:', {
        event_type: 'page_view',
        event_data: { path: pagePath },
        user_id: userId,
        session_id: sessionId,
        page_path: pagePath,
        user_agent: navigator.userAgent,
      });

      console.log('Session update:', {
        session_id: sessionId,
        user_id: userId,
        user_agent: navigator.userAgent,
        last_activity: new Date().toISOString(),
        pages_visited: 1,
        referrer: document.referrer || null,
      });
    } catch (error) {
      console.error('Page view tracking error:', error);
    }
  };

  useEffect(() => {
    // Track initial page view
    trackPageView(window.location.pathname);
  }, []);

  return (
    <AnalyticsContext.Provider value={{ trackEvent, trackPageView, sessionId }}>
      {children}
    </AnalyticsContext.Provider>
  );
};
