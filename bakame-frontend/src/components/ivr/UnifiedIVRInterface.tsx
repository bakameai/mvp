
import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useIVRClient } from '@/hooks/useIVRClient';
import IVRModeSelector from './IVRModeSelector';
import IVRAnalyticsDashboard from './IVRAnalyticsDashboard';
import { Phone, PhoneOff, Send, BarChart3, Settings, Mic, MicOff, Volume2 } from 'lucide-react';

const UnifiedIVRInterface: React.FC = () => {
  const {
    session,
    isRecording,
    isSpeaking,
    startSession,
    sendMessage,
    endSession
  } = useIVRClient();

  const [currentInput, setCurrentInput] = useState('');
  const [showAnalytics, setShowAnalytics] = useState(false);

  const handleSendMessage = async () => {
    if (currentInput.trim() && session) {
      await sendMessage(currentInput.trim());
      setCurrentInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getStatusColor = () => {
    if (!session) return 'bg-muted';
    switch (session.status) {
      case 'connected': return isSpeaking ? 'bg-accent animate-pulse' : 'bg-primary';
      case 'connecting': return 'bg-secondary animate-pulse';
      case 'error': return 'bg-destructive';
      default: return 'bg-muted';
    }
  };

  const getConnectionStatus = () => {
    if (!session) return 'Ready to Learn';
    switch (session.status) {
      case 'connected': return `Connected via ${session.mode.toUpperCase()}`;
      case 'connecting': return 'Connecting...';
      case 'error': return 'Connection Error';
      case 'disconnected': return 'Disconnected';
      default: return 'Ready to Learn';
    }
  };

  if (showAnalytics) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="container mx-auto p-6">
          <div className="flex items-center justify-between mb-6">
            <Button
              onClick={() => setShowAnalytics(false)}
              variant="outline"
              className="border-border text-foreground hover:bg-muted"
            >
              ← Back to Chat
            </Button>
          </div>
          <IVRAnalyticsDashboard />
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="container mx-auto p-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Bakame AI - English Learning Platform
            </h1>
            <Button
              onClick={() => setShowAnalytics(true)}
              variant="outline"
              className="border-border text-foreground hover:bg-muted flex items-center gap-2"
            >
              <BarChart3 className="w-4 h-4" />
              Analytics
            </Button>
          </div>
          <IVRModeSelector
            onModeSelect={startSession}
            isConnecting={false}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
            <Badge variant="outline" className="border-border text-foreground">
              {getConnectionStatus()}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={() => setShowAnalytics(true)}
              variant="outline"
              size="sm"
              className="border-border text-foreground hover:bg-muted"
            >
              <BarChart3 className="w-4 h-4" />
            </Button>
            <Button
              onClick={endSession}
              variant="outline"
              size="sm"
              className="border-border text-foreground hover:bg-muted"
            >
              <PhoneOff className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Main Chat Interface */}
        <Card className="bg-card/80 backdrop-blur-md border-border mb-6">
          <CardContent className="p-6">
            {/* Activity Indicators */}
            {session.mode !== 'http' && (
              <div className="flex justify-center gap-6 mb-6">
                <div className={`flex items-center gap-2 ${isRecording ? 'text-primary' : 'text-muted-foreground'}`}>
                  <Mic className={`w-5 h-5 ${isRecording ? 'animate-pulse' : ''}`} />
                  <span className="text-sm">You're Speaking</span>
                </div>
                <div className={`flex items-center gap-2 ${isSpeaking ? 'text-accent' : 'text-muted-foreground'}`}>
                  <Volume2 className={`w-5 h-5 ${isSpeaking ? 'animate-pulse' : ''}`} />
                  <span className="text-sm">AI Teaching</span>
                </div>
              </div>
            )}

            {/* Conversation History */}
            <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
              {session.messages.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-muted-foreground mb-2">
                    Connected via {session.mode.toUpperCase()}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Start your English learning conversation...
                  </div>
                </div>
              ) : (
                session.messages.map((message, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-accent/20 to-primary/10 border border-accent/30 ml-8'
                        : 'bg-gradient-to-r from-primary/20 to-accent/10 border border-primary/30 mr-8'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`text-sm font-medium ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent'
                          : 'bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent'
                      }`}>
                        {message.role === 'user' ? 'You' : 'Bakame AI'}
                      </span>
                      {message.type && (
                        <Badge variant="outline" className="text-xs border-border text-muted-foreground">
                          {message.type}
                        </Badge>
                      )}
                      <span className="text-xs text-muted-foreground">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-foreground">{message.content}</p>
                  </div>
                ))
              )}
            </div>

            {/* Input Area */}
            <div className="flex gap-2">
              <Input
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message or question..."
                className="flex-1 bg-input border-border text-foreground placeholder-muted-foreground"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!currentInput.trim()}
                className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button
            onClick={() => sendMessage("Teach me new vocabulary words for business English")}
            variant="outline"
            className="border-border text-foreground hover:bg-muted p-4 h-auto"
          >
            <div className="text-left">
              <div className="font-medium">Vocabulary Practice</div>
              <div className="text-sm text-muted-foreground">Learn business English words</div>
            </div>
          </Button>
          <Button
            onClick={() => sendMessage("Help me practice a job interview")}
            variant="outline"
            className="border-border text-foreground hover:bg-muted p-4 h-auto"
          >
            <div className="text-left">
              <div className="font-medium">Interview Practice</div>
              <div className="text-sm text-muted-foreground">Prepare for job interviews</div>
            </div>
          </Button>
          <Button
            onClick={() => sendMessage("Explain English grammar rules")}
            variant="outline"
            className="border-border text-foreground hover:bg-muted p-4 h-auto"
          >
            <div className="text-left">
              <div className="font-medium">Grammar Help</div>
              <div className="text-sm text-muted-foreground">Understanding English grammar</div>
            </div>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default UnifiedIVRInterface;
