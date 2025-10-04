
import { useState, useEffect } from 'react';

interface TypingAnimationProps {
  text: string;
  speed?: number;
  pauseDuration?: number;
  className?: string;
}

const TypingAnimation = ({ text, speed = 150, pauseDuration = 2000, className = "" }: TypingAnimationProps) => {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPausing, setIsPausing] = useState(false);

  useEffect(() => {
    if (isPausing) {
      // During pause, wait then reset for next cycle
      const pauseTimer = setTimeout(() => {
        setDisplayText('');
        setCurrentIndex(0);
        setIsPausing(false);
      }, pauseDuration);

      return () => clearTimeout(pauseTimer);
    } else if (currentIndex < text.length) {
      // Continue typing
      const timer = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timer);
    } else {
      // Finished typing, start pause
      setIsPausing(true);
    }
  }, [currentIndex, text, speed, pauseDuration, isPausing]);

  return (
    <span className={className}>
      {displayText}
      <span className="animate-pulse text-blue-400">|</span>
    </span>
  );
};

export default TypingAnimation;
