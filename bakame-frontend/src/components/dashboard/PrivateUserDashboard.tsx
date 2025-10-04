
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  User, 
  Phone, 
  MessageCircle, 
  Settings, 
  Calendar,
  Clock,
  Headphones,
  Activity
} from "lucide-react";

export const PrivateUserDashboard = () => {
  const mockData = {
    totalCalls: 245,
    monthlyMinutes: 1280,
    avgCallDuration: "5.2 min",
    responseRate: 94.5,
    recentCalls: [
      { contact: "Dr. Smith's Office", time: "2 hours ago", duration: "3:24", type: "incoming" },
      { contact: "Bank Customer Service", time: "1 day ago", duration: "8:15", type: "outgoing" },
      { contact: "Insurance Company", time: "2 days ago", duration: "12:30", type: "incoming" },
      { contact: "Tech Support", time: "3 days ago", duration: "6:45", type: "outgoing" }
    ],
    quickActions: [
      { title: "Schedule Call", description: "Set up automated callbacks", icon: Calendar },
      { title: "Voice Messages", description: "Manage your voicemail", icon: MessageCircle },
      { title: "Call Settings", description: "Configure preferences", icon: Settings },
      { title: "Usage Reports", description: "View detailed analytics", icon: Activity }
    ]
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Personal Dashboard</h1>
          <p className="text-muted-foreground">Your intelligent voice communication hub</p>
        </div>
        <Button className="flex items-center space-x-2">
          <Phone className="w-4 h-4" />
          <span>Make Call</span>
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Calls</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.totalCalls}</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Talk Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.monthlyMinutes} min</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+8%</span> from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg Call Duration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.avgCallDuration}</div>
            <p className="text-xs text-muted-foreground">Per conversation</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Response Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.responseRate}%</div>
            <p className="text-xs text-muted-foreground">Calls answered</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Clock className="w-5 h-5" />
            <span>Recent Calls</span>
          </CardTitle>
          <CardDescription>Your latest call activity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockData.recentCalls.map((call, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Phone className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-medium">{call.contact}</h3>
                    <p className="text-sm text-muted-foreground">{call.time}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium">{call.duration}</div>
                  <Badge variant={call.type === 'incoming' ? 'default' : 'secondary'}>
                    {call.type}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {mockData.quickActions.map((action, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
            <CardHeader className="pb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <action.icon className="w-6 h-6 text-blue-600" />
              </div>
              <CardTitle className="text-lg">{action.title}</CardTitle>
              <CardDescription>{action.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full">
                Get Started
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* AI Assistant */}
      <Card className="border-purple-200 bg-gradient-to-r from-purple-50 to-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-purple-800">
            <Headphones className="w-5 h-5" />
            <span>AI Voice Assistant</span>
          </CardTitle>
          <CardDescription>Enhance your calling experience with intelligent features</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium text-purple-800">Smart Features</h4>
              <ul className="text-sm text-purple-700 space-y-1">
                <li>• Call transcription and summaries</li>
                <li>• Intelligent call routing</li>
                <li>• Voice-activated commands</li>
              </ul>
            </div>
            <div className="space-y-3">
              <Button className="w-full bg-purple-600 hover:bg-purple-700">
                Enable AI Assistant
              </Button>
              <Button variant="outline" className="w-full border-purple-300 text-purple-700">
                Learn More
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
