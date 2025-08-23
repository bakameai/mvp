import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Phone, PhoneOff, Mic, MicOff, Volume2, Wifi, WifiOff, BookOpen, Target, MessageSquare, Trophy, Clock, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'vocabulary' | 'grammar' | 'conversation' | 'general';
}

interface LearningStats {
  wordsLearned: number;
  conversationTime: number;
  grammarTopics: number;
  currentLevel: string;
  streakDays: number;
  lessonsCompleted: number;
}

interface IVRInterfaceProps {
  className?: string;
}

// Enhanced RealtimeChat class with learning focus
class RealtimeChat {
  private pc: RTCPeerConnection | null = null;
  private dc: RTCDataChannel | null = null;
  private audioEl: HTMLAudioElement | null = null;

  constructor(private onMessage: (message: any) => void) {
    this.audioEl = document.createElement("audio");
    this.audioEl.autoplay = true;
  }

  async init() {
    try {
      console.log('Initializing English learning session...');
      
      // Get ephemeral token from our edge function
      const response = await fetch('/api/sessions/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('English learning session response:', data);
      
      if (!data.client_secret?.value) {
        throw new Error("Failed to get ephemeral token");
      }

      const EPHEMERAL_KEY = data.client_secret.value;

      // Create peer connection
      this.pc = new RTCPeerConnection();

      // Set up remote audio
      this.pc.ontrack = e => {
        if (this.audioEl) {
          this.audioEl.srcObject = e.streams[0];
        }
      };

      // Add local audio track
      const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.pc.addTrack(ms.getTracks()[0]);

      // Set up data channel
      this.dc = this.pc.createDataChannel("oai-events");
      this.dc.addEventListener("message", (e) => {
        try {
          const event = JSON.parse(e.data);
          console.log("Received event:", event.type);
          this.onMessage(event);
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      });

      // Create and set local description
      const offer = await this.pc.createOffer();
      await this.pc.setLocalDescription(offer);

      // Connect to OpenAI's Realtime API
      const baseUrl = "https://api.openai.com/v1/realtime";
      const model = "gpt-4o-realtime-preview-2024-12-17";
      const sdpResponse = await fetch(`${baseUrl}?model=${model}`, {
        method: "POST",
        body: offer.sdp,
        headers: {
          Authorization: `Bearer ${EPHEMERAL_KEY}`,
          "Content-Type": "application/sdp"
        },
      });

      if (!sdpResponse.ok) {
        throw new Error(`OpenAI connection failed: ${sdpResponse.status}`);
      }

      const answer = {
        type: "answer" as RTCSdpType,
        sdp: await sdpResponse.text(),
      };
      
      await this.pc.setRemoteDescription(answer);
      console.log("English learning WebRTC connection established");
      
      // Notify connection success
      this.onMessage({ type: 'session.created' });

    } catch (error) {
      console.error("Error initializing English learning chat:", error);
      this.onMessage({ type: 'error', error: error.message });
      throw error;
    }
  }

  async sendMessage(text: string) {
    if (!this.dc || this.dc.readyState !== 'open') {
      throw new Error('Data channel not ready');
    }

    const event = {
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [
          {
            type: 'input_text',
            text
          }
        ]
      }
    };

    this.dc.send(JSON.stringify(event));
    this.dc.send(JSON.stringify({type: 'response.create'}));
  }

  disconnect() {
    console.log('Disconnecting English learning session...');
    this.dc?.close();
    this.pc?.close();
    if (this.audioEl) {
      this.audioEl.srcObject = null;
    }
  }
}

const IVRInterface: React.FC<IVRInterfaceProps> = ({ className = '' }) => {
  const { toast } = useToast();
  
  // Core state
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [conversation, setConversation] = useState<ConversationMessage[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<string>('Ready to Learn English');
  const [learningStats, setLearningStats] = useState<LearningStats>({
    wordsLearned: 0,
    conversationTime: 0,
    grammarTopics: 0,
    currentLevel: 'Beginner',
    streakDays: 0,
    lessonsCompleted: 0
  });

  // Refs
  const chatRef = useRef<RealtimeChat | null>(null);
  const currentTranscriptRef = useRef<string>('');
  const sessionStartTime = useRef<Date | null>(null);

  const handleMessage = (event: any) => {
    console.log('Received message:', event.type);
    
    switch (event.type) {
      case 'session.created':
        console.log('English learning session created');
        setConnectionStatus('Learning Session Active');
        setIsConnected(true);
        sessionStartTime.current = new Date();
        break;

      case 'input_audio_buffer.speech_started':
        console.log('Student speaking...');
        setIsRecording(true);
        break;

      case 'input_audio_buffer.speech_stopped':
        console.log('Student stopped speaking');
        setIsRecording(false);
        break;

      case 'response.audio.delta':
        setIsSpeaking(true);
        break;

      case 'response.audio.done':
        console.log('AI finished speaking');
        setIsSpeaking(false);
        // Update conversation time
        if (sessionStartTime.current) {
          const timeSpent = Math.floor((new Date().getTime() - sessionStartTime.current.getTime()) / 60000);
          setLearningStats(prev => ({ ...prev, conversationTime: timeSpent }));
        }
        break;

      case 'response.audio_transcript.delta':
        if (event.delta) {
          currentTranscriptRef.current += event.delta;
        }
        break;

      case 'response.audio_transcript.done':
        if (currentTranscriptRef.current) {
          const aiMessage: ConversationMessage = {
            role: 'assistant',
            content: currentTranscriptRef.current,
            timestamp: new Date(),
            type: detectMessageType(currentTranscriptRef.current)
          };
          setConversation(prev => [...prev, aiMessage]);
          updateLearningStats(aiMessage);
          currentTranscriptRef.current = '';
        }
        break;

      case 'conversation.item.input_audio_transcription.completed':
        if (event.transcript) {
          const userMessage: ConversationMessage = {
            role: 'user',
            content: event.transcript,
            timestamp: new Date()
          };
          setConversation(prev => [...prev, userMessage]);
        }
        break;

      case 'error':
        console.error('Realtime API error:', event.error);
        setConnectionStatus('Connection Failed');
        toast({
          title: "Connection Error",
          description: event.error,
          variant: "destructive",
        });
        break;
    }
  };

  const detectMessageType = (content: string): 'vocabulary' | 'grammar' | 'conversation' | 'general' => {
    const lowerContent = content.toLowerCase();
    if (lowerContent.includes('word') || lowerContent.includes('vocabulary') || lowerContent.includes('meaning')) {
      return 'vocabulary';
    } else if (lowerContent.includes('grammar') || lowerContent.includes('tense') || lowerContent.includes('rule')) {
      return 'grammar';
    } else if (lowerContent.includes('practice') || lowerContent.includes('conversation') || lowerContent.includes('interview')) {
      return 'conversation';
    }
    return 'general';
  };

  const updateLearningStats = (message: ConversationMessage) => {
    if (message.type === 'vocabulary') {
      setLearningStats(prev => ({ ...prev, wordsLearned: prev.wordsLearned + 1 }));
    } else if (message.type === 'grammar') {
      setLearningStats(prev => ({ ...prev, grammarTopics: prev.grammarTopics + 1 }));
    }
  };

  const startConnection = async () => {
    try {
      console.log('Starting English learning session...');
      setConnectionStatus('Connecting...');
      
      chatRef.current = new RealtimeChat(handleMessage);
      await chatRef.current.init();
      
      toast({
        title: "Learning Session Started!",
        description: "Your English tutor is ready to help you learn!",
      });
    } catch (error) {
      console.error('Error starting learning session:', error);
      setConnectionStatus('Connection Failed');
      setIsConnected(false);
      toast({
        title: "Connection Error",
        description: error instanceof Error ? error.message : 'Failed to start learning session',
        variant: "destructive",
      });
    }
  };

  const endConnection = () => {
    console.log('Ending learning session...');
    chatRef.current?.disconnect();
    setIsConnected(false);
    setConnectionStatus('Session Ended');
    setIsRecording(false);
    setIsSpeaking(false);
    
    toast({
      title: "Learning Session Complete",
      description: `Great job! You practiced for ${learningStats.conversationTime} minutes.`,
    });
  };

  useEffect(() => {
    return () => {
      chatRef.current?.disconnect();
    };
  }, []);

  const getStatusColor = () => {
    if (!isConnected) return 'bg-white';
    if (isSpeaking) return 'bg-[#0d4dcc] animate-pulse';
    if (isRecording) return 'bg-[#ff914d] animate-pulse';
    return 'bg-[#ff914d]';
  };

  const getStatusIcon = () => {
    if (!isConnected) return <WifiOff className="w-4 h-4" />;
    return <Wifi className="w-4 h-4" />;
  };

  return (
    <div className={`max-w-4xl mx-auto ${className}`}>
      <Card className="bg-[#081a2e]/80 backdrop-blur-md border-white/20 text-white">
        <CardContent className="p-8">
          {/* Enhanced Learning Stats */}
          {isConnected && (
            <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-6">
              <div className="text-center p-3 bg-gradient-to-br from-[#ff914d]/10 to-[#0d4dcc]/10 rounded-lg border border-white/20">
                <BookOpen className="w-4 h-4 text-[#ff914d] mx-auto mb-1" />
                <div className="text-sm font-bold bg-gradient-to-r from-[#ff914d] to-[#0d4dcc] bg-clip-text text-transparent">{learningStats.wordsLearned}</div>
                <div className="text-xs text-white/70">Words</div>
              </div>
              <div className="text-center p-3 bg-gradient-to-br from-[#0d4dcc]/10 to-[#ff914d]/10 rounded-lg border border-white/20">
                <Target className="w-4 h-4 text-[#0d4dcc] mx-auto mb-1" />
                <div className="text-sm font-bold bg-gradient-to-r from-[#0d4dcc] to-[#ff914d] bg-clip-text text-transparent">{learningStats.grammarTopics}</div>
                <div className="text-xs text-white/70">Grammar</div>
              </div>
              <div className="text-center p-3 bg-gradient-to-br from-white/10 to-[#0d4dcc]/10 rounded-lg border border-white/20">
                <Clock className="w-4 h-4 text-white mx-auto mb-1" />
                <div className="text-sm font-bold text-white">{learningStats.conversationTime}</div>
                <div className="text-xs text-white/70">Minutes</div>
              </div>
              <div className="text-center p-3 bg-gradient-to-br from-[#ff914d]/10 to-white/10 rounded-lg border border-white/20">
                <Trophy className="w-4 h-4 text-[#ff914d] mx-auto mb-1" />
                <div className="text-sm font-bold bg-gradient-to-r from-[#ff914d] to-white bg-clip-text text-transparent">{learningStats.lessonsCompleted}</div>
                <div className="text-xs text-white/70">Lessons</div>
              </div>
              <div className="text-center p-3 bg-gradient-to-br from-[#0d4dcc]/10 to-[#ff914d]/10 rounded-lg border border-white/20">
                <Star className="w-4 h-4 text-[#0d4dcc] mx-auto mb-1" />
                <div className="text-sm font-bold bg-gradient-to-r from-[#0d4dcc] to-[#ff914d] bg-clip-text text-transparent">{learningStats.streakDays}</div>
                <div className="text-xs text-white/70">Streak</div>
              </div>
              <div className="text-center p-3 bg-gradient-to-br from-[#ff914d]/10 to-[#0d4dcc]/10 rounded-lg border border-white/20">
                <MessageSquare className="w-4 h-4 text-white mx-auto mb-1" />
                <div className="text-sm font-bold text-white">{learningStats.currentLevel}</div>
                <div className="text-xs text-white/70">Level</div>
              </div>
            </div>
          )}

          {/* Connection Status */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
              {getStatusIcon()}
              <Badge variant="outline" className="border-white/30 text-white bg-gradient-to-r from-[#ff914d]/10 to-[#0d4dcc]/10">
                {connectionStatus}
              </Badge>
            </div>
            
            {/* Main Call Button */}
            <div className="flex justify-center gap-4">
              {!isConnected ? (
                <Button 
                  onClick={startConnection}
                  size="lg"
                  className="bg-gradient-to-r from-[#ff914d] to-[#0d4dcc] hover:from-[#0d4dcc] hover:to-[#ff914d] text-white px-8 py-4 rounded-full flex items-center gap-3 text-lg font-semibold transition-all duration-500 hover:scale-105 shadow-[0_0_20px_rgba(255,145,77,0.3),0_0_40px_rgba(13,77,204,0.3)] hover:shadow-[0_0_30px_rgba(255,145,77,0.5),0_0_60px_rgba(13,77,204,0.5)]"
                >
                  <Phone className="w-6 h-6" />
                  Start Learning Session
                </Button>
              ) : (
                <Button 
                  onClick={endConnection}
                  size="lg"
                  className="bg-white hover:bg-white/90 text-black px-8 py-4 rounded-full flex items-center gap-3 text-lg font-semibold transition-all duration-300 hover:scale-105"
                >
                  <PhoneOff className="w-6 h-6" />
                  End Session
                </Button>
              )}
            </div>
          </div>

          {/* Activity Indicators */}
          {isConnected && (
            <div className="flex justify-center gap-6 mb-6">
              <div className={`flex items-center gap-2 ${isRecording ? 'text-[#ff914d]' : 'text-white/50'}`}>
                <Mic className={`w-5 h-5 ${isRecording ? 'animate-pulse' : ''}`} />
                <span className="text-sm">You're Speaking</span>
              </div>
              
              <div className={`flex items-center gap-2 ${isSpeaking ? 'text-[#0d4dcc]' : 'text-white/50'}`}>
                <Volume2 className={`w-5 h-5 ${isSpeaking ? 'animate-pulse' : ''}`} />
                <span className="text-sm">AI Teaching</span>
              </div>
            </div>
          )}

          {/* Conversation History */}
          {conversation.length > 0 && (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-white/80 mb-3 flex items-center gap-2">
                <div className="w-2 h-2 bg-gradient-to-r from-[#ff914d] to-[#0d4dcc] rounded-full"></div>
                Learning Conversation
              </h3>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {conversation.slice(-6).map((message, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg ${
                      message.role === 'user' 
                        ? 'bg-gradient-to-r from-[#0d4dcc]/20 to-[#ff914d]/10 border border-[#0d4dcc]/30 ml-8' 
                        : 'bg-gradient-to-r from-[#ff914d]/20 to-[#0d4dcc]/10 border border-[#ff914d]/30 mr-8'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-xs font-medium ${
                        message.role === 'user' 
                          ? 'bg-gradient-to-r from-[#0d4dcc] to-[#ff914d] bg-clip-text text-transparent' 
                          : 'bg-gradient-to-r from-[#ff914d] to-[#0d4dcc] bg-clip-text text-transparent'
                      }`}>
                        {message.role === 'user' ? 'You' : 'Bakame AI Tutor'}
                      </span>
                      {message.type && (
                        <Badge variant="outline" className="text-xs border-white/30 text-white/70 bg-gradient-to-r from-[#ff914d]/5 to-[#0d4dcc]/5">
                          {message.type}
                        </Badge>
                      )}
                      <span className="text-xs text-white/50">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-white/90">{message.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default IVRInterface;
