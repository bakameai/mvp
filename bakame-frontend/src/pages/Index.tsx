import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronDown, Menu, X, Phone, MessageSquare, Calendar, BookOpen, ArrowRight, Play, Users, Shield, Zap, Target, CheckCircle, GraduationCap, Languages, Headphones, Brain, Mic, Database, Globe, BarChart3, Volume2, Newspaper, Building } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import TypingAnimation from '@/components/TypingAnimation';
import EarlyAccessModal from '@/components/EarlyAccessModal';
import VideoModal from '@/components/VideoModal';
import FAQ from '@/components/FAQ';
import { ThemeToggle } from '@/components/theme/ThemeToggle';
import LiveChat from '@/components/chat/LiveChat';
const Index = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isEarlyAccessOpen, setIsEarlyAccessOpen] = useState(false);
  const [isVideoOpen, setIsVideoOpen] = useState(false);
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };
  const closeMenu = () => {
    setIsMenuOpen(false);
  };
  const openEarlyAccess = () => {
    setIsEarlyAccessOpen(true);
  };
  const openVideo = () => {
    setIsVideoOpen(true);
  };
  return <div className="min-h-screen bg-background text-foreground relative overflow-hidden">
      {/* Enhanced space-time background */}
      <div className="absolute inset-0 overflow-hidden">
        <svg className="absolute inset-0 w-full h-full opacity-20" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="1" result="coloredBlur" />
              <feMerge> 
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <g transform="translate(0,0)">
            <path d="M0,25 Q25,20 50,25 T100,25" fill="none" stroke="rgba(34,197,94,0.4)" strokeWidth="0.2" filter="url(#glow)" />
            <path d="M0,50 Q25,45 50,50 T100,50" fill="none" stroke="rgba(59,130,246,0.3)" strokeWidth="0.2" />
            <path d="M0,75 Q25,70 50,75 T100,75" fill="none" stroke="rgba(34,197,94,0.4)" strokeWidth="0.2" filter="url(#glow)" />
          </g>
        </svg>
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-green-500/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/3 right-1/3 w-72 h-72 bg-blue-500/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-50 flex items-center justify-between p-6 md:p-8">
        <div className="flex items-center space-x-4">
          <div className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
            Bakame AI
          </div>
          <Badge variant="outline" className="border-primary/30 text-primary text-xs">
            Beta
          </Badge>
        </div>
        
        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          <Link to="/" className="text-foreground hover:text-primary transition-colors">Home</Link>
          <Link to="/ivr" className="text-foreground hover:text-primary transition-colors font-semibold">
            <span className="flex items-center gap-1">
              <Brain className="h-4 w-4" />
              Bakame AI
            </span>
          </Link>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <span className="flex items-center text-foreground hover:text-primary transition-colors cursor-pointer">
                Use Cases <ChevronDown className="ml-1 h-4 w-4" />
              </span>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-background border-border z-50">
              <DropdownMenuItem>
                <span className="text-foreground">Government</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <span className="text-foreground">Enterprise</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <span className="text-foreground">Education</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Link to="/about" className="text-foreground hover:text-primary transition-colors">About</Link>
          <Link to="/team" className="text-foreground hover:text-primary transition-colors">Team</Link>
          <Link to="/contact" className="text-foreground hover:text-primary transition-colors">Contact</Link>
          <ThemeToggle />
        </div>

        {/* Mobile menu button */}
        <div className="md:hidden">
          <button onClick={toggleMenu} className="text-foreground hover:text-primary transition-colors">
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Desktop CTA */}
        <div className="hidden md:block">
          
        </div>
      </nav>

      {/* Mobile Navigation Menu */}
      {isMenuOpen && <div className="md:hidden fixed inset-0 z-40 bg-background/95 backdrop-blur-sm">
          <div className="flex flex-col items-center justify-center h-full space-y-8">
            <Link to="/" onClick={closeMenu} className="text-2xl text-foreground hover:text-primary transition-colors">Home</Link>
            <Link to="/ivr" onClick={closeMenu} className="text-2xl text-foreground hover:text-primary transition-colors">Try English Learning</Link>
            <div className="text-center">
              <div className="text-xl text-foreground mb-4">Use Cases</div>
              <div className="space-y-4">
                <span className="block text-foreground">Government</span>
                <span className="block text-foreground">Enterprise</span>
                <span className="block text-foreground">Education</span>
              </div>
            </div>
            <Link to="/about" onClick={closeMenu} className="text-2xl text-foreground hover:text-primary transition-colors">About</Link>
            <Link to="/team" onClick={closeMenu} className="text-2xl text-foreground hover:text-primary transition-colors">Team</Link>
            <Link to="/contact" onClick={closeMenu} className="text-2xl text-foreground hover:text-primary transition-colors">Contact</Link>
            <div className="pt-4">
              <ThemeToggle />
            </div>
            <Button onClick={() => {
          closeMenu();
          openEarlyAccess();
        }} className="bg-gradient-to-r from-primary to-accent text-primary-foreground hover:opacity-90 transition-all duration-300 transform hover:scale-105">
              Sign Up for Early Access
            </Button>
          </div>
        </div>}

      {/* Main Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="container mx-auto px-6 py-20 text-center">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent leading-tight">
              Learn English with AI Voice Tutor
            </h1>
            
            <div className="text-xl md:text-2xl text-muted-foreground mb-8 h-16 flex items-center justify-center">
              <TypingAnimation text="Your personal English tutor powered by AI - practice speaking, learn vocabulary, and improve pronunciation." className="text-muted-foreground" />
            </div>
            
            <p className="text-lg text-muted-foreground mb-12 max-w-2xl mx-auto">
              Bakame AI is an English learning platform that helps you practice conversation, 
              build vocabulary, and improve pronunciation through real-time voice interaction. 
              Perfect for learners who want to speak English confidently.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Button onClick={openEarlyAccess} className="bg-gradient-to-r from-primary to-accent text-primary-foreground hover:opacity-90 transition-all duration-300 transform hover:scale-105 text-lg px-8 py-4">
                <GraduationCap className="mr-2 h-5 w-5" />
                Sign Up for Early Access
              </Button>
              
              
            </div>

            {/* Learning Features */}
            <div className="flex flex-wrap justify-center gap-4 mb-16">
              <div className="px-4 py-2 bg-gradient-to-r from-primary/20 to-accent/20 rounded-lg border border-border flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-foreground" />
                <span className="text-muted-foreground">Conversation Practice</span>
              </div>
              
              <div className="px-4 py-2 bg-gradient-to-r from-accent/20 to-primary/20 rounded-lg border border-border flex items-center gap-2">
                <Brain className="h-4 w-4 text-foreground" />
                <span className="text-muted-foreground">Vocabulary Building</span>
              </div>
              
              <div className="px-4 py-2 bg-gradient-to-r from-secondary/20 to-accent/20 rounded-lg border border-border flex items-center gap-2">
                <Mic className="h-4 w-4 text-foreground" />
                <span className="text-muted-foreground">Pronunciation Help</span>
              </div>
            </div>

            {/* Other Use Cases */}
            <div className="flex flex-wrap justify-center gap-4 mb-16">
              <div className="px-4 py-2 bg-gradient-to-r from-primary/20 to-accent/20 rounded-lg border border-border flex items-center gap-2">
                <Building className="h-4 w-4 text-foreground" />
                <span className="text-muted-foreground">Enterprise Solutions</span>
              </div>
              
              <div className="px-4 py-2 bg-gradient-to-r from-accent/20 to-primary/20 rounded-lg border border-border flex items-center gap-2">
                <Shield className="h-4 w-4 text-foreground" />
                <span className="text-muted-foreground">Government Services</span>
              </div>
              
              <div className="px-4 py-2 bg-gradient-to-r from-secondary/20 to-accent/20 rounded-lg border border-border flex items-center gap-2">
                <Users className="h-4 w-4 text-foreground" />
                <span className="text-muted-foreground">Customer Support</span>
              </div>
            </div>
          </div>
        </section>

        {/* Core Learning Modules */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center text-foreground">
              Core Learning Modules
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Languages className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">English Practice</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Grammar correction, pronunciation feedback, and conversation practice to improve your English fluency.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Brain className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Math Module</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Mental math problems with adaptive difficulty progression to strengthen your mathematical skills.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <BookOpen className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Reading Comprehension</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Story-based learning with questions to improve your reading and understanding skills.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <MessageSquare className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Debate Practice</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Structured debate topics with counter-arguments to enhance your critical thinking and communication.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Target className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">General Q&A</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Multi-topic conversations and help system for general knowledge and assistance.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Building className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Business Solutions</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Enterprise support, customer service automation, and professional communication assistance.
                  </CardDescription>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Technical Infrastructure */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center text-foreground">
              Technical Infrastructure
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Phone className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Voice & SMS Access</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Twilio integration for phone-based learning, accessible from any phone without internet.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Zap className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">AI Integration</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Llama API with OpenAI fallback for response generation, ensuring reliable AI interactions.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Mic className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Voice Transcription</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    OpenAI Whisper for accurate speech-to-text processing in multiple languages.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Database className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Memory System</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Redis-based conversation history and user context for personalized learning experiences.
                  </CardDescription>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Advanced Features */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center text-foreground">
              Advanced Features
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Globe className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Cultural Integration</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Rwanda-specific content with Kinyarwanda phrases for better cultural understanding.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <BarChart3 className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Admin Dashboard</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    User analytics, session tracking, and curriculum alignment for comprehensive insights.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Volume2 className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Deepgram TTS</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    High-quality voice synthesis for better audio experience and natural conversations.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Newspaper className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Dynamic Content</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    NewsAPI integration for trending debate topics and current events discussions.
                  </CardDescription>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Why Learn English with AI */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-8 text-foreground">
              Why Learn English with Bakame AI?
            </h2>
            <p className="text-lg text-muted-foreground mb-12 max-w-2xl mx-auto">
              Traditional language learning can be expensive and time-consuming. 
              Our AI tutor is available 24/7 to help you practice English at your own pace.
            </p>
          </div>
        </section>

        {/* Learning Methods */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center text-foreground">
              How You'll Learn English
            </h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Languages className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Conversation Practice</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Practice real conversations with AI. Discuss topics, ask questions, and get instant feedback on your speaking.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <BookOpen className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Vocabulary Building</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Learn new words in context with explanations in both English and Kinyarwanda for better understanding.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Headphones className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Pronunciation Help</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Get help with difficult sounds, stress patterns, and intonation to speak English more naturally.
                  </CardDescription>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Other Use Cases */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center text-foreground">
              Our Voice AI Technology Powers More Than Learning
            </h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Shield className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Government Services</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Emergency services, citizen support, and public information systems that work even during network outages.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Users className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Healthcare</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Patient support hotlines and appointment systems that remain accessible during network issues.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm hover:bg-card/80 transition-all duration-300">
                <CardHeader>
                  <Zap className="h-8 w-8 text-foreground mb-2" />
                  <CardTitle className="text-card-foreground">Enterprise</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    Customer service and internal communication systems that work reliably without internet dependency.
                  </CardDescription>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center text-foreground">
              Why Choose Bakame AI for English Learning?
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <CheckCircle className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">Available 24/7</h3>
                    <p className="text-muted-foreground">Practice English anytime, anywhere. Your AI tutor never sleeps.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <CheckCircle className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">Personalized Learning</h3>
                    <p className="text-muted-foreground">Adapted to your level and learning pace, with support in Kinyarwanda when needed.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <CheckCircle className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">Real Voice Interaction</h3>
                    <p className="text-muted-foreground">Practice speaking and listening with natural voice conversations, not just text.</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <CheckCircle className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">Instant Feedback</h3>
                    <p className="text-muted-foreground">Get immediate corrections and suggestions to improve your English quickly.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <CheckCircle className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">Practical Focus</h3>
                    <p className="text-muted-foreground">Learn English for real-world situations like job interviews, business meetings, and daily conversations.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <CheckCircle className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">Culturally Aware</h3>
                    <p className="text-muted-foreground">Designed specifically for Rwandan learners with cultural context and local examples.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* User Testimonials */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center text-foreground">
              What Early Users Are Saying
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <Card className="bg-card border-border backdrop-blur-sm">
                <CardContent className="p-8">
                  <p className="text-muted-foreground italic mb-4">
                    "This AI tutor is patient and helps me practice English conversations. 
                    I'm excited to improve my speaking skills!"
                  </p>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
                      <span className="text-primary-foreground font-bold">AM</span>
                    </div>
                    <div>
                      <p className="text-foreground font-semibold">Alex M.</p>
                      <p className="text-muted-foreground text-sm">University Student</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card border-border backdrop-blur-sm">
                <CardContent className="p-8">
                  <p className="text-muted-foreground italic mb-4">
                    "Finally, a way to practice English speaking without feeling embarrassed. 
                    The AI understands my accent and helps me improve."
                  </p>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-secondary rounded-full flex items-center justify-center">
                      <span className="text-secondary-foreground font-bold">SM</span>
                    </div>
                    <div>
                      <p className="text-foreground font-semibold">Sarah M.</p>
                      <p className="text-muted-foreground text-sm">Business Professional</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-foreground">
              Ready to Start Learning English?
            </h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join thousands of learners who are improving their English speaking skills 
              with our AI-powered voice tutor. Start your journey today.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button onClick={openEarlyAccess} className="bg-gradient-to-r from-primary to-accent text-primary-foreground hover:opacity-90 transition-all duration-300 transform hover:scale-105 text-lg px-8 py-4">
                <GraduationCap className="mr-2 h-5 w-5" />
                Sign Up for Early Access
              </Button>
              
              <Link to="/contact">
                <Button variant="outline" className="border-border text-foreground hover:bg-muted transition-all duration-300 text-lg px-8 py-4">
                  <MessageSquare className="mr-2 h-5 w-5" />
                  Contact Us
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Blog Section */}
        <section className="container mx-auto px-6 py-20 bg-muted/30">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
              Latest News & Updates
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Stay updated with our latest developments, media coverage, and industry insights
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <Card className="bg-card/80 backdrop-blur-sm border-border hover:shadow-lg transition-all duration-300">
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-primary font-medium">Media Coverage</span>
                  <span className="text-sm text-muted-foreground">2025</span>
                </div>
                <CardTitle className="text-xl">Bakame AI Featured in Dallas Innovates</CardTitle>
                <CardDescription>
                  Our innovative AI solutions and startup journey highlighted in Dallas's leading innovation publication.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <a 
                  href="https://dallasinnovates.com/tag/bakame-ai/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-primary hover:text-primary/80 transition-colors"
                >
                  Read Article <ArrowRight className="ml-2 h-4 w-4" />
                </a>
              </CardContent>
            </Card>

            <Card className="bg-card/80 backdrop-blur-sm border-border hover:shadow-lg transition-all duration-300">
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-primary font-medium">Innovation Award</span>
                  <span className="text-sm text-muted-foreground">2025</span>
                </div>
                <CardTitle className="text-xl">CREATE Competition Winner 2025</CardTitle>
                <CardDescription>
                  Bakame AI recognized as winner in TCU Neeley's CREATE innovation competition for groundbreaking AI solutions.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <a 
                  href="https://www.neeley.tcu.edu/News/Events/CREATE-Winners-2025" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-primary hover:text-primary/80 transition-colors"
                >
                  Read More <ArrowRight className="ml-2 h-4 w-4" />
                </a>
              </CardContent>
            </Card>

            <Card className="bg-card/80 backdrop-blur-sm border-border hover:shadow-lg transition-all duration-300">
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-primary font-medium">Education Coverage</span>
                  <span className="text-sm text-muted-foreground">May 2025</span>
                </div>
                <CardTitle className="text-xl">Higher Ed Leadership Recognition</CardTitle>
                <CardDescription>
                  Bakame AI's impact on educational technology featured in Fort Worth Report's higher education coverage.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <a 
                  href="https://fortworthreport.org/2025/05/26/higher-ed-footnotes-new-leadership-takes-helm-on-tcc-board/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-primary hover:text-primary/80 transition-colors"
                >
                  Read Article <ArrowRight className="ml-2 h-4 w-4" />
                </a>
              </CardContent>
            </Card>
          </div>

          <div className="text-center">
            <Link to="/blog">
              <Button variant="outline" className="border-border text-foreground hover:bg-muted transition-all duration-300">
                View All Articles <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="container mx-auto px-6 py-20">
          <FAQ />
        </section>

        {/* Footer */}
        <footer className="border-t border-border bg-card/50 backdrop-blur-sm">
          <div className="container mx-auto px-6 py-12">
            <div className="grid md:grid-cols-4 gap-8">
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-4">Company</h3>
                <ul className="space-y-2">
                  <li><Link to="/about" className="text-muted-foreground hover:text-foreground transition-colors">About</Link></li>
                  <li><Link to="/team" className="text-muted-foreground hover:text-foreground transition-colors">Team</Link></li>
                  <li><Link to="/blog" className="text-muted-foreground hover:text-foreground transition-colors">Blog</Link></li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-4">Learning</h3>
                <ul className="space-y-2">
                  <li><Link to="/ivr" className="text-muted-foreground hover:text-foreground transition-colors">Try English Learning</Link></li>
                  <li><Link to="/support" className="text-muted-foreground hover:text-foreground transition-colors">Help Center</Link></li>
                  <li><Link to="/contact" className="text-muted-foreground hover:text-foreground transition-colors">Contact Support</Link></li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-4">Use Cases</h3>
                <ul className="space-y-2">
                  <li><Link to="/government-solution" className="text-muted-foreground hover:text-foreground transition-colors">Government</Link></li>
                  <li><Link to="/enterprise-solution" className="text-muted-foreground hover:text-foreground transition-colors">Enterprise</Link></li>
                  <li><Link to="/education-solution" className="text-muted-foreground hover:text-foreground transition-colors">Education</Link></li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-4">Legal</h3>
                <ul className="space-y-2">
                  <li><Link to="/privacy" className="text-muted-foreground hover:text-foreground transition-colors">Privacy Policy</Link></li>
                  <li><Link to="/terms" className="text-muted-foreground hover:text-foreground transition-colors">Terms of Service</Link></li>
                </ul>
              </div>
            </div>
            
            <div className="border-t border-border pt-8 mt-8 text-center">
              <p className="text-muted-foreground">© 2025 Bakame AI. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>

      {/* Modals */}
      <EarlyAccessModal isOpen={isEarlyAccessOpen} onClose={() => setIsEarlyAccessOpen(false)} />
      
      <VideoModal isOpen={isVideoOpen} onClose={() => setIsVideoOpen(false)} videoId="dQw4w9WgXcQ" />
      
      {/* Live Chat */}
      <LiveChat />
    </div>;
};
export default Index;