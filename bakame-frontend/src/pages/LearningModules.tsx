import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { BookOpen, Users, Clock, Star, Phone, MessageSquare } from "lucide-react";

interface LearningModule {
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration: string;
  participants: number;
  rating: number;
  topics: string[];
  available_via: ('voice' | 'sms')[];
}

const LearningModules: React.FC = () => {
  const [modules] = useState<LearningModule[]>([
    {
      name: "English Basics",
      description: "Learn fundamental English vocabulary and grammar through interactive conversations",
      difficulty: "beginner",
      duration: "15-20 min",
      participants: 1250,
      rating: 4.8,
      topics: ["Greetings", "Numbers", "Colors", "Family", "Food"],
      available_via: ["voice", "sms"]
    },
    {
      name: "Math Fundamentals",
      description: "Practice arithmetic, algebra, and problem-solving with AI guidance",
      difficulty: "beginner",
      duration: "10-15 min",
      participants: 980,
      rating: 4.7,
      topics: ["Addition", "Subtraction", "Multiplication", "Division", "Word Problems"],
      available_via: ["voice", "sms"]
    },
    {
      name: "Science Exploration",
      description: "Discover basic scientific concepts through questions and experiments",
      difficulty: "intermediate",
      duration: "20-25 min",
      participants: 650,
      rating: 4.6,
      topics: ["Physics", "Chemistry", "Biology", "Earth Science"],
      available_via: ["voice"]
    },
    {
      name: "Debate & Discussion",
      description: "Improve critical thinking and argumentation skills through structured debates",
      difficulty: "advanced",
      duration: "25-30 min",
      participants: 420,
      rating: 4.9,
      topics: ["Current Events", "Ethics", "Social Issues", "Logic"],
      available_via: ["voice"]
    },
    {
      name: "Reading Comprehension",
      description: "Enhance reading skills with stories, articles, and comprehension exercises",
      difficulty: "intermediate",
      duration: "15-20 min",
      participants: 780,
      rating: 4.5,
      topics: ["Short Stories", "News Articles", "Poetry", "Analysis"],
      available_via: ["voice", "sms"]
    }
  ]);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleStartModule = (moduleName: string) => {
    alert(`Starting ${moduleName} module. In production, this would connect you to the AI tutor via phone or SMS.`);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Learning Modules</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Choose from our AI-powered learning modules. Each module provides personalized tutoring 
          through voice calls or SMS, adapting to your learning pace and style.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modules.map((module) => (
          <Card key={module.name} className="flex flex-col">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">{module.name}</CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge className={getDifficultyColor(module.difficulty)}>
                      {module.difficulty}
                    </Badge>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {module.duration}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm font-medium">{module.rating}</span>
                </div>
              </div>
              <CardDescription>{module.description}</CardDescription>
            </CardHeader>

            <CardContent className="flex-1 space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Participants</span>
                  <div className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    <span>{module.participants.toLocaleString()}</span>
                  </div>
                </div>
                <Progress value={(module.participants / 1500) * 100} className="h-2" />
              </div>

              <div className="space-y-2">
                <span className="text-sm font-medium">Topics Covered:</span>
                <div className="flex flex-wrap gap-1">
                  {module.topics.map((topic) => (
                    <Badge key={topic} variant="outline" className="text-xs">
                      {topic}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-sm font-medium">Available via:</span>
                <div className="flex gap-2">
                  {module.available_via.includes('voice') && (
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Phone className="h-3 w-3" />
                      Voice Call
                    </Badge>
                  )}
                  {module.available_via.includes('sms') && (
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <MessageSquare className="h-3 w-3" />
                      SMS
                    </Badge>
                  )}
                </div>
              </div>

              <Button 
                className="w-full mt-auto" 
                onClick={() => handleStartModule(module.name)}
              >
                <BookOpen className="h-4 w-4 mr-2" />
                Start Learning
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Phone className="h-5 w-5" />
            How to Access Learning Modules
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium flex items-center gap-2">
                <Phone className="h-4 w-4" />
                Voice Learning
              </h4>
              <p className="text-sm text-muted-foreground">
                Call our AI tutor at <strong>+250-XXX-XXXX</strong> and say the module name 
                to start an interactive voice learning session.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                SMS Learning
              </h4>
              <p className="text-sm text-muted-foreground">
                Text the module name to <strong>+250-XXX-XXXX</strong> to receive 
                interactive lessons and exercises via SMS.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LearningModules;
