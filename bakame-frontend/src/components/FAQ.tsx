
import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

const FAQ = () => {
  const [openItems, setOpenItems] = useState<number[]>([]);

  const toggleItem = (index: number) => {
    setOpenItems(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  const faqItems = [
    {
      question: "What makes your offline AI different from cloud-based solutions?",
      answer: "Our system runs entirely on local hardware without requiring internet connectivity. This means your voice services remain operational during network outages, natural disasters, or cyber attacks. All processing happens on-premises, ensuring complete data privacy and security."
    },
    {
      question: "How does the beta program work?",
      answer: "We're currently working with select partners to test and refine our offline AI technology. Beta participants get early access to our platform, direct support from our team, and the opportunity to influence product development. Join our waitlist to be considered for the next beta phase."
    },
    {
      question: "What hardware requirements are needed?",
      answer: "Our solution is designed to run on standard server hardware that most organizations already have. We'll work with you to assess your specific requirements and recommend the optimal setup for your use case during the consultation process."
    },
    {
      question: "How long does implementation take?",
      answer: "Implementation timelines vary based on your specific requirements and existing infrastructure. During our beta phase, we work closely with each partner to ensure a smooth deployment. Typical implementations range from a few weeks to a few months."
    },
    {
      question: "What kind of support do you provide?",
      answer: "As a growing startup, we provide personalized support to all our beta partners. This includes technical guidance, implementation assistance, and ongoing support. Our team is committed to ensuring your success with our platform."
    },
    {
      question: "Is this technology proven?",
      answer: "We're a startup building innovative offline AI technology. While we're still in beta, we're working with select partners to validate and improve our solution. Our approach focuses on reliability and security for critical infrastructure applications."
    },
    {
      question: "What are the costs involved?",
      answer: "Pricing varies based on your specific needs and deployment size. During the beta phase, we offer flexible arrangements for early partners. Contact us to discuss your requirements and learn about our current pricing structure."
    },
    {
      question: "Can you integrate with our existing phone systems?",
      answer: "Yes, our solution is designed to integrate with standard telephony infrastructure. We support various protocols and can work with your existing PBX systems, SIP trunks, and other telephony equipment."
    }
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center text-foreground">
        Frequently Asked Questions
      </h2>
      
      <div className="space-y-4">
        {faqItems.map((item, index) => (
          <div 
            key={index}
            className="bg-card border-border backdrop-blur-sm rounded-lg border overflow-hidden"
          >
            <button
              onClick={() => toggleItem(index)}
              className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-muted/50 transition-all duration-200"
            >
              <span className="text-foreground font-semibold pr-4">
                {item.question}
              </span>
              {openItems.includes(index) ? (
                <ChevronUp className="h-5 w-5 text-muted-foreground flex-shrink-0" />
              ) : (
                <ChevronDown className="h-5 w-5 text-muted-foreground flex-shrink-0" />
              )}
            </button>
            
            {openItems.includes(index) && (
              <div className="px-6 pb-4">
                <p className="text-muted-foreground leading-relaxed">
                  {item.answer}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default FAQ;
