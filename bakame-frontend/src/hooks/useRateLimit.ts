
import { useState } from 'react';
import { authAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

interface UseRateLimitResult {
  isBlocked: boolean;
  remaining: number;
  resetTime: string | null;
  checkLimit: (action: string, limit?: number) => Promise<boolean>;
  resetBlock: () => void;
}

export const useRateLimit = (): UseRateLimitResult => {
  const [isBlocked, setIsBlocked] = useState(false);
  const [remaining, setRemaining] = useState(0);
  const [resetTime, setResetTime] = useState<string | null>(null);
  const { toast } = useToast();

  const checkLimit = async (
    action: string, 
    limit: number = 5
  ): Promise<boolean> => {
    try {
      const response = await fetch('/api/rate-limit-check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ action, limit })
      });
      
      const data = response.ok ? await response.json() : null;
      const error = response.ok ? null : new Error('Rate limit check failed');

      if (error) {
        console.error('Rate limit check failed:', error);
        // Fail open - allow the action if rate limiting fails
        setIsBlocked(false);
        setRemaining(limit - 1);
        return true;
      }

      const allowed = data?.allowed || false;
      setIsBlocked(!allowed);
      setRemaining(data?.remaining || 0);
      
      if (data?.resetTime) {
        setResetTime(data.resetTime);
      }

      if (!allowed) {
        const resetDate = data?.resetTime ? new Date(data.resetTime) : new Date(Date.now() + 15 * 60 * 1000);
        const minutesUntilReset = Math.ceil((resetDate.getTime() - Date.now()) / (1000 * 60));
        
        toast({
          title: "Too Many Requests",
          description: `Please wait ${minutesUntilReset} minutes before trying again.`,
          variant: "destructive",
        });
        
        // Auto-reset block after window period
        setTimeout(() => {
          setIsBlocked(false);
          setResetTime(null);
        }, minutesUntilReset * 60 * 1000);
      }

      return allowed;
    } catch (error) {
      console.error('Rate limit check failed:', error);
      // Fail open - allow the action if rate limiting fails
      setIsBlocked(false);
      setRemaining(limit - 1);
      return true;
    }
  };

  const resetBlock = () => {
    setIsBlocked(false);
    setResetTime(null);
  };

  return {
    isBlocked,
    remaining,
    resetTime,
    checkLimit,
    resetBlock
  };
};
