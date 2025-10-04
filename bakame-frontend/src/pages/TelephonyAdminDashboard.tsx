import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { telephonyAPI } from "@/services/api";
import { Phone, MessageSquare, Users, TrendingUp, Clock, MapPin } from "lucide-react";

interface TelephonyStats {
  total_sessions: number;
  active_users: number;
  total_voice_calls: number;
  total_sms: number;
  average_session_duration: number;
  popular_modules: Array<{ name: string; count: number }>;
  regional_usage: Array<{ region: string; users: number }>;
}

interface SessionData {
  id: number;
  phone_number: string;
  module_name: string;
  interaction_type: string;
  timestamp: string;
  session_duration: number;
  user_input: string;
  ai_response: string;
}

const TelephonyAdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<TelephonyStats | null>(null);
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, sessionsData] = await Promise.all([
          telephonyAPI.getStats(),
          telephonyAPI.getSessionHistory()
        ]);
        setStats(statsData);
        setSessions(sessionsData);
      } catch (error) {
        console.error('Error fetching telephony data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading telephony dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Telephony Admin Dashboard</h1>
          <p className="text-muted-foreground">Monitor AI learning sessions and user engagement</p>
        </div>
        <Button onClick={() => window.location.reload()}>
          Refresh Data
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <Phone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_sessions || 0}</div>
            <p className="text-xs text-muted-foreground">All learning interactions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_users || 0}</div>
            <p className="text-xs text-muted-foreground">Unique phone numbers</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Voice Calls</CardTitle>
            <Phone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_voice_calls || 0}</div>
            <p className="text-xs text-muted-foreground">Voice interactions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">SMS Messages</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_sms || 0}</div>
            <p className="text-xs text-muted-foreground">Text interactions</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="sessions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="sessions">Recent Sessions</TabsTrigger>
          <TabsTrigger value="modules">Popular Modules</TabsTrigger>
          <TabsTrigger value="regions">Regional Usage</TabsTrigger>
        </TabsList>

        <TabsContent value="sessions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Learning Sessions</CardTitle>
              <CardDescription>Latest AI tutoring interactions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {sessions.slice(0, 10).map((session) => (
                  <div key={session.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant={session.interaction_type === 'voice' ? 'default' : 'secondary'}>
                          {session.interaction_type}
                        </Badge>
                        <span className="font-medium">{session.module_name}</span>
                        <span className="text-sm text-muted-foreground">{session.phone_number}</span>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {session.user_input}
                      </p>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="flex items-center gap-1 text-sm text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {Math.round(session.session_duration || 0)}s
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(session.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="modules" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Popular Learning Modules</CardTitle>
              <CardDescription>Most used educational content</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stats?.popular_modules?.map((module, index) => (
                  <div key={module.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium">
                        {index + 1}
                      </div>
                      <span className="font-medium">{module.name}</span>
                    </div>
                    <Badge variant="outline">{module.count} sessions</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="regions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Regional Usage</CardTitle>
              <CardDescription>User distribution across Rwanda</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stats?.regional_usage?.map((region) => (
                  <div key={region.region} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{region.region}</span>
                    </div>
                    <Badge variant="outline">{region.users} users</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TelephonyAdminDashboard;
