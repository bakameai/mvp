import { useState, useEffect, useRef } from 'react';

interface AnimatedCounterProps {
  end: string;
  duration?: number;
  className?: string;
}

const AnimatedCounter = ({ end, duration = 10000, className = '' }: AnimatedCounterProps) => {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [shouldPulse, setShouldPulse] = useState(true);
  const countRef = useRef<HTMLDivElement>(null);
  const hasAnimated = useRef(false);

  // Extract numeric part and suffix from the end value
  const getNumericParts = (value: string) => {
    const match = value.match(/^(\d+(?:\.\d+)?)(.*)/);
    if (match) {
      let numeric = parseFloat(match[1]);
      let suffix = match[2];
      
      // Convert K to actual thousands
      if (suffix.includes('K')) {
        numeric = numeric * 1000;
        suffix = suffix.replace('K', '');
      }
      
      return {
        numeric,
        suffix
      };
    }
    return { numeric: 0, suffix: value };
  };

  const { numeric: endValue, suffix } = getNumericParts(end);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated.current) {
          setIsVisible(true);
          hasAnimated.current = true;
        }
      },
      { threshold: 0.1 }
    );

    if (countRef.current) {
      observer.observe(countRef.current);
    }

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    const startTime = Date.now();
    const startValue = 0;

    // Stop pulsing after 5 seconds
    const pulseTimer = setTimeout(() => {
      setShouldPulse(false);
    }, 5000);

    const animate = () => {
      const now = Date.now();
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Different easing function for bounce effect
      const easeOutBounce = (t: number) => {
        if (t < 1 / 2.75) {
          return 7.5625 * t * t;
        } else if (t < 2 / 2.75) {
          return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
        } else if (t < 2.5 / 2.75) {
          return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
        } else {
          return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
        }
      };

      const easedProgress = easeOutBounce(progress);
      const currentValue = startValue + (endValue - startValue) * easedProgress;

      setCount(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setCount(endValue);
      }
    };

    requestAnimationFrame(animate);

    return () => {
      clearTimeout(pulseTimer);
    };
  }, [isVisible, endValue, duration]);

  const formatValue = (value: number) => {
    return Math.floor(value).toString() + suffix;
  };

  return (
    <div ref={countRef} className={`${className} transform transition-all duration-300 hover:scale-110 ${shouldPulse ? 'animate-pulse' : ''}`}>
      {formatValue(count)}
    </div>
  );
};

export default AnimatedCounter;