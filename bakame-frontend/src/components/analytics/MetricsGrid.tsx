import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Users, 
  Activity, 
  Phone, 
  MessageSquare,
  Clock,
  TrendingUp,
  Target,
  BarChart3
} from "lucide-react";
import { adminAPI } from "@/services/api";

export function MetricsGrid() {
  const [metrics, setMetrics] = useState({
    totalSessions: 0,
    activeSessions: 0,
    avgDuration: 0,
    completionRate: 0,
    voiceCalls: 0,
    smsMessages: 0,
    uniqueUsers: 0,
    successRate: 0
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const [ivrStats, userSessions] = await Promise.all([
          adminAPI.getIVRStats(),
          adminAPI.getUserSessions()
        ]);

        const totalSessions = userSessions.length;
        const voiceSessions = userSessions.filter(s => s.interaction_type === 'voice').length;
        const smsSessions = userSessions.filter(s => s.interaction_type === 'sms').length;
        const completedSessions = userSessions.filter(s => s.session_duration && s.session_duration > 0).length;
        const avgDuration = userSessions.reduce((acc, s) => acc + (s.session_duration || 0), 0) / totalSessions || 0;
        const uniqueUsers = new Set(userSessions.map(s => s.phone_number)).size;

        setMetrics({
          totalSessions,
          activeSessions: ivrStats.active_sessions || 0,
          avgDuration: Math.round(avgDuration * 100) / 100,
          completionRate: totalSessions > 0 ? Math.round((completedSessions / totalSessions) * 100) : 0,
          voiceCalls: voiceSessions,
          smsMessages: smsSessions,
          uniqueUsers,
          successRate: totalSessions > 0 ? Math.round((completedSessions / totalSessions) * 100) : 0
        });
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const metricCards = [
    {
      title: "Total IVR Sessions",
      value: metrics.totalSessions.toLocaleString(),
      icon: Activity,
      color: "text-stat-blue",
      bgColor: "bg-stat-blue/10",
      change: "+12%",
      changeType: "positive"
    },
    {
      title: "Active Sessions",
      value: metrics.activeSessions.toString(),
      icon: Users,
      color: "text-stat-green",
      bgColor: "bg-stat-green/10",
      change: "+5%",
      changeType: "positive"
    },
    {
      title: "Avg Session Duration",
      value: `${metrics.avgDuration}min`,
      icon: Clock,
      color: "text-stat-purple",
      bgColor: "bg-stat-purple/10",
      change: "+8%",
      changeType: "positive"
    },
    {
      title: "Completion Rate",
      value: `${metrics.completionRate}%`,
      icon: Target,
      color: "text-stat-orange",
      bgColor: "bg-stat-orange/10",
      change: "-2%",
      changeType: "negative"
    },
    {
      title: "Voice Calls",
      value: metrics.voiceCalls.toLocaleString(),
      icon: Phone,
      color: "text-stat-blue",
      bgColor: "bg-stat-blue/10",
      change: "+15%",
      changeType: "positive"
    },
    {
      title: "SMS Messages",
      value: metrics.smsMessages.toLocaleString(),
      icon: MessageSquare,
      color: "text-stat-green",
      bgColor: "bg-stat-green/10",
      change: "+7%",
      changeType: "positive"
    },
    {
      title: "Unique Students",
      value: metrics.uniqueUsers.toLocaleString(),
      icon: Users,
      color: "text-stat-purple",
      bgColor: "bg-stat-purple/10",
      change: "+18%",
      changeType: "positive"
    },
    {
      title: "Success Rate",
      value: `${metrics.successRate}%`,
      icon: TrendingUp,
      color: "text-stat-orange",
      bgColor: "bg-stat-orange/10",
      change: "+3%",
      changeType: "positive"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metricCards.map((metric, index) => (
        <Card key={index} className="hover:shadow-lg transition-all duration-300 animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">{metric.title}</p>
                <p className="text-3xl font-bold text-foreground">{metric.value}</p>
                <div className="flex items-center mt-2">
                  <Badge 
                    variant="secondary" 
                    className={`text-xs ${metric.changeType === 'positive' ? 'text-stat-green' : 'text-stat-orange'}`}
                  >
                    {metric.change} vs last period
                  </Badge>
                </div>
              </div>
              <div className={`p-3 rounded-lg ${metric.bgColor} ${metric.color}`}>
                <metric.icon className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
