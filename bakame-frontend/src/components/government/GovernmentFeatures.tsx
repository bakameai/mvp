
import { Shield, Users, Phone, Building } from "lucide-react";

const GovernmentFeatures = () => {
  const features = [
    {
      icon: Shield,
      title: "Secure by Design",
      description: "Government-grade security with end-to-end encryption and compliance with data protection regulations.",
      delay: "0s"
    },
    {
      icon: Users,
      title: "Universal Access",
      description: "Works on any phone, in any language, ensuring all citizens can access government services.",
      delay: "0.1s"
    },
    {
      icon: Phone,
      title: "Always Available",
      description: "24/7 service availability, even during emergencies or infrastructure failures.",
      delay: "0.2s"
    },
    {
      icon: Building,
      title: "Scalable Infrastructure",
      description: "Scales from local municipalities to national deployments with consistent performance.",
      delay: "0.3s"
    }
  ];

  return (
    <div className="mb-20">
      <h2 className="text-3xl font-bold mb-12 text-center animate-fade-in text-foreground">How Bakame AI Serves Citizens</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((item, index) => (
          <div 
            key={index}
            className="bg-card/50 backdrop-blur-sm rounded-xl p-6 border border-border hover:border-border/50 transition-all duration-500 hover:scale-105 hover:bg-card animate-fade-in group cursor-pointer"
            style={{animationDelay: item.delay}}
          >
            <div className="w-12 h-12 bg-muted/50 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
              <item.icon className="w-6 h-6 text-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-3 text-foreground">{item.title}</h3>
            <p className="text-muted-foreground text-sm group-hover:text-foreground transition-colors duration-300">
              {item.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GovernmentFeatures;
