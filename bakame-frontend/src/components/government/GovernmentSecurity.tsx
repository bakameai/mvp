
import { Shield, Building } from "lucide-react";

const GovernmentSecurity = () => {
  return (
    <div className="mb-20">
      <h2 className="text-3xl font-bold mb-12 text-center animate-fade-in text-foreground">Security & Compliance</h2>
      <div className="bg-card/50 backdrop-blur-sm rounded-xl p-8 border border-border hover:border-border/50 transition-all duration-500 animate-fade-in">
        <div className="grid md:grid-cols-2 gap-8">
          <div className="animate-fade-in" style={{animationDelay: '0.2s'}}>
            <h3 className="text-xl font-semibold mb-4 text-foreground">Data Protection</h3>
            <ul className="space-y-3 text-muted-foreground">
              {[
                "End-to-end encryption for all voice data",
                "GDPR and local data protection compliance",
                "On-premise deployment options",
                "Regular security audits and updates"
              ].map((item, index) => (
                <li key={index} className="flex items-start hover:text-foreground transition-colors duration-300" style={{animationDelay: `${0.3 + index * 0.1}s`}}>
                  <Shield className="w-4 h-4 mt-1 mr-3 text-foreground flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="animate-fade-in" style={{animationDelay: '0.4s'}}>
            <h3 className="text-xl font-semibold mb-4 text-foreground">Government Standards</h3>
            <ul className="space-y-3 text-muted-foreground">
              {[
                "Accessibility compliance (WCAG)",
                "Multi-language support requirements",
                "Disaster recovery and continuity",
                "Audit trails and reporting"
              ].map((item, index) => (
                <li key={index} className="flex items-start hover:text-foreground transition-colors duration-300" style={{animationDelay: `${0.5 + index * 0.1}s`}}>
                  <Building className="w-4 h-4 mt-1 mr-3 text-foreground flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GovernmentSecurity;
