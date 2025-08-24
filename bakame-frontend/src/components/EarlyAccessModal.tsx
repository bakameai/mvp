
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { authAPI } from '@/services/api';
import { useAnalytics } from '@/components/analytics/AnalyticsProvider';
import { CheckCircle, ArrowRight } from 'lucide-react';

interface EarlyAccessModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const EarlyAccessModal = ({ isOpen, onClose }: EarlyAccessModalProps) => {
  const { toast } = useToast();
  const { trackEvent } = useAnalytics();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    company: '',
    productUse: '',
    additionalInfo: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await authAPI.submitEarlyAccess({
        email: formData.email,
        name: formData.name,
        company: formData.company,
        solution_interest: `${formData.productUse} | ${formData.additionalInfo}`
      });

      if (response.success) {
        trackEvent('early_access_request', { 
          product_use: formData.productUse,
          company: formData.company
        });
        
        setStep(3); // Success step
        
        // Reset form after a delay
        setTimeout(() => {
          setFormData({
            email: '',
            name: '',
            company: '',
            productUse: '',
            additionalInfo: ''
          });
          setStep(1);
          onClose();
        }, 3000);
      } else {
        console.error('Error submitting early access request:', response.error);
        toast({
          title: "Error",
          description: response.error || "Failed to submit your request. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error submitting form:', error);
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

  const canProceedToStep2 = formData.email && formData.name && formData.company;
  const canSubmit = canProceedToStep2 && formData.productUse;

  if (step === 3) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-md">
          <div className="text-center py-6">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-2xl font-bold mb-2">Thank You!</h3>
            <p className="text-gray-600 mb-4">
              Your request has been submitted successfully. We'll be in touch soon with early access details.
            </p>
            <div className="text-sm text-gray-500">
              This window will close automatically...
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Request Early Access</DialogTitle>
          <DialogDescription>
            Join the waitlist to be among the first to experience offline AI technology
          </DialogDescription>
        </DialogHeader>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center mb-6">
          <div className="flex items-center space-x-4">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              1
            </div>
            <div className={`w-8 h-1 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              2
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {step === 1 && (
            <>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Full Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    placeholder="Your full name"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email Address *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    placeholder="your@email.com"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="company">Company/Organization *</Label>
                  <Input
                    id="company"
                    value={formData.company}
                    onChange={(e) => handleInputChange("company", e.target.value)}
                    placeholder="Your organization"
                    required
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <Button
                  type="button"
                  onClick={() => setStep(2)}
                  disabled={!canProceedToStep2}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Next <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div className="space-y-4">
                <div>
                  <Label>Primary Use Case *</Label>
                  <Select value={formData.productUse} onValueChange={(value) => handleInputChange("productUse", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="How will you use our product?" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="customer-service">Customer Service</SelectItem>
                      <SelectItem value="education">Education & Training</SelectItem>
                      <SelectItem value="government-services">Government Services</SelectItem>
                      <SelectItem value="healthcare">Healthcare Communication</SelectItem>
                      <SelectItem value="emergency-services">Emergency Services</SelectItem>
                      <SelectItem value="multilingual-support">Multilingual Support</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="additionalInfo">Tell us more about your needs</Label>
                  <Textarea
                    id="additionalInfo"
                    value={formData.additionalInfo}
                    onChange={(e) => handleInputChange("additionalInfo", e.target.value)}
                    placeholder="What specific challenges are you hoping to solve? What's your timeline?"
                    className="min-h-[80px]"
                  />
                </div>
              </div>

              <div className="flex justify-between">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setStep(1)}
                >
                  Back
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmitting || !canSubmit}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isSubmitting ? "Submitting..." : "Request Early Access"}
                </Button>
              </div>
            </>
          )}
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default EarlyAccessModal;
