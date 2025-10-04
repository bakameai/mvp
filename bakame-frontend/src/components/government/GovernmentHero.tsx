
import { Building } from "lucide-react";

const GovernmentHero = () => {
  return (
    <div className="text-center mb-16">
      <div className="w-16 h-16 bg-muted/50 rounded-2xl flex items-center justify-center mx-auto mb-6">
        <Building className="w-8 h-8 text-foreground" />
      </div>
      <h1 className="text-5xl md:text-6xl font-bold mb-6 text-foreground animate-fade-in" style={{animationDelay: '0.2s'}}>
        Government Solutions
      </h1>
      <p className="text-xl text-muted-foreground max-w-3xl mx-auto animate-fade-in" style={{animationDelay: '0.4s'}}>
        Secure, accessible, and reliable IVR systems that bring government services directly to citizens, regardless of location or connectivity.
      </p>
    </div>
  );
};

export default GovernmentHero;
