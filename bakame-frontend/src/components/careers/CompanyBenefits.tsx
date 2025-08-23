
import { useState, useEffect } from "react";

const CompanyBenefits = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`mb-20 transition-all duration-700 ease-out delay-200 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
      <h2 className="text-3xl font-bold mb-12 text-white">Benefits & perks</h2>
      <div className="grid md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="group hover:translate-x-1 transition-transform duration-200">
            <h3 className="font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">Health & wellness</h3>
            <p className="text-gray-300">Comprehensive medical, dental, and vision coverage</p>
          </div>
          <div className="group hover:translate-x-1 transition-transform duration-200">
            <h3 className="font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">Learning & development</h3>
            <p className="text-gray-300">$3,000 annual budget for conferences and courses</p>
          </div>
          <div className="group hover:translate-x-1 transition-transform duration-200">
            <h3 className="font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">Innovation time</h3>
            <p className="text-gray-300">20% time for personal projects and research</p>
          </div>
        </div>
        <div className="space-y-6">
          <div className="group hover:translate-x-1 transition-transform duration-200">
            <h3 className="font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">Flexible work</h3>
            <p className="text-gray-300">Remote-first with flexible hours</p>
          </div>
          <div className="group hover:translate-x-1 transition-transform duration-200">
            <h3 className="font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">Equipment</h3>
            <p className="text-gray-300">Top-tier equipment plus home office setup</p>
          </div>
          <div className="group hover:translate-x-1 transition-transform duration-200">
            <h3 className="font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">Team events</h3>
            <p className="text-gray-300">Quarterly gatherings and annual retreats</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyBenefits;
