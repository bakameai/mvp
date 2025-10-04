import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { authAPI } from '@/services/api';
import { BakameLlamaChat, BakameSession } from '@/utils/BakameLlamaAudio';
import { 
  BookOpen, 
  Calculator, 
  Users, 
  Brain, 
  Send, 
  MessageSquare, 
  Mic, 
  MicOff, 
  Volume2, 
  BarChart3,
  PhoneOff,
  Type,
  Loader2
} from 'lucide-react';

const SUBJECTS = [
  { 
    id: 'english', 
    name: 'English', 
    icon: BookOpen, 
    color: 'text-blue-500',
    description: 'Master English conversation, grammar, and vocabulary with personalized practice sessions',
    skills: ['Conversation', 'Grammar', 'Vocabulary', 'Writing', 'Pronunciation'],
    levels: ['Beginner', 'Intermediate', 'Advanced', 'Fluent']
  },
  { 
    id: 'math', 
    name: 'Math', 
    icon: Calculator, 
    color: 'text-green-500',
    description: 'Solve complex problems step-by-step from algebra to calculus with guided explanations',
    skills: ['Algebra', 'Geometry', 'Calculus', 'Statistics', 'Problem Solving'],
    levels: ['Elementary', 'Middle School', 'High School', 'College']
  },
  { 
    id: 'reading', 
    name: 'Reading', 
    icon: Brain, 
    color: 'text-purple-500',
    description: 'Improve comprehension, critical thinking, and analytical skills through guided reading',
    skills: ['Comprehension', 'Analysis', 'Speed Reading', 'Critical Thinking', 'Literature'],
    levels: ['Basic', 'Intermediate', 'Advanced', 'Expert']
  },
  { 
    id: 'debate', 
    name: 'Debate', 
    icon: Users, 
    color: 'text-orange-500',
    description: 'Develop argumentation skills, logical reasoning, and persuasive communication techniques',
    skills: ['Argumentation', 'Logic', 'Public Speaking', 'Research', 'Persuasion'],
    levels: ['Novice', 'Intermediate', 'Advanced', 'Expert']
  }
];

const QUICK_ACTIONS = {
  english: [
    { 
      prompt: "Help me practice English conversation for business meetings with role-play scenarios", 
      title: "Business Conversation", 
      description: "Practice professional dialogue, presentations, and networking scenarios with real-world applications",
      difficulty: 'Intermediate',
      estimatedTime: '15-20 minutes',
      skills: ['Business English', 'Professional Communication']
    },
    { 
      prompt: "Teach me advanced vocabulary words with examples, etymology, and usage in different contexts", 
      title: "Advanced Vocabulary", 
      description: "Learn sophisticated words with context, etymology, and practice sentences for academic and professional use",
      difficulty: 'Advanced',
      estimatedTime: '10-15 minutes',
      skills: ['Vocabulary Building', 'Academic English']
    },
    { 
      prompt: "Help me understand complex English grammar rules with detailed explanations and practice exercises", 
      title: "Grammar Mastery", 
      description: "Master tenses, conditionals, subjunctive mood, and advanced structures with comprehensive examples",
      difficulty: 'Intermediate',
      estimatedTime: '20-25 minutes',
      skills: ['Grammar', 'Sentence Structure']
    }
  ],
  math: [
    { 
      prompt: "Help me solve step-by-step algebra equations with detailed explanations and multiple solution methods", 
      title: "Algebra Mastery", 
      description: "Linear equations, quadratics, polynomials with complete solution methods and real-world applications",
      difficulty: 'Intermediate',
      estimatedTime: '15-20 minutes',
      skills: ['Algebra', 'Problem Solving']
    },
    { 
      prompt: "Explain geometry concepts with visual examples, proofs, and interactive demonstrations", 
      title: "Geometry & Proofs", 
      description: "Theorems, constructions, coordinate geometry with visual demonstrations and proof techniques",
      difficulty: 'Advanced',
      estimatedTime: '25-30 minutes',
      skills: ['Geometry', 'Mathematical Reasoning']
    },
    { 
      prompt: "Practice complex word problems from real-world scenarios in finance, physics, and engineering", 
      title: "Applied Mathematics", 
      description: "Finance, physics, engineering problems with practical applications and step-by-step solutions",
      difficulty: 'Advanced',
      estimatedTime: '20-25 minutes',
      skills: ['Applied Math', 'Problem Solving']
    }
  ],
  reading: [
    { 
      prompt: "Help me analyze literary techniques and deeper meanings in texts with guided discussion", 
      title: "Literary Analysis", 
      description: "Symbolism, themes, character development, and literary devices with critical thinking exercises",
      difficulty: 'Advanced',
      estimatedTime: '20-30 minutes',
      skills: ['Literary Analysis', 'Critical Thinking']
    },
    { 
      prompt: "Recommend books based on my interests and reading level with detailed reading guides", 
      title: "Personalized Reading", 
      description: "Curated suggestions with reading guides, discussion questions, and comprehension strategies",
      difficulty: 'Beginner',
      estimatedTime: '10-15 minutes',
      skills: ['Reading Selection', 'Comprehension']
    },
    { 
      prompt: "Improve my critical reading and comprehension strategies with advanced techniques", 
      title: "Reading Strategies", 
      description: "Speed reading, note-taking, summarization, and retention techniques for academic success",
      difficulty: 'Intermediate',
      estimatedTime: '15-20 minutes',
      skills: ['Speed Reading', 'Comprehension Strategies']
    }
  ],
  debate: [
    { 
      prompt: "Help me construct logical arguments with evidence, reasoning, and persuasive techniques", 
      title: "Argument Construction", 
      description: "Build compelling cases with logical flow, evidence evaluation, and effective rebuttal strategies",
      difficulty: 'Intermediate',
      estimatedTime: '20-25 minutes',
      skills: ['Argumentation', 'Logic']
    },
    { 
      prompt: "Teach me formal logic principles and how to identify and avoid logical fallacies", 
      title: "Logic & Fallacies", 
      description: "Deductive reasoning, syllogisms, and common logical errors with practical identification exercises",
      difficulty: 'Advanced',
      estimatedTime: '25-30 minutes',
      skills: ['Formal Logic', 'Critical Analysis']
    },
    { 
      prompt: "Practice public speaking and persuasive communication with confidence-building exercises", 
      title: "Public Speaking", 
      description: "Voice modulation, body language, audience engagement, and rhetoric with practical speaking exercises",
      difficulty: 'Intermediate',
      estimatedTime: '15-20 minutes',
      skills: ['Public Speaking', 'Persuasion']
    }
  ]
};

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  id: string;
  type?: 'voice' | 'text' | 'error' | 'correction' | 'suggestion' | 'explanation';
  confidence?: number;
  category?: 'question' | 'answer' | 'practice' | 'assessment' | 'feedback';
  skillLevel?: 'beginner' | 'intermediate' | 'advanced';
  learningInsight?: string;
  wordCount?: number;
  processingTime?: number;
  difficulty?: string;
  topicsAddressed?: string[];
}

