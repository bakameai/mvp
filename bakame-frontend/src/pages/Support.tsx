import { useState } from "react";
import { ChevronDown, ChevronUp, Mail, Phone, MessageCircle, Book, Users, Building, Shield } from "lucide-react";

const Support = () => {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const faqs = [
    {
      question: "What is Bakame AI and how does it work?",
      answer: "Bakame AI is an offline-capable IVR (Interactive Voice Response) system that provides AI-powered communication solutions. Our technology works without internet connectivity, making it perfect for areas with limited infrastructure. We specialize in English language education and voice-based interactions in Kinyarwanda and other local languages."
    },
    {
      question: "How can I contribute to the Kinyarwanda dataset project?",
      answer: "We need your help to collect 455,000 hours of Kinyarwanda audio data. You can contribute by participating in our IVR demo, recording voice samples, or joining our community contribution program. Visit our IVR demo page to get started."
    },
    {
      question: "What are the system requirements for Bakame AI?",
      answer: "Our IVR system is designed to work on basic phone infrastructure. For educational institutions, we support standard telephone systems. For enterprise and government deployments, we provide detailed technical specifications during consultation."
    },
    {
      question: "How do I schedule a demo for my organization?",
      answer: "Contact us at happy@bakame.org with your organization details, use case, and preferred demo time. We offer specialized demos for education, enterprise, and government sectors."
    },
    {
      question: "What languages does Bakame AI support?",
      answer: "Currently, we support English and are actively developing Kinyarwanda capabilities. Our goal is to expand to other low-resource languages in the Global South. Contact us for specific language requirements."
    },
    {
      question: "Is my data secure with Bakame AI?",
      answer: "Yes, we implement enterprise-grade security measures. For government and enterprise clients, we offer additional security protocols and can deploy on-premises solutions. All voice data is processed securely and stored according to international privacy standards."
    },
    {
      question: "What pricing plans do you offer?",
      answer: "We offer tiered pricing based on usage and deployment type. Educational institutions receive special pricing. Contact us for a custom quote based on your specific needs and scale."
    },
    {
      question: "Can Bakame AI work offline?",
      answer: "Yes! This is one of our key features. Our IVR system is designed to work in areas with limited or no internet connectivity, making it ideal for rural areas and developing regions."
    }
  ];

  const contactMethods = [
    {
      icon: Mail,
      title: "Email Support",
      description: "Get help via email within 24 hours",
      contact: "happy@bakame.org",
      action: "mailto:happy@bakame.org"
    },
    {
      icon: Phone,
      title: "Schedule a Call",
      description: "Book a consultation with our team",
      contact: "Schedule Demo",
      action: "mailto:happy@bakame.org?subject=Schedule Demo Request"
    },
    {
      icon: MessageCircle,
      title: "Community Support",
      description: "Join our community discussions",
      contact: "Join Discord",
      action: "#"
    }
  ];

  const resources = [
    {
      icon: Book,
      title: "Documentation",
      description: "Technical guides and API documentation",
      items: ["Getting Started Guide", "IVR Setup Manual", "API Reference", "Best Practices"]
    },
    {
      icon: Users,
      title: "Educational Resources",
      description: "Resources for schools and educators",
      items: ["Curriculum Integration", "Teacher Training", "Student Assessment", "Deployment Guide"]
    },
    {
      icon: Building,
      title: "Enterprise & Government",
      description: "Enterprise-grade documentation",
      items: ["Security Compliance", "Scalability Guide", "Custom Deployment", "SLA Information"]
    }
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 md:p-8 border-b border-border">
        <a href="/" className="text-2xl font-bold">Bakame Ai</a>
        <div className="hidden md:flex space-x-8">
          <a href="/ivr" className="text-muted-foreground hover:text-foreground transition-colors">IVR Demo</a>
          <a href="/blog" className="text-muted-foreground hover:text-foreground transition-colors">Blog</a>
          <a href="/contact" className="text-muted-foreground hover:text-foreground transition-colors">Contact</a>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            Support Center
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Get help with Bakame AI. Find answers, contact support, and access resources for your IVR and AI education needs.
          </p>
        </div>

        {/* Quick Contact */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {contactMethods.map((method, index) => (
            <div key={index} className="bg-card/50 backdrop-blur-sm rounded-2xl p-6 border border-border hover:bg-card/80 transition-all duration-300">
              <method.icon className="w-8 h-8 text-accent mb-4" />
              <h3 className="text-xl font-bold text-foreground mb-2">{method.title}</h3>
              <p className="text-muted-foreground mb-4">{method.description}</p>
              <a 
                href={method.action}
                className="inline-flex items-center text-accent hover:text-accent/80 font-medium"
              >
                {method.contact}
                <ChevronDown className="ml-1 w-4 h-4 rotate-[-90deg]" />
              </a>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-foreground mb-8 text-center">Frequently Asked Questions</h2>
          <div className="max-w-4xl mx-auto space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-card/30 backdrop-blur-sm rounded-lg border border-border overflow-hidden">
                <button
                  onClick={() => toggleFaq(index)}
                  className="w-full flex justify-between items-center p-6 text-left hover:bg-card/50 transition-colors"
                >
                  <span className="font-bold text-foreground text-lg">{faq.question}</span>
                  {openFaq === index ? (
                    <ChevronUp className="w-5 h-5 text-accent flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-accent flex-shrink-0" />
                  )}
                </button>
                {openFaq === index && (
                  <div className="px-6 pb-6">
                    <p className="text-muted-foreground leading-relaxed">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Resources Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-foreground mb-8 text-center">Resources & Documentation</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {resources.map((resource, index) => (
              <div key={index} className="bg-card/30 backdrop-blur-sm rounded-2xl p-6 border border-border">
                <resource.icon className="w-8 h-8 text-secondary mb-4" />
                <h3 className="text-xl font-bold text-foreground mb-2">{resource.title}</h3>
                <p className="text-muted-foreground mb-4">{resource.description}</p>
                <ul className="space-y-2">
                  {resource.items.map((item, itemIndex) => (
                    <li key={itemIndex} className="text-sm text-muted-foreground hover:text-foreground cursor-pointer transition-colors">
                      • {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Emergency Contact */}
        <div className="bg-gradient-to-r from-primary/10 via-secondary/10 to-accent/10 rounded-2xl p-8 text-center border border-accent/20">
          <Shield className="w-12 h-12 text-accent mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-foreground mb-4">Need Immediate Assistance?</h3>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            For urgent technical issues, security concerns, or critical deployment support, contact our priority support team.
          </p>
          <a 
            href="mailto:happy@bakame.org?subject=Urgent Support Request"
            className="inline-flex items-center bg-gradient-to-r from-primary to-secondary text-primary-foreground px-8 py-3 rounded-full font-semibold hover:opacity-90 transition-opacity"
          >
            Contact Priority Support
          </a>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-16 p-6">
        <div className="container mx-auto text-center">
          <p className="text-muted-foreground text-sm">
            © 2025 Bakame AI. All rights reserved. | 
            <a href="/privacy" className="hover:text-foreground ml-1">Privacy</a> | 
            <a href="/terms" className="hover:text-foreground ml-1">Terms</a>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Support;
