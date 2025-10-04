
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useQuery } from '@tanstack/react-query';
import { authAPI } from '@/services/api';
import { BookOpen, MessageSquare, Clock, Users, TrendingUp, Activity } from 'lucide-react';

interface AnalyticsData {
  totalSessions: number;
  activeUsers: number;
  averageSessionDuration: number;
  totalMessages: number;
  topLearningTopics: { topic: string; count: number }[];
  sessionsByMode: { mode: string; count: number }[];
}

const IVRAnalyticsDashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');

  const { data: analytics, isLoading } = useQuery({
    queryKey: ['ivr-analytics', timeRange],
    queryFn: async () => {
      const { data: sessions, error } = await supabase
        .from('ivr_sessions')
        .select('*')
        .gte('created_at', new Date(Date.now() - getTimeRangeMs(timeRange)).toISOString());

      if (error) throw error;

      // Calculate analytics from session data
      const analyticsData: AnalyticsData = {
        totalSessions: sessions.length,
        activeUsers: new Set(sessions.map(s => s.user_id).filter(Boolean)).size,
        averageSessionDuration: sessions.reduce((acc, s) => acc + (s.duration_seconds || 0), 0) / sessions.length || 0,
        totalMessages: sessions.reduce((acc, s) => {
          const history = s.conversation_history;
          if (Array.isArray(history)) {
            return acc + history.length;
          }
          return acc;
        }, 0),
        topLearningTopics: extractTopics(sessions),
        sessionsByMode: groupSessionsByMode(sessions)
      };

      return analyticsData;
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  const getTimeRangeMs = (range: string) => {
    switch (range) {
      case '24h': return 24 * 60 * 60 * 1000;
      case '7d': return 7 * 24 * 60 * 60 * 1000;
      case '30d': return 30 * 24 * 60 * 60 * 1000;
      default: return 24 * 60 * 60 * 1000;
    }
  };

  const extractTopics = (sessions: any[]) => {
    const topics: { [key: string]: number } = {};
    sessions.forEach(session => {
      const history = session.conversation_history;
      if (Array.isArray(history)) {
        history.forEach((msg: any) => {
          if (msg && typeof msg === 'object' && msg.type) {
            topics[msg.type] = (topics[msg.type] || 0) + 1;
          }
        });
      }
    });
    return Object.entries(topics)
      .map(([topic, count]) => ({ topic, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  };

  const groupSessionsByMode = (sessions: any[]) => {
    const modes: { [key: string]: number } = {};
    sessions.forEach(session => {
      const mode = session.session_id?.includes('webrtc') ? 'WebRTC' : 
                   session.session_id?.includes('ws') ? 'WebSocket' : 'HTTP';
      modes[mode] = (modes[mode] || 0) + 1;
    });
    return Object.entries(modes).map(([mode, count]) => ({ mode, count }));
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ${Math.floor(seconds % 60)}s`;
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="bg-[#081a2e]/80 backdrop-blur-md border-white/20 animate-pulse">
              <CardContent className="p-4">
                <div className="h-16 bg-white/10 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-[#ff914d] to-[#0d4dcc] bg-clip-text text-transparent">
          IVR Analytics Dashboard
        </h2>
        <div className="flex gap-2">
          {['24h', '7d', '30d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range as any)}
              className={`px-3 py-1 rounded-lg text-sm transition-all ${
                timeRange === range
                  ? 'bg-foreground text-background'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card className="bg-[#081a2e]/80 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white/70">Total Sessions</p>
                <p className="text-2xl font-bold text-white">{analytics?.totalSessions || 0}</p>
              </div>
              <Activity className="w-8 h-8 text-[#ff914d]" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#081a2e]/80 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white/70">Active Users</p>
                <p className="text-2xl font-bold text-white">{analytics?.activeUsers || 0}</p>
              </div>
              <Users className="w-8 h-8 text-[#0d4dcc]" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#081a2e]/80 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white/70">Avg. Duration</p>
                <p className="text-2xl font-bold text-white">
                  {formatDuration(analytics?.averageSessionDuration || 0)}
                </p>
              </div>
              <Clock className="w-8 h-8 text-[#ff914d]" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#081a2e]/80 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white/70">Total Messages</p>
                <p className="text-2xl font-bold text-white">{analytics?.totalMessages || 0}</p>
              </div>
              <MessageSquare className="w-8 h-8 text-[#0d4dcc]" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-[#081a2e]/80 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-[#ff914d]" />
              Top Learning Topics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analytics?.topLearningTopics.map((topic, index) => (
                <div key={topic.topic} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-gradient-to-r from-[#ff914d] to-[#0d4dcc] rounded-full"></div>
                    <span className="text-white/80 capitalize">{topic.topic}</span>
                  </div>
                  <Badge variant="outline" className="border-white/30 text-white">
                    {topic.count}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#081a2e]/80 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-[#0d4dcc]" />
              Sessions by Mode
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analytics?.sessionsByMode.map((mode, index) => (
                <div key={mode.mode} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-gradient-to-r from-[#0d4dcc] to-[#ff914d] rounded-full"></div>
                    <span className="text-white/80">{mode.mode}</span>
                  </div>
                  <Badge variant="outline" className="border-white/30 text-white">
                    {mode.count}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default IVRAnalyticsDashboard;
