import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Phone, MessageSquare, Play, Pause, Volume2, Mic, Settings } from "lucide-react";

const IVRInterface: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [currentModule, setCurrentModule] = useState<string | null>(null);
  const [phoneNumber, setPhoneNumber] = useState('');

  const modules = [
    { id: 'english', name: 'English Basics', description: 'Learn fundamental English' },
    { id: 'math', name: 'Math Fundamentals', description: 'Practice arithmetic and algebra' },
    { id: 'science', name: 'Science Exploration', description: 'Discover scientific concepts' },
    { id: 'debate', name: 'Debate & Discussion', description: 'Improve critical thinking' },
    { id: 'reading', name: 'Reading Comprehension', description: 'Enhance reading skills' }
  ];

  const handleConnect = () => {
    if (phoneNumber) {
      setIsConnected(true);
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setCurrentModule(null);
  };

  const handleStartModule = (moduleId: string) => {
    setCurrentModule(moduleId);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">IVR Interface</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Interactive Voice Response system for testing and managing AI learning sessions.
          This interface simulates the telephony experience for development and testing.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Connection Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Phone className="h-5 w-5" />
              Connection
            </CardTitle>
            <CardDescription>
              Simulate phone connection to the AI tutor
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Phone Number</label>
              <Input
                placeholder="+250-XXX-XXX-XXX"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                disabled={isConnected}
              />
            </div>

            <div className="flex items-center justify-between">
              <Badge variant={isConnected ? "default" : "secondary"}>
                {isConnected ? "Connected" : "Disconnected"}
              </Badge>
              {isConnected ? (
                <Button variant="destructive" onClick={handleDisconnect}>
                  Hang Up
                </Button>
              ) : (
                <Button onClick={handleConnect} disabled={!phoneNumber}>
                  <Phone className="h-4 w-4 mr-2" />
                  Call
                </Button>
              )}
            </div>

            {isConnected && (
              <div className="space-y-3 pt-4 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Call Duration</span>
                  <span className="text-sm font-mono">00:45</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Audio Quality</span>
                  <div className="flex items-center gap-1">
                    <Volume2 className="h-3 w-3" />
                    <span className="text-sm">Good</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Main Interface */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Learning Session</CardTitle>
            <CardDescription>
              {isConnected 
                ? "Choose a learning module to start your AI tutoring session"
                : "Connect to start a learning session"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!isConnected ? (
              <div className="text-center py-12 text-muted-foreground">
                <Phone className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Connect your phone to start learning</p>
              </div>
            ) : (
              <Tabs defaultValue="modules" className="space-y-4">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="modules">Learning Modules</TabsTrigger>
                  <TabsTrigger value="conversation">Conversation</TabsTrigger>
                </TabsList>

                <TabsContent value="modules" className="space-y-4">
                  <div className="grid gap-3">
                    {modules.map((module) => (
                      <div
                        key={module.id}
                        className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                          currentModule === module.id 
                            ? 'border-primary bg-primary/5' 
                            : 'hover:bg-muted/50'
                        }`}
                        onClick={() => handleStartModule(module.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium">{module.name}</h4>
                            <p className="text-sm text-muted-foreground">{module.description}</p>
                          </div>
                          {currentModule === module.id && (
                            <Badge>Active</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="conversation" className="space-y-4">
                  {currentModule ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">
                          Active: {modules.find(m => m.id === currentModule)?.name}
                        </h4>
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline">
                            <Mic className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Settings className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      <div className="bg-muted/50 rounded-lg p-4 space-y-3">
                        <div className="space-y-2">
                          <div className="bg-primary/10 rounded-lg p-3">
                            <p className="text-sm">
                              <strong>AI Tutor:</strong> Hello! Welcome to {modules.find(m => m.id === currentModule)?.name}. 
                              I'm here to help you learn. What would you like to start with today?
                            </p>
                          </div>
                          <div className="bg-background rounded-lg p-3 ml-8">
                            <p className="text-sm">
                              <strong>You:</strong> I'd like to practice basic vocabulary.
                            </p>
                          </div>
                          <div className="bg-primary/10 rounded-lg p-3">
                            <p className="text-sm">
                              <strong>AI Tutor:</strong> Great choice! Let's start with everyday objects. 
                              Can you tell me what you use to write?
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Button size="sm">
                          <Play className="h-4 w-4 mr-2" />
                          Speak
                        </Button>
                        <Button size="sm" variant="outline">
                          <Pause className="h-4 w-4 mr-2" />
                          Pause
                        </Button>
                        <Button size="sm" variant="outline">
                          End Session
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>Select a learning module to start the conversation</p>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle>IVR System Information</CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <h4 className="font-medium">Voice Commands</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• "Start [module name]" - Begin a learning session</li>
              <li>• "Help" - Get assistance and options</li>
              <li>• "Repeat" - Repeat the last question</li>
              <li>• "Stop" - End current session</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">SMS Commands</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Text module name to start learning</li>
              <li>• "HELP" - Get list of available modules</li>
              <li>• "STOP" - Unsubscribe from SMS learning</li>
              <li>• "STATUS" - Check your learning progress</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default IVRInterface;
