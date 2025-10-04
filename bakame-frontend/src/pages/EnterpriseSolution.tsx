import { useNavigate } from "react-router-dom";
import { ArrowLeft, Building2, Shield, Clock, BarChart3 } from "lucide-react";
import { useState, useEffect } from "react";
const EnterpriseSolution = () => {
  const navigate = useNavigate();
  const [activeUseCase, setActiveUseCase] = useState<number | null>(null);
  const [statsVisible, setStatsVisible] = useState(false);
  const [animatedStats, setAnimatedStats] = useState({
    cost: 0,
    response: 0,
    uptime: 0,
    satisfaction: 0
  });

  // Animate counters when stats section becomes visible
  useEffect(() => {
    if (statsVisible) {
      const duration = 2000;
      const steps = 60;
      const stepTime = duration / steps;
      let step = 0;
      const timer = setInterval(() => {
        step++;
        const progress = step / steps;
        setAnimatedStats({
          cost: Math.floor(60 * progress),
          response: Math.floor(40 * progress),
          uptime: Math.floor(99.9 * progress * 10) / 10,
          satisfaction: Math.floor(85 * progress)
        });
        if (step >= steps) {
          clearInterval(timer);
        }
      }, stepTime);
      return () => clearInterval(timer);
    }
  }, [statsVisible]);

  // Observer for stats animation
  useEffect(() => {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setStatsVisible(true);
        }
      });
    }, {
      threshold: 0.3
    });
    const statsElement = document.getElementById('stats-section');
    if (statsElement) observer.observe(statsElement);
    return () => observer.disconnect();
  }, []);
  const toggleUseCase = (index: number) => {
    setActiveUseCase(activeUseCase === index ? null : index);
  };
  const useCases = [{
    title: "Customer Service Automation",
    color: "purple",
    description: "Handle customer inquiries, support tickets, and service requests 24/7 with intelligent voice interactions. Reduce wait times and improve customer satisfaction while cutting operational costs.",
    items: [{
      title: "Order Processing",
      desc: "Automated order taking, status updates, and tracking information"
    }, {
      title: "Technical Support",
      desc: "Intelligent troubleshooting and issue resolution guidance"
    }, {
      title: "Account Management",
      desc: "Balance inquiries, payment processing, and account updates"
    }]
  }, {
    title: "Internal Communications",
    color: "blue",
    description: "Streamline internal processes with voice-activated systems for HR, IT support, facilities management, and employee information systems that work across all locations.",
    items: [{
      title: "HR Services",
      desc: "Leave requests, policy information, and benefits inquiries"
    }, {
      title: "IT Helpdesk",
      desc: "Password resets, system status, and technical assistance"
    }, {
      title: "Facilities",
      desc: "Room bookings, maintenance requests, and facility information"
    }]
  }, {
    title: "Sales & Lead Management",
    color: "green",
    description: "Capture leads, qualify prospects, and provide product information through intelligent voice interactions. Integrate with your CRM for seamless lead nurturing and follow-up processes.",
    items: [{
      title: "Lead Qualification",
      desc: "Automated prospect screening and scoring"
    }, {
      title: "Product Info",
      desc: "Detailed product specifications and pricing"
    }, {
      title: "Appointment Setting",
      desc: "Automated scheduling and calendar integration"
    }]
  }];
  return <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 md:p-8 border-b border-border animate-fade-in">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate('/')} className="p-2 hover:bg-muted rounded-lg transition-all duration-300 hover:scale-110 group">
            <ArrowLeft className="w-5 h-5 group-hover:transform group-hover:-translate-x-1 transition-transform duration-300" />
          </button>
          <div className="text-2xl font-bold">Bakame Ai</div>
        </div>
        <div className="hidden md:flex space-x-8">
          <a href="/blog" className="text-muted-foreground hover:text-foreground transition-all duration-300 hover:scale-105 relative after:content-[''] after:absolute after:w-full after:scale-x-0 after:h-0.5 after:bottom-0 after:left-0 after:bg-foreground after:origin-bottom-right after:transition-transform after:duration-300 hover:after:scale-x-100 hover:after:origin-bottom-left">Blog</a>
          
          <a href="/team" className="text-muted-foreground hover:text-foreground transition-all duration-300 hover:scale-105 relative after:content-[''] after:absolute after:w-full after:scale-x-0 after:h-0.5 after:bottom-0 after:left-0 after:bg-foreground after:origin-bottom-right after:transition-transform after:duration-300 hover:after:scale-x-100 hover:after:origin-bottom-left">Team</a>
          
        </div>
      </nav>

      <div className="container mx-auto px-6 py-20">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="w-16 h-16 bg-muted/50 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Building2 className="w-8 h-8 text-foreground" />
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 text-foreground animate-fade-in" style={{
          animationDelay: '0.2s'
        }}>
            Enterprise Solutions
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto animate-fade-in" style={{
          animationDelay: '0.4s'
        }}>
            Scalable, secure, and reliable IVR systems that transform customer service and internal communications for businesses of all sizes.
          </p>
        </div>

        {/* How It Works Section */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold mb-12 text-center animate-fade-in">How Bakame AI Powers Your Business</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[{
            icon: Shield,
            title: "Enterprise Security",
            description: "Bank-level encryption and security protocols with on-premise deployment options for complete data control.",
            delay: "0s"
          }, {
            icon: Clock,
            title: "24/7 Availability",
            description: "Always-on customer service that works even during internet outages or network failures.",
            delay: "0.1s"
          }, {
            icon: BarChart3,
            title: "Advanced Analytics",
            description: "Real-time insights and reporting to optimize customer interactions and business processes.",
            delay: "0.2s"
          }, {
            icon: Building2,
            title: "Seamless Integration",
            description: "Easy integration with existing CRM, ERP, and business systems through robust APIs.",
            delay: "0.3s"
          }].map((item, index) => <div key={index} className="bg-card/50 backdrop-blur-sm rounded-xl p-6 border border-border hover:border-border/50 transition-all duration-300 hover:bg-card animate-fade-in group cursor-pointer" style={{
            animationDelay: item.delay
          }}>
                <div className="w-12 h-12 bg-muted/50 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <item.icon className="w-6 h-6 text-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-3 group-hover:text-foreground transition-colors duration-300">{item.title}</h3>
                <p className="text-muted-foreground text-sm group-hover:text-foreground transition-colors duration-300">
                  {item.description}
                </p>
              </div>)}
          </div>
        </div>

        {/* Use Cases Section */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold mb-12 text-center animate-fade-in">Enterprise Use Cases</h2>
          <div className="space-y-6">
            {useCases.map((useCase, index) => <div key={index} className="bg-card/50 backdrop-blur-sm rounded-xl border border-border hover:border-border/50 transition-all duration-300 animate-fade-in overflow-hidden" style={{
            animationDelay: `${index * 0.1}s`
          }}>
                <div className="p-8 cursor-pointer group" onClick={() => toggleUseCase(index)}>
                  <div className="flex items-center justify-between">
                    <h3 className="text-2xl font-semibold text-foreground group-hover:text-muted-foreground transition-colors duration-300">
                      {useCase.title}
                    </h3>
                    <div className={`transform transition-transform duration-300 ${activeUseCase === index ? 'rotate-180' : ''}`}>
                      <svg className="w-6 h-6 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>
                  <p className="text-muted-foreground mt-4 group-hover:text-foreground transition-colors duration-300">
                    {useCase.description}
                  </p>
                </div>
                
                <div className={`overflow-hidden transition-all duration-500 ${activeUseCase === index ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
                  <div className="px-8 pb-8">
                    <div className="grid md:grid-cols-3 gap-4 pt-4 border-t border-border">
                      {useCase.items.map((item, itemIndex) => <div key={itemIndex} className="bg-muted/50 rounded-lg p-4 hover:bg-muted transition-all duration-300" style={{
                    animationDelay: `${itemIndex * 0.1}s`
                  }}>
                          <h4 className="font-semibold text-foreground mb-2">{item.title}</h4>
                          <p className="text-muted-foreground text-sm">{item.desc}</p>
                        </div>)}
                    </div>
                  </div>
                </div>
              </div>)}
          </div>
        </div>

        {/* ROI Section */}
        <div className="mb-20" id="stats-section">
          <h2 className="text-3xl font-bold mb-12 text-center animate-fade-in">Return on Investment</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[{
            value: animatedStats.cost,
            suffix: "%",
            label: "Cost Reduction"
          }, {
            value: animatedStats.response,
            suffix: "%",
            label: "Faster Response"
          }, {
            value: animatedStats.uptime,
            suffix: "%",
            label: "Uptime"
          }, {
            value: animatedStats.satisfaction,
            suffix: "%",
            label: "Customer Satisfaction"
          }].map((stat, index) => <div key={index} className="text-center bg-card/50 backdrop-blur-sm rounded-xl p-6 border border-border hover:border-border/50 transition-all duration-300 hover:bg-card group animate-fade-in" style={{
            animationDelay: `${index * 0.1}s`
          }}>
                <div className="text-3xl font-bold text-foreground mb-2 group-hover:scale-110 transition-transform duration-300">
                  {stat.value}{stat.suffix}
                </div>
                <div className="text-muted-foreground group-hover:text-foreground transition-colors duration-300">{stat.label}</div>
              </div>)}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-card/50 backdrop-blur-sm rounded-3xl p-12 border border-border hover:border-border/50 transition-all duration-300 animate-fade-in">
          <h2 className="text-3xl font-bold mb-6">Scale Your Business with AI</h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join leading enterprises already using Bakame AI to transform their customer experience and operational efficiency.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button onClick={() => navigate('/signup')} className="bg-foreground text-background px-8 py-4 rounded-full font-semibold text-lg hover:bg-muted-foreground transition-all duration-300 hover:scale-105 group relative overflow-hidden">
              <span className="relative z-10">Request Free Trial</span>
            </button>
            <button className="border border-border text-foreground px-8 py-4 rounded-full font-semibold text-lg hover:bg-muted transition-all duration-300 hover:scale-105 hover:border-muted-foreground hover:shadow-lg hover:shadow-muted/25">
              Enterprise Demo
            </button>
          </div>
        </div>
      </div>
    </div>;
};
export default EnterpriseSolution;