
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { useRateLimit } from '@/hooks/useRateLimit';
import { authAPI } from '@/services/api';
import { useAnalytics } from '@/components/analytics/AnalyticsProvider';
import { sanitizeInput, validateEmail, logSecurityEvent } from '@/utils/security';

interface NewsletterSignupProps {
  source?: string;
  className?: string;
}

export const NewsletterSignup = ({ source = 'general', className = "" }: NewsletterSignupProps) => {
  const { toast } = useToast();
  const { trackEvent } = useAnalytics();
  const { isBlocked, checkLimit } = useRateLimit();
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isBlocked) {
      toast({
        title: "Too Many Requests",
        description: "Please wait before subscribing again.",
        variant: "destructive",
      });
      return;
    }

    // Validate email
    if (!validateEmail(email)) {
      toast({
        title: "Invalid Email",
        description: "Please enter a valid email address.",
        variant: "destructive",
      });
      return;
    }

    // Check rate limit (2 subscriptions per 10 minutes)
    const canProceed = await checkLimit('newsletter_signup', 2);
    if (!canProceed) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Sanitize inputs
      const sanitizedEmail = sanitizeInput(email, 254).toLowerCase();
      const sanitizedName = sanitizeInput(name, 100);

      // Use type assertion for the newsletter subscriptions table
      const { error } = await (supabase as any)
        .from('newsletter_subscriptions')
        .insert([{
          email: sanitizedEmail,
          name: sanitizedName || null,
          source,
          status: 'active'
        }]);

      if (error) {
        if (error.code === '23505') { // Unique constraint violation
          toast({
            title: "Already Subscribed",
            description: "You're already subscribed to our newsletter!",
          });
        } else {
          console.error('Error subscribing to newsletter:', error);
          
          await logSecurityEvent({
            event_type: 'newsletter_subscription_error',
            details: { error: error.message, source },
            severity: 'medium'
          });

          toast({
            title: "Error",
            description: "Failed to subscribe. Please try again.",
            variant: "destructive",
          });
        }
      } else {
        trackEvent('newsletter_signup', { source });
        
        await logSecurityEvent({
          event_type: 'newsletter_subscription_success',
          details: { source },
          severity: 'low'
        });

        toast({
          title: "Successfully Subscribed",
          description: "Thank you for subscribing to our newsletter!",
        });
        
        setEmail('');
        setName('');
      }
    } catch (error) {
      console.error('Error subscribing:', error);
      
      await logSecurityEvent({
        event_type: 'newsletter_subscription_exception',
        details: { source },
        severity: 'high'
      });

      toast({
        title: "Error",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 ${className}`}>
      <h3 className="text-xl font-semibold text-white mb-4">Stay Updated</h3>
      <p className="text-white/70 mb-4">Get the latest updates on AI communication technology.</p>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          type="text"
          placeholder="Your name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
        />
        <Input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
          required
        />
        <Button
          type="submit"
          disabled={isSubmitting || !email}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-2 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-600 transition-all duration-300 disabled:opacity-50"
        >
          {isSubmitting ? "Subscribing..." : "Subscribe"}
        </Button>
      </form>
    </div>
  );
};
