import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Activity } from "lucide-react";

import { useState, useEffect } from "react";
import { adminAPI } from "@/services/api";

interface IVRActivity {
  id: number;
  phone_number: string;
  session_id: string;
  module_name: string;
  interaction_type: string;
  timestamp: string;
  session_duration?: number;
}

const getActivityDescription = (activity: IVRActivity) => {
  const duration = activity.session_duration ? ` (${Math.round(activity.session_duration)}min)` : '';
  const user = `Student ${activity.phone_number.slice(-4)}`;
  
  switch (activity.module_name) {
    case 'english':
      return `${user} completed English conversation session${duration}`;
    case 'math':
      return `${user} practiced Math problems${duration}`;
    case 'comprehension':
      return `${user} worked on Reading comprehension${duration}`;
    case 'debate':
      return `${user} participated in Debate session${duration}`;
    default:
      return `${user} completed ${activity.module_name} session${duration}`;
  }
};

const getTypeColor = (interaction_type: string) => {
  switch (interaction_type) {
    case "voice": return "bg-stat-green/10 text-stat-green";
    case "sms": return "bg-stat-blue/10 text-stat-blue";
    default: return "bg-muted/50 text-muted-foreground";
  }
};

const getUserInitials = (phone: string) => {
  return `S${phone.slice(-2)}`;
};

const formatTimeAgo = (timestamp: string) => {
  const now = new Date();
  const activityTime = new Date(timestamp);
  const diffInMinutes = Math.floor((now.getTime() - activityTime.getTime()) / (1000 * 60));
  
  if (diffInMinutes < 1) return 'just now';
  if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours} hours ago`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  return `${diffInDays} days ago`;
};

export function ActivityFeed() {
  const [activities, setActivities] = useState<IVRActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const sessions = await adminAPI.getUserSessions();
        const recentSessions = sessions.slice(0, 10).map((session, index) => ({
          id: index + 1,
          phone_number: session.phone_number,
          session_id: session.session_id,
          module_name: session.module_name,
          interaction_type: session.interaction_type,
          timestamp: session.timestamp,
          session_duration: session.session_duration,
        }));
        setActivities(recentSessions);
      } catch (error) {
        console.error('Error fetching activities:', error);
        setActivities([]);
      } finally {
        setLoading(false);
      }
    };

    fetchActivities();
    const interval = setInterval(fetchActivities, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="animate-fade-in">
        <CardHeader>
          <CardTitle>Loading Activity Feed...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg animate-pulse">
                <div className="h-8 w-8 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="animate-fade-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl">
          <Activity className="h-6 w-6 text-stat-purple" />
          🎓 Student Learning Activity Feed
          <Badge variant="secondary" className="animate-pulse-glow bg-stat-green/20 text-stat-green border-stat-green/30">
            🔴 Live Updates
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.length === 0 ? (
            <p className="text-muted-foreground text-center py-4">No recent IVR activities</p>
          ) : (
            activities.map((activity, index) => (
              <div 
                key={activity.id} 
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/30 transition-colors animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="text-xs bg-primary/10 text-primary">
                    {getUserInitials(activity.phone_number)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-foreground">
                    {getActivityDescription(activity)}
                    {' '}
                    <span className={`px-1.5 py-0.5 text-xs rounded-full ${getTypeColor(activity.interaction_type)}`}>
                      {activity.interaction_type}
                    </span>
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatTimeAgo(activity.timestamp)}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
