
import { useState, useEffect } from "react";
import TypingAnimation from "@/components/TypingAnimation";

const CareersHero = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [titleHovered, setTitleHovered] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`text-center mb-20 transition-all duration-700 ease-out ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
      <h1 
        className={`text-5xl md:text-6xl font-bold mb-6 leading-tight transition-all duration-300 cursor-pointer ${
          titleHovered ? 'text-blue-400 scale-105' : 'text-white'
        }`}
        onMouseEnter={() => setTitleHovered(true)}
        onMouseLeave={() => setTitleHovered(false)}
      >
        <TypingAnimation 
          text="Join us in building the future of communication"
          speed={120}
        />
      </h1>
      <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
        Help us create AI-powered communication systems that work everywhere, 
        for everyone, regardless of infrastructure limitations.
      </p>
    </div>
  );
};

export default CareersHero;
