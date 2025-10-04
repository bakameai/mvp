
import { useEffect } from 'react';
import { logSecurityEvent } from '@/utils/security';

export const useSecurityMonitoring = () => {
  useEffect(() => {
    // Monitor for suspicious activities
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        logSecurityEvent({
          event_type: 'page_focus',
          details: { url: window.location.href },
          severity: 'low'
        });
      }
    };

    const handleBeforeUnload = () => {
      logSecurityEvent({
        event_type: 'page_unload',
        details: { url: window.location.href },
        severity: 'low'
      });
    };

    // Monitor for potential security events
    const handleKeyDown = (event: KeyboardEvent) => {
      // Detect potential developer tools usage
      if (event.key === 'F12' || 
          (event.ctrlKey && event.shiftKey && event.key === 'I') ||
          (event.ctrlKey && event.shiftKey && event.key === 'C')) {
        logSecurityEvent({
          event_type: 'devtools_attempt',
          details: { key: event.key, ctrlKey: event.ctrlKey, shiftKey: event.shiftKey },
          severity: 'low'
        });
      }
    };

    // Monitor for context menu (right-click)
    const handleContextMenu = (event: MouseEvent) => {
      logSecurityEvent({
        event_type: 'context_menu',
        details: { x: event.clientX, y: event.clientY },
        severity: 'low'
      });
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('contextmenu', handleContextMenu);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('contextmenu', handleContextMenu);
    };
  }, []);
};
