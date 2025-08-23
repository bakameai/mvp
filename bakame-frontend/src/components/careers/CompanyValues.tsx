
import { useState, useEffect } from "react";

const CompanyValues = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const values = [{
    title: "Impact-driven",
    description: "We're building technology that connects people regardless of infrastructure limitations."
  }, {
    title: "Collaborative",
    description: "We believe diverse perspectives drive innovation and build truly accessible solutions."
  }, {
    title: "Curious",
    description: "We invest in continuous learning through research, conferences, and dedicated innovation time."
  }, {
    title: "Excellence",
    description: "We maintain the highest standards in everything we do, from code quality to user experience."
  }];

  return (
    <div className={`mb-20 transition-all duration-700 ease-out delay-100 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
      <h2 className="text-3xl font-bold mb-12 text-white">Our values</h2>
      <div className="grid md:grid-cols-2 gap-8">
        {values.map((value, index) => (
          <div 
            key={index} 
            className="group p-6 rounded-lg bg-gray-800/30 border border-gray-700/50 hover:bg-gray-800/50 hover:border-gray-600/50 transition-all duration-300 cursor-default hover:scale-105"
            style={{
              animationDelay: `${index * 100}ms`
            }}
          >
            <h3 className="text-lg font-semibold text-white mb-3 group-hover:text-blue-400 transition-colors duration-200">
              {value.title}
            </h3>
            <p className="text-gray-300 leading-relaxed">{value.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CompanyValues;
