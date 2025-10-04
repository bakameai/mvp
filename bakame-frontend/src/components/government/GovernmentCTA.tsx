
import { useNavigate } from "react-router-dom";

const GovernmentCTA = () => {
  const navigate = useNavigate();

  return (
    <div className="text-center bg-card/50 backdrop-blur-sm rounded-3xl p-12 border border-border hover:border-border/50 transition-all duration-500 animate-fade-in">
      <h2 className="text-3xl font-bold mb-6 text-foreground">Serve Your Citizens Better</h2>
      <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
        Join government agencies already using Bakame AI to provide accessible, secure, and reliable services to all citizens.
      </p>
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button 
          onClick={() => navigate('/government-demo')}
          className="bg-foreground text-background px-8 py-4 rounded-full font-semibold text-lg hover:bg-muted-foreground transition-all duration-300 hover:scale-105"
        >
          Request Pilot Program
        </button>
        <button className="border border-border text-foreground px-8 py-4 rounded-full font-semibold text-lg hover:bg-muted transition-all duration-300 hover:scale-105 hover:border-border/50">
          Government Demo
        </button>
      </div>
    </div>
  );
};

export default GovernmentCTA;
