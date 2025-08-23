
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { authAPI } from '@/services/api';
import { useAnalytics } from '@/components/analytics/AnalyticsProvider';

const GovernmentDemo = () => {
  const { toast } = useToast();
  const { trackEvent } = useAnalytics();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    organization: '',
    position: '',
    agencyType: '',
    citizenSize: '',
    currentSystems: '',
    primaryUseCase: '',
    timeline: '',
    budget: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Use type assertion for the new table
      const { error } = await (supabase as any)
        .from('government_demo_requests')
        .insert([{
          first_name: formData.firstName,
          last_name: formData.lastName,
          email: formData.email,
          phone: formData.phone,
          organization: formData.organization,
          position: formData.position,
          agency_type: formData.agencyType,
          citizen_size: formData.citizenSize,
          current_systems: formData.currentSystems,
          primary_use_case: formData.primaryUseCase,
          timeline: formData.timeline,
          budget: formData.budget,
          status: 'pending'
        }]);

      if (error) {
        console.error('Error submitting government demo request:', error);
        toast({
          title: "Error",
          description: "Failed to submit your request. Please try again.",
          variant: "destructive",
        });
      } else {
        trackEvent('government_demo_request', { agency_type: formData.agencyType });
        toast({
          title: "Request Submitted",
          description: "Thank you! We'll contact you within 24 hours to schedule your demo.",
        });
        
        // Reset form
        setFormData({
          firstName: '',
          lastName: '',
          email: '',
          phone: '',
          organization: '',
          position: '',
          agencyType: '',
          citizenSize: '',
          currentSystems: '',
          primaryUseCase: '',
          timeline: '',
          budget: ''
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 via-purple-900 to-slate-900">
      <div className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Government AI Demo
            </h1>
            <p className="text-xl text-white/80 mb-8">
              See how Bakame AI can transform citizen services and internal operations
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
            <h2 className="text-2xl font-bold text-white mb-6">Request Your Pilot Demo</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="firstName" className="text-white">First Name *</Label>
                  <Input
                    id="firstName"
                    value={formData.firstName}
                    onChange={(e) => handleInputChange("firstName", e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="lastName" className="text-white">Last Name *</Label>
                  <Input
                    id="lastName"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange("lastName", e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                    required
                  />
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
                  />
                </div>
                <div>
                  <Label htmlFor="phone" className="text-white">Phone</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => handleInputChange("phone", e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                  />
                </div>
                <div>
                  <Label htmlFor="organization" className="text-white">Organization *</Label>
                  <Input
                    id="organization"
                    value={formData.organization}
                    onChange={(e) => handleInputChange("organization", e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="position" className="text-white">Position/Title *</Label>
                  <Input
                    id="position"
                    value={formData.position}
                    onChange={(e) => handleInputChange("position", e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                    required
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label className="text-white">Agency Type *</Label>
                  <Select value={formData.agencyType} onValueChange={(value) => handleInputChange("agencyType", value)}>
                    <SelectTrigger className="bg-white/10 border-white/20 text-white">
                      <SelectValue placeholder="Select agency type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="federal">Federal Agency</SelectItem>
                      <SelectItem value="state">State Government</SelectItem>
                      <SelectItem value="local">Local Government</SelectItem>
                      <SelectItem value="municipal">Municipal</SelectItem>
                      <SelectItem value="county">County</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="text-white">Citizens Served</Label>
                  <Select value={formData.citizenSize} onValueChange={(value) => handleInputChange("citizenSize", value)}>
                    <SelectTrigger className="bg-white/10 border-white/20 text-white">
                      <SelectValue placeholder="Select population size" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="<10k">Less than 10,000</SelectItem>
                      <SelectItem value="10k-50k">10,000 - 50,000</SelectItem>
                      <SelectItem value="50k-100k">50,000 - 100,000</SelectItem>
                      <SelectItem value="100k-500k">100,000 - 500,000</SelectItem>
                      <SelectItem value="500k-1m">500,000 - 1 Million</SelectItem>
                      <SelectItem value=">1m">Over 1 Million</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label className="text-white">Primary Use Case *</Label>
                <Select value={formData.primaryUseCase} onValueChange={(value) => handleInputChange("primaryUseCase", value)}>
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Select primary use case" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="citizen-services">Citizen Services</SelectItem>
                    <SelectItem value="multilingual-support">Multilingual Support</SelectItem>
                    <SelectItem value="document-translation">Document Translation</SelectItem>
                    <SelectItem value="public-meetings">Public Meetings</SelectItem>
                    <SelectItem value="emergency-communications">Emergency Communications</SelectItem>
                    <SelectItem value="internal-operations">Internal Operations</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label className="text-white">Implementation Timeline</Label>
                  <Select value={formData.timeline} onValueChange={(value) => handleInputChange("timeline", value)}>
                    <SelectTrigger className="bg-white/10 border-white/20 text-white">
                      <SelectValue placeholder="Select timeline" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="immediate">Immediate (1-3 months)</SelectItem>
                      <SelectItem value="short-term">Short-term (3-6 months)</SelectItem>
                      <SelectItem value="medium-term">Medium-term (6-12 months)</SelectItem>
                      <SelectItem value="long-term">Long-term (12+ months)</SelectItem>
                      <SelectItem value="exploring">Just exploring</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="text-white">Budget Range</Label>
                  <Select value={formData.budget} onValueChange={(value) => handleInputChange("budget", value)}>
                    <SelectTrigger className="bg-white/10 border-white/20 text-white">
                      <SelectValue placeholder="Select budget range" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="<25k">Under $25,000</SelectItem>
                      <SelectItem value="25k-50k">$25,000 - $50,000</SelectItem>
                      <SelectItem value="50k-100k">$50,000 - $100,000</SelectItem>
                      <SelectItem value="100k-250k">$100,000 - $250,000</SelectItem>
                      <SelectItem value="250k+">$250,000+</SelectItem>
                      <SelectItem value="tbd">To be determined</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="currentSystems" className="text-white">Current Systems & Challenges</Label>
                <Textarea
                  id="currentSystems"
                  value={formData.currentSystems}
                  onChange={(e) => handleInputChange("currentSystems", e.target.value)}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50 min-h-[100px]"
                  placeholder="Tell us about your current systems and any specific challenges you're facing..."
                />
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 rounded-full font-semibold text-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-300 hover:scale-105 disabled:opacity-50"
              >
                {isSubmitting ? "Submitting..." : "Request Demo"}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GovernmentDemo;
