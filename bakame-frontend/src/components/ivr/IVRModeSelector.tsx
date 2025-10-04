
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Mic, Wifi, MessageSquare, Phone, Headphones, Type } from 'lucide-react';
import { IVRMode } from '@/hooks/useIVRClient';

interface IVRModeSelectorProps {
  onModeSelect: (mode: IVRMode) => void;
  isConnecting: boolean;
}

const IVRModeSelector: React.FC<IVRModeSelectorProps> = ({ onModeSelect, isConnecting }) => {
  const modes = [
    {
      id: 'webrtc' as IVRMode,
      title: 'Voice Learning (WebRTC)',
      description: 'Real-time voice conversation with AI tutor',
      icon: <Phone className="w-6 h-6" />,
      features: ['Real-time voice chat', 'Pronunciation help', 'Natural conversation'],
      recommended: true,
      gradient: 'from-[#ff914d] to-[#0d4dcc]'
    },
    {
      id: 'websocket' as IVRMode,
      title: 'Interactive Chat (WebSocket)',
      description: 'Fast, responsive text and voice interactions',
      icon: <Headphones className="w-6 h-6" />,
      features: ['Low latency', 'Mixed voice/text', 'Enhanced features'],
      recommended: false,
      gradient: 'from-[#0d4dcc] to-[#ff914d]'
    },
    {
      id: 'http' as IVRMode,
      title: 'Text Learning (HTTP)',
      description: 'Traditional text-based English learning',
      icon: <Type className="w-6 h-6" />,
      features: ['Text-based chat', 'Grammar focus', 'Vocabulary building'],
      recommended: false,
      gradient: 'from-[#081a2e] to-[#0d4dcc]'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-[#ff914d] to-[#0d4dcc] bg-clip-text text-transparent">
          Choose Your Learning Mode
        </h2>
        <p className="text-white/80 text-lg">
          Select how you'd like to practice English with Bakame AI
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {modes.map((mode) => (
          <Card 
            key={mode.id} 
            className="bg-[#081a2e]/80 backdrop-blur-md border-white/20 hover:border-white/40 transition-all duration-300 hover:scale-105"
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-full bg-gradient-to-r ${mode.gradient}`}>
                  {mode.icon}
                </div>
                {mode.recommended && (
                  <Badge className="bg-gradient-to-r from-[#ff914d] to-[#0d4dcc] text-white border-none">
                    Recommended
                  </Badge>
                )}
              </div>

              <h3 className="text-xl font-semibold text-white mb-2">{mode.title}</h3>
              <p className="text-white/70 text-sm mb-4">{mode.description}</p>

              <div className="space-y-2 mb-6">
                {mode.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm text-white/80">
                    <div className="w-1 h-1 bg-gradient-to-r from-[#ff914d] to-[#0d4dcc] rounded-full"></div>
                    {feature}
                  </div>
                ))}
              </div>

              <Button
                onClick={() => onModeSelect(mode.id)}
                disabled={isConnecting}
                className={`w-full bg-gradient-to-r ${mode.gradient} hover:opacity-90 text-white`}
              >
                {isConnecting ? 'Connecting...' : 'Start Learning'}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="text-center mt-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#ff914d]/10 to-[#0d4dcc]/10 rounded-full border border-white/20">
          <Wifi className="w-4 h-4 text-[#0d4dcc]" />
          <span className="text-sm text-foreground">Connected to Devin Infrastructure</span>
        </div>
      </div>
    </div>
  );
};

export default IVRModeSelector;
