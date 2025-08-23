
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
import { Shield } from 'lucide-react';

interface SecureContactFormProps {
  className?: string;
}

export const SecureContactForm = ({ className = "" }: SecureContactFormProps) => {
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
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Required field validation
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.length > 100) {
      newErrors.name = 'Name must be less than 100 characters';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (formData.phone && !validatePhone(formData.phone)) {
      newErrors.phone = 'Please enter a valid phone number';
    }

    if (!formData.message.trim()) {
      newErrors.message = 'Message is required';
    } else if (formData.message.length < 10) {
      newErrors.message = 'Message must be at least 10 characters';
    } else if (formData.message.length > 2000) {
      newErrors.message = 'Message must be less than 2000 characters';
    }

    // Optional field length validation
    if (formData.company.length > 100) {
      newErrors.company = 'Company name must be less than 100 characters';
    }

    if (formData.subject.length > 200) {
      newErrors.subject = 'Subject must be less than 200 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isBlocked) {
      toast({
        title: "Rate Limited",
        description: "Please wait before submitting another form.",
        variant: "destructive",
      });
      return;
    }

    if (!validateForm()) {
      await logSecurityEvent({
        event_type: 'form_validation_failed',
        details: { form: 'contact', errors: Object.keys(errors) },
        severity: 'low'
      });
      return;
    }

    // Check rate limit
    const canProceed = await checkLimit('contact_form', 3); // 3 submissions per 15 minutes
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
          title: "Submission Error",
          description: "There was a problem submitting your message. Please try again.",
          variant: "destructive",
        });
      } else {
        trackEvent('contact_form_submitted', { solution_type: sanitizedData.solution_type });
        
        await logSecurityEvent({
          event_type: 'form_submission_success',
          details: { form: 'contact', solution_type: sanitizedData.solution_type },
          severity: 'low'
        });

        toast({
          title: "Message Sent Successfully",
          description: "Thank you for your message. Our team will get back to you soon!",
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
        setErrors({});
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      
      await logSecurityEvent({
        event_type: 'form_submission_exception',
        details: { form: 'contact', error: String(error) },
        severity: 'high'
      });

      toast({
        title: "Unexpected Error",
        description: "An unexpected error occurred. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <div className={`bg-white/5 backdrop-blur-sm rounded-3xl p-8 border border-white/10 ${className}`}>
      <div className="flex items-center gap-2 mb-6">
        <Shield className="h-5 w-5 text-green-400" />
        <h2 className="text-2xl font-bold text-white">Secure Contact Form</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="name" className="text-white">Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleInputChange("name", e.target.value)}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
              required
              maxLength={100}
            />
            {errors.name && <p className="text-red-400 text-sm mt-1">{errors.name}</p>}
          </div>
          
          <div>
            <Label htmlFor="email" className="text-white">Email *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange("email", e.target.value)}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
              required
              maxLength={254}
            />
            {errors.email && <p className="text-red-400 text-sm mt-1">{errors.email}</p>}
          </div>
          
          <div>
            <Label htmlFor="phone" className="text-white">Phone</Label>
            <Input
              id="phone"
              value={formData.phone}
              onChange={(e) => handleInputChange("phone", e.target.value)}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
              maxLength={20}
            />
            {errors.phone && <p className="text-red-400 text-sm mt-1">{errors.phone}</p>}
          </div>
          
          <div>
            <Label htmlFor="company" className="text-white">Company</Label>
            <Input
              id="company"
              value={formData.company}
              onChange={(e) => handleInputChange("company", e.target.value)}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
              maxLength={100}
            />
            {errors.company && <p className="text-red-400 text-sm mt-1">{errors.company}</p>}
          </div>
        </div>

        <div>
          <Label className="text-white">Solution Interest</Label>
          <Select value={formData.solution_type} onValueChange={(value) => handleInputChange("solution_type", value)}>
            <SelectTrigger className="bg-white/10 border-white/20 text-white">
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
          <Label htmlFor="subject" className="text-white">Subject</Label>
          <Input
            id="subject"
            value={formData.subject}
            onChange={(e) => handleInputChange("subject", e.target.value)}
            className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
            maxLength={200}
          />
          {errors.subject && <p className="text-red-400 text-sm mt-1">{errors.subject}</p>}
        </div>

        <div>
          <Label htmlFor="message" className="text-white">Message *</Label>
          <Textarea
            id="message"
            value={formData.message}
            onChange={(e) => handleInputChange("message", e.target.value)}
            className="bg-white/10 border-white/20 text-white placeholder:text-white/50 min-h-[120px]"
            placeholder="Tell us about your needs..."
            required
            maxLength={2000}
          />
          <div className="flex justify-between items-center mt-1">
            {errors.message && <p className="text-red-400 text-sm">{errors.message}</p>}
            <p className="text-white/50 text-sm">{formData.message.length}/2000</p>
          </div>
        </div>

        <Button
          type="submit"
          disabled={isSubmitting || isBlocked}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 rounded-full font-semibold text-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-300 hover:scale-105 disabled:opacity-50"
        >
          {isSubmitting ? "Sending..." : isBlocked ? "Rate Limited" : "Send Secure Message"}
        </Button>
        
        <p className="text-white/60 text-sm text-center">
          <Shield className="inline h-4 w-4 mr-1" />
          Your data is protected with advanced security measures
        </p>
      </form>
    </div>
  );
};
