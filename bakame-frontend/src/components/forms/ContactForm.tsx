import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { useRateLimit } from '@/hooks/useRateLimit';
import { authAPI } from '@/services/api';
import { useAnalytics } from '@/components/analytics/AnalyticsProvider';
import { sanitizeInput, validateEmail, validatePhone, logSecurityEvent } from '@/utils/security';

interface ContactFormProps {
  className?: string;
}

export const ContactForm = ({ className = "" }: ContactFormProps) => {
  const { toast } = useToast();
  const { trackEvent } = useAnalytics();
  const { isBlocked, checkLimit } = useRateLimit();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    subject: '',
    message: '',
    solution_type: '',
  });

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      toast({
        title: "Validation Error",
        description: "Name is required",
        variant: "destructive",
      });
      return false;
    }

    if (!validateEmail(formData.email)) {
      toast({
        title: "Validation Error",
        description: "Please enter a valid email address",
        variant: "destructive",
      });
      return false;
    }

    if (formData.phone && !validatePhone(formData.phone)) {
      toast({
        title: "Validation Error",
        description: "Please enter a valid phone number",
        variant: "destructive",
      });
      return false;
    }

    if (!formData.message.trim()) {
      toast({
        title: "Validation Error",
        description: "Message is required",
        variant: "destructive",
      });
      return false;
    }

    if (formData.message.length < 10) {
      toast({
        title: "Validation Error",
        description: "Message must be at least 10 characters long",
        variant: "destructive",
      });
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isBlocked) {
      toast({
        title: "Too Many Requests",
        description: "Please wait before submitting another form.",
        variant: "destructive",
      });
      return;
    }

    if (!validateForm()) {
      return;
    }

    // Check rate limit (3 submissions per 15 minutes)
    const canProceed = await checkLimit('contact_form', 3);
    if (!canProceed) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Sanitize all inputs
      const sanitizedData = {
        name: sanitizeInput(formData.name, 100),
        email: sanitizeInput(formData.email, 254).toLowerCase(),
        phone: sanitizeInput(formData.phone, 20),
        company: sanitizeInput(formData.company, 100),
        subject: sanitizeInput(formData.subject, 200),
        message: sanitizeInput(formData.message, 2000),
        solution_type: formData.solution_type,
      };

      const { error } = await supabase
        .from('contact_submissions')
        .insert([{
          ...sanitizedData,
          status: 'new'
        }]);

      if (error) {
        console.error('Error submitting contact form:', error);
        
        await logSecurityEvent({
          event_type: 'form_submission_error',
          details: { form: 'contact', error: error.message },
          severity: 'medium'
        });

        toast({
          title: "Error",
          description: "Failed to send your message. Please try again.",
          variant: "destructive",
        });
      } else {
        trackEvent('contact_form_submitted', { solution_type: sanitizedData.solution_type });
        
        await logSecurityEvent({
          event_type: 'form_submission_success',
          details: { form: 'contact' },
          severity: 'low'
        });

        toast({
          title: "Message Sent",
          description: "Thank you for your message. We'll get back to you soon!",
        });
        
        // Reset form
        setFormData({
          name: '',
          email: '',
          phone: '',
          company: '',
          subject: '',
          message: '',
          solution_type: '',
        });
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      
      await logSecurityEvent({
        event_type: 'form_submission_exception',
        details: { form: 'contact' },
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

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className={`bg-card backdrop-blur-sm rounded-3xl p-8 border border-border ${className}`}>
      <h2 className="text-2xl font-bold text-card-foreground mb-6">Get in Touch</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="name" className="text-foreground">Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleInputChange("name", e.target.value)}
              className="bg-input border-border text-foreground placeholder:text-muted-foreground"
              required
            />
          </div>
          <div>
            <Label htmlFor="email" className="text-foreground">Email *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange("email", e.target.value)}
              className="bg-input border-border text-foreground placeholder:text-muted-foreground"
              required
            />
          </div>
          <div>
            <Label htmlFor="phone" className="text-foreground">Phone</Label>
            <Input
              id="phone"
              value={formData.phone}
              onChange={(e) => handleInputChange("phone", e.target.value)}
              className="bg-input border-border text-foreground placeholder:text-muted-foreground"
            />
          </div>
          <div>
            <Label htmlFor="company" className="text-foreground">Company</Label>
            <Input
              id="company"
              value={formData.company}
              onChange={(e) => handleInputChange("company", e.target.value)}
              className="bg-input border-border text-foreground placeholder:text-muted-foreground"
            />
          </div>
        </div>

        <div>
          <Label className="text-foreground">Solution Interest</Label>
          <Select value={formData.solution_type} onValueChange={(value) => handleInputChange("solution_type", value)}>
            <SelectTrigger className="bg-input border-border text-foreground">
              <SelectValue placeholder="Select a solution" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="education">Education</SelectItem>
              <SelectItem value="enterprise">Enterprise</SelectItem>
              <SelectItem value="government">Government</SelectItem>
              <SelectItem value="general">General Inquiry</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="subject" className="text-foreground">Subject</Label>
          <Input
            id="subject"
            value={formData.subject}
            onChange={(e) => handleInputChange("subject", e.target.value)}
            className="bg-input border-border text-foreground placeholder:text-muted-foreground"
          />
        </div>

        <div>
          <Label htmlFor="message" className="text-foreground">Message *</Label>
          <Textarea
            id="message"
            value={formData.message}
            onChange={(e) => handleInputChange("message", e.target.value)}
            className="bg-input border-border text-foreground placeholder:text-muted-foreground min-h-[120px]"
            placeholder="Tell us about your needs..."
            required
          />
        </div>

        <Button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-primary text-primary-foreground py-3 rounded-full font-semibold text-lg hover:bg-primary/90 transition-all duration-300 disabled:opacity-50"
        >
          {isSubmitting ? "Sending..." : "Send Message"}
        </Button>
      </form>
    </div>
  );
};