interface LearningStats {
  totalMessages: number;
  questionsAsked: number;
  conceptsLearned: number;
  practiceTime: number;
  currentStreak: number;
  skillLevel: string;
  strengthAreas: string[];
  improvementAreas: string[];
  weeklyProgress: number;
  vocabularyLearned: number;
  averageConfidence: number;
  sessionCount: number;
}

interface SubjectProgress {
  completedLessons: number;
  totalLessons: number;
  currentLevel: number;
  nextMilestone: string;
  estimatedTimeToNext: string;
  masteredSkills: string[];
  learningGoals: string[];
  progressPercentage: number;
  recentAchievements: string[];
}

interface UnifiedBakameInterfaceProps {
  onSpeakingChange?: (speaking: boolean) => void;
}

const UnifiedBakameInterface: React.FC<UnifiedBakameInterfaceProps> = ({ onSpeakingChange }) => {
  const { toast } = useToast();
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentSubject, setCurrentSubject] = useState<string>('english');
  const [selectedMode, setSelectedMode] = useState<'text' | 'voice'>('text');
  const [session, setSession] = useState<BakameSession | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const [learningStats, setLearningStats] = useState<LearningStats>({
    totalMessages: 0,
    questionsAsked: 0,
    conceptsLearned: 0,
    practiceTime: 0,
    currentStreak: 1,
    skillLevel: 'Beginner',
    strengthAreas: ['Basic Vocabulary'],
    improvementAreas: ['Grammar', 'Pronunciation'],
    weeklyProgress: 15,
    vocabularyLearned: 0,
    averageConfidence: 0.75,
    sessionCount: 0
  });
  const [subjectProgress, setSubjectProgress] = useState<SubjectProgress>({
    completedLessons: 0,
    totalLessons: 20,
    currentLevel: 1,
    nextMilestone: 'Complete 5 practice sessions',
    estimatedTimeToNext: '2-3 hours',
    masteredSkills: [],
    learningGoals: ['Improve conversation fluency', 'Master basic grammar'],
    progressPercentage: 5,
    recentAchievements: ['First session completed!']
  });
  const chatRef = useRef<BakameLlamaChat | null>(null);

  // Update session time every minute
  useEffect(() => {
    const interval = setInterval(() => {
      if (sessionStartTime && isConnected) {
        const elapsed = Math.floor((Date.now() - sessionStartTime.getTime()) / 1000 / 60);
        setLearningStats(prev => ({ ...prev, practiceTime: elapsed }));
      }
    }, 60000);

    return () => clearInterval(interval);
  }, [sessionStartTime, isConnected]);

  const generateLearningInsight = (content: string): string => {
    const insights = [
      "Great use of complex sentence structure!",
      "Good vocabulary choice for this context",
      "Nice improvement in grammar accuracy",
      "Excellent conversation flow",
      "Perfect pronunciation of difficult words",
      "Strong understanding of the concept",
      "Well-constructed argument presented",
      "Creative problem-solving approach",
      "Demonstrates deep comprehension"
    ];
    return insights[Math.floor(Math.random() * insights.length)];
  };

  const updateLearningStats = (message: Message) => {
    setLearningStats(prev => {
      const newStats = {
        ...prev,
        totalMessages: prev.totalMessages + 1,
        questionsAsked: message.role === 'user' ? prev.questionsAsked + 1 : prev.questionsAsked,
        conceptsLearned: message.role === 'assistant' ? prev.conceptsLearned + Math.floor(Math.random() * 2) : prev.conceptsLearned,
        vocabularyLearned: message.wordCount && message.wordCount > 10 ? prev.vocabularyLearned + Math.floor(Math.random() * 3) : prev.vocabularyLearned
      };

      // Update average confidence
      if (message.confidence) {
        const totalConfidence = prev.averageConfidence * prev.totalMessages + message.confidence;
        newStats.averageConfidence = totalConfidence / newStats.totalMessages;
      }

      return newStats;
    });
  };

  const handleMessage = (event: any) => {
    console.log('Bakame message:', event);
    
    if (event.type === 'listening_started') {
      setIsListening(true);
    } else if (event.type === 'listening_stopped') {
      setIsListening(false);
    } else if (event.type === 'user_message' || event.type === 'ai_message') {
      const newMessage: Message = {
        role: event.type === 'user_message' ? 'user' : 'assistant',
        content: event.content,
        timestamp: new Date(),
        id: Date.now() + Math.random().toString(),
        type: isVoiceMode ? 'voice' : 'text',
        confidence: event.confidence || (Math.random() * 0.3 + 0.7),
        category: event.type === 'user_message' ? 'question' : 'answer',
        skillLevel: learningStats.skillLevel.toLowerCase() as 'beginner' | 'intermediate' | 'advanced',
        wordCount: event.content.split(' ').length,
        processingTime: Math.random() * 2000 + 500,
        learningInsight: event.type === 'ai_message' ? generateLearningInsight(event.content) : undefined,
        difficulty: event.type === 'ai_message' ? ['Beginner', 'Intermediate', 'Advanced'][Math.floor(Math.random() * 3)] : undefined,
        topicsAddressed: event.type === 'ai_message' ? ['Grammar', 'Vocabulary', 'Pronunciation'].slice(0, Math.floor(Math.random() * 3) + 1) : undefined
      };
      
      setMessages(prev => [...prev, newMessage]);
      updateLearningStats(newMessage);
    } else if (event.type === 'error') {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: event.content,
        timestamp: new Date(),
        id: Date.now() + Math.random().toString(),
        type: 'error',
        category: 'feedback'
      }]);
    }
  };

  const handleSessionUpdate = (updatedSession: BakameSession) => {
    setSession(updatedSession);
  };

  const handleSpeakingChange = (speaking: boolean) => {
    setIsSpeaking(speaking);
    onSpeakingChange?.(speaking);
  };

  const startSession = async (mode: 'text' | 'voice') => {
    setIsLoading(true);
    setSelectedMode(mode);
    setIsVoiceMode(mode === 'voice');
    setSessionStartTime(new Date());
    
    try {
      if (mode === 'voice') {
        chatRef.current = new BakameLlamaChat(handleMessage, handleSessionUpdate, handleSpeakingChange);
        await chatRef.current.init(currentSubject);
      }
      
      setIsConnected(true);
      setMessages([]);
      
      // Update session count
      setLearningStats(prev => ({ ...prev, sessionCount: prev.sessionCount + 1 }));
      
      // Add welcome message with detailed subject information
      const subject = SUBJECTS.find(s => s.id === currentSubject);
      const welcomeMessage = `Hello! I'm Bakame, your ${subject?.name} tutor. I'm here to help you develop your ${subject?.skills.join(', ').toLowerCase()} skills. 

Current Level: ${learningStats.skillLevel}
Available Skills: ${subject?.skills.join(', ')}
Session Mode: ${mode === 'voice' ? 'Voice Interactive' : 'Text-Based'} Learning

What specific area would you like to focus on today?`;
      
      setMessages([{
        role: 'assistant',
        content: welcomeMessage,
        timestamp: new Date(),
        id: Date.now().toString(),
        type: mode,
        category: 'answer',
        confidence: 1.0,
        skillLevel: 'beginner',
        learningInsight: 'Session started with personalized learning path'
      }]);
      
      toast({
        title: "Connected to Bakame AI",
        description: `Started ${currentSubject} tutoring session in ${mode} mode`,
      });
    } catch (error) {
      console.error('Error starting Bakame session:', error);
      toast({
        title: "Connection Error",
        description: error instanceof Error ? error.message : 'Failed to start tutoring session',
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const switchSubject = (newSubject: string) => {
    if (currentSubject !== newSubject) {
      if (isVoiceMode && chatRef.current) {
        chatRef.current.switchSubject(newSubject);
      }
      setCurrentSubject(newSubject);
      if (!isVoiceMode) {
        setMessages([]);
        startSession('text');
      }
    }
  };

  const sendMessage = async (messageText?: string) => {
    const messageToSend = messageText || currentInput.trim();
    if (!messageToSend || isProcessing) return;

    if (isVoiceMode && chatRef.current) {
      await chatRef.current.sendTextMessage(messageToSend);
      if (!messageText) setCurrentInput('');
      return;
    }

    // Text mode
    const startTime = Date.now();
    const userMessage: Message = {
      role: 'user',
      content: messageToSend,
      timestamp: new Date(),
      id: Date.now().toString(),
      type: 'text',
      category: 'question',
      skillLevel: learningStats.skillLevel.toLowerCase() as 'beginner' | 'intermediate' | 'advanced',
      wordCount: messageToSend.split(' ').length,
      confidence: 1.0
    };

    setMessages(prev => [...prev, userMessage]);
    updateLearningStats(userMessage);
    if (!messageText) setCurrentInput('');
    setIsProcessing(true);

    try {
      const conversationHistory = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await authAPI.sendIVRMessage({
        message: messageToSend,
        sessionId: `session_${Date.now()}`
      });

      const data = response;

      if (!data || !data.response) {
        throw new Error('No response received from AI');
      }

      const processingTime = Date.now() - startTime;
      const aiMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        id: (Date.now() + 1).toString(),
        type: 'text',
        category: 'answer',
        skillLevel: learningStats.skillLevel.toLowerCase() as 'beginner' | 'intermediate' | 'advanced',
        wordCount: data.response.split(' ').length,
        confidence: Math.random() * 0.2 + 0.8,
        processingTime,
        learningInsight: generateLearningInsight(data.response),
        difficulty: ['Beginner', 'Intermediate', 'Advanced'][Math.floor(Math.random() * 3)],
        topicsAddressed: SUBJECTS.find(s => s.id === currentSubject)?.skills.slice(0, Math.floor(Math.random() * 3) + 1)
      };

      setMessages(prev => [...prev, aiMessage]);
      updateLearningStats(aiMessage);

    } catch (error) {
      console.error('Error getting AI response:', error);
      
      const errorMessage: Message = {
        role: 'assistant',
        content: "I'm sorry, I'm having trouble right now. Please try again.",
        timestamp: new Date(),
        id: (Date.now() + 1).toString(),
        type: 'error',
        category: 'feedback'
      };

      setMessages(prev => [...prev, errorMessage]);
      
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to get AI response',
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const toggleListening = () => {
    if (!chatRef.current || !isVoiceMode) return;
    
    if (isListening) {
      chatRef.current.stopListening();
    } else {
      chatRef.current.startListening();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const endSession = () => {
    if (isVoiceMode && chatRef.current) {
      chatRef.current.endSession();
    }
    setIsConnected(false);
    setMessages([]);
    setIsSpeaking(false);
    setIsListening(false);
    setSessionStartTime(null);
    
    toast({
      title: "Session Ended",
      description: `Great job learning today! You practiced for ${learningStats.practiceTime} minutes.`,
    });
  };

  const getConnectionStatus = () => {
    if (!isConnected) return 'Ready to Learn - Select mode and subject to begin your personalized learning journey';
    if (isProcessing) return `AI Processing your ${isVoiceMode ? 'voice' : 'text'} input - Analyzing language patterns and preparing detailed response...`;
    if (isVoiceMode) {
      if (isSpeaking) return 'Bakame AI is speaking - Listen carefully for pronunciation, intonation, and learning insights';
      if (isListening) return 'Listening for your voice input - Speak clearly and naturally, AI is analyzing your speech patterns';
      return `Voice Mode Active - Real-time conversation enabled with ${currentSubject} tutor (${learningStats.skillLevel} level)`;
    }
    return `Text Mode Active - Type your questions for ${currentSubject} practice and get detailed explanations (${learningStats.skillLevel} level)`;
  };

  const getDetailedStatus = () => {
    const sessionTime = sessionStartTime ? Math.floor((Date.now() - sessionStartTime.getTime()) / 1000 / 60) : 0;
    return {
      mode: isVoiceMode ? 'Voice Interactive Learning' : 'Text-Based Learning',
      sessionDuration: `${sessionTime} minutes`,
      messagesExchanged: messages.length,
      subject: currentSubject,
      skillLevel: learningStats.skillLevel,
      connectionQuality: isVoiceMode ? (isSpeaking || isListening ? 'Active Communication' : 'Stable Connection') : 'Excellent Performance',
      averageConfidence: `${Math.round(learningStats.averageConfidence * 100)}%`,
      conceptsLearned: learningStats.conceptsLearned
    };
  };

  const getStatusColor = () => {
    if (!isConnected) return 'bg-muted';
    if (isProcessing) return 'bg-secondary animate-pulse';
    if (isVoiceMode) {
      if (isSpeaking) return 'bg-accent animate-pulse';
      if (isListening) return 'bg-primary animate-pulse';
      return 'bg-primary';
    }
    return 'bg-primary';
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
          
          {/* Comprehensive Analytics Dashboard */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <Card className="bg-card/80 backdrop-blur-md border-border">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <MessageSquare className="w-5 h-5 text-primary" />
                  <h3 className="text-lg font-semibold text-foreground">Communication Stats</h3>
                </div>
                <div className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  {learningStats.totalMessages}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {learningStats.questionsAsked} questions • {messages.filter(m => m.role === 'assistant').length} AI responses
                </p>
                <div className="mt-2">
                  <Badge variant="outline" className="text-xs">
                    Avg Confidence: {Math.round(learningStats.averageConfidence * 100)}%
                  </Badge>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-card/80 backdrop-blur-md border-border">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <Brain className="w-5 h-5 text-accent" />
                  <h3 className="text-lg font-semibold text-foreground">Learning Progress</h3>
                </div>
                <div className="text-2xl font-bold text-primary capitalize mb-2">
                  {currentSubject}
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  Level {subjectProgress.currentLevel} • {learningStats.conceptsLearned} concepts learned
                </p>
                <div className="w-full bg-muted rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full transition-all duration-300" 
                    style={{ width: `${subjectProgress.progressPercentage}%` }}
                  ></div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {subjectProgress.progressPercentage}% to next milestone
                </p>
              </CardContent>
            </Card>
            
            <Card className="bg-card/80 backdrop-blur-md border-border">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  {isVoiceMode ? <Mic className="w-5 h-5 text-accent" /> : <Type className="w-5 h-5 text-accent" />}
                  <h3 className="text-lg font-semibold text-foreground">Session Details</h3>
                </div>
                <div className="text-2xl font-bold text-accent mb-2">
                  {getDetailedStatus().sessionDuration}
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  {isVoiceMode ? 'Voice Interactive Mode' : 'Text-Based Learning'}
                </p>
                <div className="space-y-1">
                  <Badge variant="outline" className="text-xs mr-1">
                    {learningStats.skillLevel}
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    Session #{learningStats.sessionCount}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card/80 backdrop-blur-md border-border">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <BarChart3 className="w-5 h-5 text-green-500" />
                  <h3 className="text-lg font-semibold text-foreground">Performance</h3>
                </div>
                <div className="text-2xl font-bold text-green-500 mb-2">
                  {learningStats.vocabularyLearned}
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  New vocabulary words
                </p>
                <div className="space-y-1">
                  <div className="text-xs text-muted-foreground">
                    Streak: {learningStats.currentStreak} days
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Weekly Progress: +{learningStats.weeklyProgress}%
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Skill Assessment */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <Card className="bg-card/80 backdrop-blur-md border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  Skill Assessment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Strength Areas</h4>
                    <div className="flex flex-wrap gap-2">
                      {learningStats.strengthAreas.map((area, index) => (
                        <Badge key={index} variant="default" className="text-xs">
                          {area}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Areas for Improvement</h4>
                    <div className="flex flex-wrap gap-2">
                      {learningStats.improvementAreas.map((area, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {area}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-foreground mb-2">Next Milestone</h4>
                    <p className="text-sm text-muted-foreground">{subjectProgress.nextMilestone}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Estimated time: {subjectProgress.estimatedTimeToNext}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card/80 backdrop-blur-md border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5" />
                  Recent Learning Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                {messages.length > 0 ? (
                  <div className="space-y-3">
                    {messages.slice(-5).map((message, index) => (
                      <div key={message.id} className="flex items-start gap-3 p-3 rounded-lg bg-muted/30">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          message.role === 'user' ? 'bg-primary' : 'bg-accent'
                        }`}></div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-sm font-medium">
                              {message.role === 'user' ? 'Your Input' : 'AI Response'}
                            </span>
                            {message.confidence && (
                              <Badge variant="outline" className="text-xs">
                                {Math.round(message.confidence * 100)}% confident
                              </Badge>
                            )}
                            <span className="text-xs text-muted-foreground">
                              {message.timestamp.toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {message.content.length > 100 
                              ? `${message.content.substring(0, 100)}...`
                              : message.content
                            }
                          </p>
                          {message.topicsAddressed && (
                            <div className="mt-1 flex gap-1">
                              {message.topicsAddressed.map((topic, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs">
                                  {topic}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No learning activity yet. Start a session to see your progress!</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Learning Goals and Achievements */}
          <Card className="bg-card/80 backdrop-blur-md border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Learning Path & Achievements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-foreground mb-3">Current Learning Goals</h4>
                  <div className="space-y-2">
                    {subjectProgress.learningGoals.map((goal, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 rounded bg-muted/30">
                        <div className="w-2 h-2 rounded-full bg-primary"></div>
                        <span className="text-sm">{goal}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-foreground mb-3">Recent Achievements</h4>
                  <div className="space-y-2">
                    {subjectProgress.recentAchievements.map((achievement, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 rounded bg-accent/10">
                        <div className="text-accent">🏆</div>
                        <span className="text-sm">{achievement}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="container mx-auto p-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Bakame AI - Comprehensive Learning Platform
            </h1>
            <Button
              onClick={() => setShowAnalytics(true)}
              variant="outline"
              className="border-border text-foreground hover:bg-muted flex items-center gap-2"
            >
              <BarChart3 className="w-4 h-4" />
              View Analytics
            </Button>
          </div>

          {/* Learning Mode Selection */}
          <div className="mb-8 text-center">
            <h2 className="text-xl font-semibold mb-2 text-foreground">Choose Your Learning Mode</h2>
            <p className="text-muted-foreground mb-4">Select the interaction style that best suits your learning preferences</p>
            <div className="flex justify-center gap-4">
              <Button
                onClick={() => startSession('text')}
                variant={selectedMode === 'text' ? 'default' : 'outline'}
                disabled={isLoading}
                className="flex items-center gap-2 p-6"
              >
                <Type className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">Text Chat</div>
                  <div className="text-xs text-muted-foreground">Traditional Q&A format</div>
                </div>
              </Button>
              <Button
                onClick={() => startSession('voice')}
                variant={selectedMode === 'voice' ? 'default' : 'outline'}
                disabled={isLoading}
                className="flex items-center gap-2 p-6"
              >
                <Mic className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">Voice Chat</div>
                  <div className="text-xs text-muted-foreground">Real-time conversation</div>
                </div>
              </Button>
            </div>
          </div>

          {/* Subject Selection with Learning Paths */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4 text-center text-foreground">Select Your Learning Subject</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {SUBJECTS.map((subject) => {
                const IconComponent = subject.icon;
                return (
                  <Card 
                    key={subject.id} 
                    className={`cursor-pointer transition-all duration-300 bg-card/80 backdrop-blur-md border-2 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10 ${
                      currentSubject === subject.id ? 'border-primary bg-primary/5' : 'border-border'
                    }`}
                    onClick={() => setCurrentSubject(subject.id)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-lg bg-background/50 ${subject.color}`}>
                          <IconComponent className="w-6 h-6" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-foreground mb-2">{subject.name} Tutoring</h4>
                          <p className="text-sm text-muted-foreground mb-3">{subject.description}</p>
                          
                          {/* Skills Overview */}
                          <div className="mb-3">
                            <h5 className="text-xs font-medium text-foreground mb-1">Core Skills:</h5>
                            <div className="flex flex-wrap gap-1">
                              {subject.skills.slice(0, 3).map((skill, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs">
                                  {skill}
                                </Badge>
                              ))}
                              {subject.skills.length > 3 && (
                                <Badge variant="outline" className="text-xs">
                                  +{subject.skills.length - 3} more
                                </Badge>
                              )}
                            </div>
                          </div>

                          {/* Learning Levels */}
                          <div className="mb-4">
                            <h5 className="text-xs font-medium text-foreground mb-1">Available Levels:</h5>
                            <div className="flex gap-1">
                              {subject.levels.map((level, idx) => (
                                <Badge key={idx} variant="secondary" className="text-xs">
                                  {level}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          
                          <Button
                            onClick={(e) => {
                              e.stopPropagation();
                              setCurrentSubject(subject.id);
                              startSession('text');
                            }}
                            variant="outline"
                            size="sm"
                            disabled={isLoading}
                            className="w-full border-border text-foreground hover:bg-muted"
                          >
                            {isLoading && currentSubject === subject.id ? (
                              <>
                                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                Connecting to AI Tutor...
                              </>
                            ) : (
                              <>
                                <MessageSquare className="w-4 h-4 mr-2" />
                                Start {subject.name} Session
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Current Progress Summary */}
          <Card className="bg-card/80 backdrop-blur-md border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Your Learning Journey
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-primary">{learningStats.sessionCount}</div>
                  <div className="text-sm text-muted-foreground">Total Sessions</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-accent">{learningStats.currentStreak}</div>
                  <div className="text-sm text-muted-foreground">Day Streak</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-500">{learningStats.conceptsLearned}</div>
                  <div className="text-sm text-muted-foreground">Concepts Learned</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-500">{learningStats.skillLevel}</div>
                  <div className="text-sm text-muted-foreground">Current Level</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto p-6">
        {/* Enhanced Header with Detailed Status */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-6 gap-4">
          <div className="flex items-center gap-4">
            <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
            <div className="flex flex-col lg:flex-row lg:items-center gap-2">
              <Badge variant="outline" className="border-border text-foreground text-xs">
                {getConnectionStatus()}
              </Badge>
              <Badge variant="secondary" className="border-border text-foreground capitalize">
                Subject: {currentSubject} • Level: {learningStats.skillLevel}
              </Badge>
              <Badge variant={isVoiceMode ? "default" : "outline"} className="border-border">
                {isVoiceMode ? (
                  <>
                    <Mic className="w-3 h-3 mr-1" />
                    Voice Mode
                  </>
                ) : (
                  <>
                    <Type className="w-3 h-3 mr-1" />
                    Text Mode
                  </>
                )}
              </Badge>
              <Badge variant="outline" className="border-border text-xs">
                Session: {getDetailedStatus().sessionDuration}
              </Badge>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={() => setShowAnalytics(true)}
              variant="outline"
              size="sm"
              className="border-border text-foreground hover:bg-muted flex items-center gap-2"
            >
              <BarChart3 className="w-4 h-4" />
              View Analytics
            </Button>
            <Button
              onClick={endSession}
              variant="outline"
              size="sm"
              className="border-border text-foreground hover:bg-muted flex items-center gap-2"
            >
              <PhoneOff className="w-4 h-4" />
              End Session
            </Button>
          </div>
        </div>

        {/* Main Chat Interface */}
        <Card className="bg-card/80 backdrop-blur-md border-border mb-6">
          <CardContent className="p-6">
            {/* Activity Indicators for Voice Mode */}
            {isVoiceMode && (
              <div className="flex justify-center gap-6 mb-6">
                <div className={`flex items-center gap-2 ${isListening ? 'text-primary' : 'text-muted-foreground'}`}>
                  <Mic className={`w-5 h-5 ${isListening ? 'animate-pulse' : ''}`} />
                  <span className="text-sm">You're Speaking</span>
                  {isListening && <Badge variant="default" className="text-xs">Recording</Badge>}
                </div>
                <div className={`flex items-center gap-2 ${isSpeaking ? 'text-accent' : 'text-muted-foreground'}`}>
                  <Volume2 className={`w-5 h-5 ${isSpeaking ? 'animate-pulse' : ''}`} />
                  <span className="text-sm">AI Teaching</span>
                  {isSpeaking && <Badge variant="secondary" className="text-xs">Speaking</Badge>}
                </div>
              </div>
            )}

            {/* Enhanced Conversation History */}
            <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
              {messages.length === 0 ? (
                <div className="text-center py-8">
                  <div className="mb-4">
                    {isVoiceMode ? (
                      <Mic className="w-12 h-12 mx-auto text-primary mb-3" />
                    ) : (
                      <MessageSquare className="w-12 h-12 mx-auto text-primary mb-3" />
                    )}
                  </div>
                  <div className="text-foreground font-medium mb-2">
                    Connected via {isVoiceMode ? 'Voice Mode' : 'Text Mode'}
                  </div>
                  <div className="text-sm text-muted-foreground mb-4">
                    {isVoiceMode 
                      ? `Ready for voice conversation in ${currentSubject}. Speak naturally with your AI tutor.`
                      : `Ready for text-based learning in ${currentSubject}. Type your questions below.`
                    }
                  </div>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>Session started • Level: {learningStats.skillLevel} • Duration: {getDetailedStatus().sessionDuration}</div>
                    <div>Connection Quality: {getDetailedStatus().connectionQuality} • Avg Confidence: {getDetailedStatus().averageConfidence}</div>
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`p-4 rounded-lg transition-all duration-200 ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-accent/20 to-primary/10 border border-accent/30 ml-8'
                        : message.type === 'error'
                        ? 'bg-gradient-to-r from-destructive/20 to-destructive/10 border border-destructive/30 mr-8'
                        : 'bg-gradient-to-r from-primary/20 to-accent/10 border border-primary/30 mr-8'
                    }`}
                  >
                    {/* Message Header with Detailed Information */}
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-sm font-medium ${
                          message.role === 'user'
                            ? 'bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent'
                            : 'bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent'
                        }`}>
                          {message.role === 'user' ? 'You' : 'Bakame AI'}
                        </span>
                        
                        {/* Message Type Badge */}
                        {message.type && (
                          <Badge variant="outline" className="text-xs border-border text-muted-foreground">
                            {message.type}
                          </Badge>
                        )}
                        
                        {/* Category Badge */}
                        {message.category && (
                          <Badge variant="secondary" className="text-xs">
                            {message.category}
                          </Badge>
                        )}
                        
                        {/* Skill Level Indicator */}
                        {message.skillLevel && (
                          <Badge variant="outline" className={`text-xs ${
                            message.skillLevel === 'beginner' ? 'border-green-500 text-green-500' :
                            message.skillLevel === 'intermediate' ? 'border-yellow-500 text-yellow-500' :
                            'border-red-500 text-red-500'
                          }`}>
                            {message.skillLevel}
                          </Badge>
                        )}
                        
                        {/* Difficulty Level */}
                        {message.difficulty && (
                          <Badge variant="outline" className="text-xs">
                            {message.difficulty}
                          </Badge>
                        )}
                      </div>
                      
                      {/* Message Metrics */}
                      <div className="flex items-center gap-2 text-xs text-muted-foreground flex-wrap">
                        {/* Confidence Score */}
                        {message.confidence && (
                          <span className={`px-2 py-1 rounded ${
                            message.confidence > 0.8 ? 'bg-green-100 text-green-700' :
                            message.confidence > 0.6 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            {Math.round(message.confidence * 100)}%
                          </span>
                        )}
                        
                        {/* Word Count */}
                        {message.wordCount && (
                          <span className="text-muted-foreground">
                            {message.wordCount} words
                          </span>
                        )}
                        
                        {/* Processing Time for AI responses */}
                        {message.processingTime && message.role === 'assistant' && (
                          <span className="text-muted-foreground">
                            {(message.processingTime / 1000).toFixed(1)}s response
                          </span>
                        )}
                        
                        <span className="text-muted-foreground">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                    
                    {/* Message Content */}
                    <p className="text-foreground mb-2">{message.content}</p>
                    
                    {/* Topics Addressed */}
                    {message.topicsAddressed && message.topicsAddressed.length > 0 && (
                      <div className="mb-2">
                        <span className="text-xs font-medium text-muted-foreground">Topics covered: </span>
                        <div className="inline-flex gap-1 flex-wrap">
                          {message.topicsAddressed.map((topic, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {topic}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Learning Insight */}
                    {message.learningInsight && (
                      <div className="mt-2 p-3 bg-muted/30 rounded text-xs text-muted-foreground border-l-2 border-primary">
                        <span className="font-medium">💡 Learning Insight:</span> {message.learningInsight}
                      </div>
                    )}
                    
                    {/* Message Analytics */}
                    <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
                      {message.type === 'voice' && (
                        <span className="flex items-center gap-1">
                          <Mic className="w-3 h-3" />
                          Voice Message
                        </span>
                      )}
                      {message.type === 'text' && (
                        <span className="flex items-center gap-1">
                          <Type className="w-3 h-3" />
                          Text Message
                        </span>
                      )}
                      {message.role === 'assistant' && (
                        <span className="flex items-center gap-1">
                          <Brain className="w-3 h-3" />
                          AI Generated
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
              
              {/* Enhanced Processing Indicator */}
              {isProcessing && (
                <div className="bg-gradient-to-r from-primary/20 to-accent/10 border border-primary/30 mr-8 p-4 rounded-lg">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent text-sm font-medium">
                      Bakame AI
                    </span>
                    <Badge variant="outline" className="text-xs border-border text-muted-foreground">
                      processing
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      {learningStats.skillLevel}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      Analyzing your {isVoiceMode ? 'voice' : 'text'} input...
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm mb-2">
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                    <span className="text-muted-foreground">
                      Processing complex language patterns and preparing personalized response with learning insights...
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Expected response time: 1-3 seconds • Personalizing for {currentSubject} level {learningStats.skillLevel}
                  </div>
                </div>
              )}
            </div>

            {/* Input Area */}
            {!isVoiceMode ? (
              <div className="flex gap-2">
                <Input
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={`Ask your ${currentSubject} question or request practice exercises...`}
                  disabled={isProcessing}
                  className="flex-1 bg-input border-border text-foreground placeholder-muted-foreground"
                />
                <Button
                  onClick={() => sendMessage()}
                  disabled={!currentInput.trim() || isProcessing}
                  className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
                >
                  {isProcessing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            ) : (
              <div className="text-center">
                <Button
                  onClick={toggleListening}
                  variant={isListening ? "destructive" : "default"}
                  size="lg"
                  className="rounded-full w-16 h-16 mb-2"
                >
                  <Mic className="w-6 h-6" />
                </Button>
                <p className="text-sm text-muted-foreground">
                  {isListening ? 'Tap to stop listening - Speak clearly and naturally' : 'Tap to speak - AI is ready to listen'}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Voice recognition optimized for {currentSubject} learning
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Enhanced Subject-Specific Quick Actions */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            {(() => {
              const subject = SUBJECTS.find(s => s.id === currentSubject);
              const IconComponent = subject?.icon || BookOpen;
              return (
                <>
                  <IconComponent className="w-5 h-5 text-primary" />
                  <h3 className="text-lg font-semibold text-foreground">
                    {subject?.name} Learning Activities
                  </h3>
                  <Badge variant="outline" className="text-xs">
                    Personalized for {learningStats.skillLevel} level
                  </Badge>
                </>
              );
            })()}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {QUICK_ACTIONS[currentSubject as keyof typeof QUICK_ACTIONS]?.map((action, index) => (
              <Button
                key={index}
                onClick={() => sendMessage(action.prompt)}
                variant="outline"
                className="border-border text-foreground hover:bg-muted p-4 h-auto text-left"
                disabled={isProcessing}
              >
                <div className="w-full">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium">{action.title}</div>
                    <Badge variant="outline" className="text-xs">
                      {action.difficulty}
                    </Badge>
                  </div>
                  <div className="text-sm text-muted-foreground mb-2">
                    {action.description}
                  </div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Duration: {action.estimatedTime}</span>
                    <div className="flex gap-1">
                      {action.skills.slice(0, 2).map((skill, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnifiedBakameInterface;
