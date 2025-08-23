
import React from 'react';
import UnifiedBakameInterface from '@/components/bakame/UnifiedBakameInterface';

const IVR = () => {
  return (
    <div className="min-h-screen bg-background text-foreground relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-accent/20 to-secondary/20"></div>
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, hsl(var(--foreground) / 0.15) 1px, transparent 0)`,
          backgroundSize: '40px 40px'
        }}></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-20 flex justify-between items-center p-6 md:p-8 backdrop-blur-sm bg-card/50 border-b border-border">
        <a href="/" className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent hover:from-accent hover:to-primary transition-all duration-500">
          Bakame AI
        </a>
        <div className="hidden md:flex space-x-8">
          <a href="/" className="text-muted-foreground hover:text-foreground transition-colors">Home</a>
          <a href="/blog" className="text-muted-foreground hover:text-foreground transition-colors">Blog</a>
        </div>
      </nav>

      {/* Main content */}
      <div className="relative z-10">
        <UnifiedBakameInterface />
      </div>
    </div>
  );
};

export default IVR;
