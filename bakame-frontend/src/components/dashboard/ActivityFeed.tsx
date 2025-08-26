import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

interface Activity {
  id: number;
  user: string;
  action: string;
  target: string;
  timestamp: Date;
  type: "create" | "update" | "delete" | "login" | "logout";
}

const activities: Activity[] = [
  {
    id: 1,
    user: "Student #247",
    action: "completed",
    target: "IVR English Conversation Session",
    timestamp: new Date(Date.now() - 3 * 60 * 1000),
    type: "create"
  },
  {
    id: 2,
    user: "Kigali Primary School",
    action: "initiated",
    target: "25 new IVR learning sessions",
    timestamp: new Date(Date.now() - 8 * 60 * 1000),
    type: "login"
  },
  {
    id: 3,
    user: "Student #189",
    action: "achieved",
    target: "Level 3 Speaking Proficiency",
    timestamp: new Date(Date.now() - 12 * 60 * 1000),
    type: "create"
  },
  {
    id: 4,
    user: "IVR System",
    action: "processed",
    target: "147 voice interactions today",
    timestamp: new Date(Date.now() - 25 * 60 * 1000),
    type: "update"
  },
  {
    id: 5,
    user: "Teacher Uwimana",
    action: "reviewed",
    target: "student IVR progress reports",
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    type: "update"
  },
  {
    id: 6,
    user: "Musanze Secondary",
    action: "downloaded",
    target: "offline lesson content package",
    timestamp: new Date(Date.now() - 1.5 * 60 * 60 * 1000),
    type: "login"
  }
];

const getTypeColor = (type: Activity["type"]) => {
  switch (type) {
    case "create": return "bg-stat-green/10 text-stat-green";
    case "update": return "bg-stat-blue/10 text-stat-blue";
    case "delete": return "bg-destructive/10 text-destructive";
    case "login": return "bg-stat-purple/10 text-stat-purple";
    default: return "bg-muted/50 text-muted-foreground";
  }
};

const getUserInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase();
};

const formatTimeAgo = (timestamp: Date) => {
  const now = new Date();
  const diffInMinutes = Math.floor((now.getTime() - timestamp.getTime()) / (1000 * 60));
  
  if (diffInMinutes < 1) return 'just now';
  if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours} hours ago`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  return `${diffInDays} days ago`;
};

export function ActivityFeed() {
  return (
    <Card className="animate-fade-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-stat-purple" />
          IVR Learning Activity Feed
          <Badge variant="secondary" className="animate-pulse-glow bg-stat-green/20 text-stat-green border-stat-green/30">
            Live
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity, index) => (
            <div 
              key={activity.id} 
              className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/30 transition-colors animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <Avatar className="h-8 w-8">
                <AvatarFallback className="text-xs bg-primary/10 text-primary">
                  {getUserInitials(activity.user)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground">
                  <span className="font-medium">{activity.user}</span>
                  {' '}
                  <span className={`px-1.5 py-0.5 text-xs rounded-full ${getTypeColor(activity.type)}`}>
                    {activity.action}
                  </span>
                  {' '}
                  <span className="text-muted-foreground">{activity.target}</span>
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatTimeAgo(activity.timestamp)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
