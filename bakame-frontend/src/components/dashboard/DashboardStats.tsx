
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Building2, TrendingUp, Activity, Phone, BookOpen, Clock, Target, Mic, MessageSquare, GraduationCap, BarChart3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { adminAPI } from "@/services/api";
import { UserProfile } from "@/pages/AdminDashboard";
import { StatCard } from "./StatCard";
import { ActivityFeed } from "./ActivityFeed";
import { QuickActions } from "./QuickActions";
import { WelcomeSection } from "./WelcomeSection";
import { ProfileCard } from "./ProfileCard";
import { DataChart } from "./DataChart";

interface DashboardStatsProps {
  userProfile: UserProfile;
  onActionClick?: (action: string) => void;
}

export const DashboardStats = ({ userProfile, onActionClick }: DashboardStatsProps) => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalOrganizations: 0,
    activeUsers: 0,
    newUsersThisMonth: 0,
    totalIVRSessions: 0,
    voiceSessions: 0,
    smsSessions: 0,
    recentSessions24h: 0,
    averageSessionDuration: 0,
    peerLearningSessions: 0,
    activePeerSessions: 0,
    moduleStats: {} as Record<string, number>,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        if (userProfile.role === 'admin') {
          const [adminStats, ivrStats] = await Promise.all([
            adminAPI.getAdminStats(),
            adminAPI.getIVRStats()
          ]);
          
          setStats({
            totalUsers: adminStats.total_users || 0,
            totalOrganizations: adminStats.organizations || 0,
            activeUsers: adminStats.active_users || 0,
            newUsersThisMonth: adminStats.new_users_this_month || 0,
            totalIVRSessions: ivrStats.total_ivr_sessions || 0,
            voiceSessions: ivrStats.voice_sessions || 0,
            smsSessions: ivrStats.sms_sessions || 0,
            recentSessions24h: ivrStats.recent_sessions_24h || 0,
            averageSessionDuration: ivrStats.average_session_duration || 0,
            peerLearningSessions: ivrStats.peer_learning_sessions || 0,
            activePeerSessions: ivrStats.active_peer_sessions || 0,
            moduleStats: ivrStats.module_statistics || {},
          });
        } else {
          setStats({
            totalUsers: 1,
            totalOrganizations: 1,
            activeUsers: 1,
            newUsersThisMonth: 0,
            totalIVRSessions: 0,
            voiceSessions: 0,
            smsSessions: 0,
            recentSessions24h: 0,
            averageSessionDuration: 0,
            peerLearningSessions: 0,
            activePeerSessions: 0,
            moduleStats: {},
          });
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [userProfile]);

  const statCards = [
    {
      title: "Total IVR Sessions",
      value: stats.totalIVRSessions,
      icon: Phone,
      iconColor: "blue" as const,
    },
    {
      title: "Voice Interactions",
      value: stats.voiceSessions,
      icon: Mic,
      iconColor: "green" as const,
    },
    {
      title: "SMS Interactions", 
      value: stats.smsSessions,
      icon: MessageSquare,
      iconColor: "purple" as const,
    },
    {
      title: "Avg Duration (min)",
      value: stats.averageSessionDuration,
      icon: Clock,
      iconColor: "orange" as const,
    },
    {
      title: "Recent Sessions (24h)",
      value: stats.recentSessions24h,
      icon: TrendingUp,
      iconColor: "blue" as const,
    },
    {
      title: "Peer Learning Sessions",
      value: stats.peerLearningSessions,
      icon: Users,
      iconColor: "green" as const,
    },
    {
      title: "Active Peer Sessions",
      value: stats.activePeerSessions,
      icon: Activity,
      iconColor: "purple" as const,
    },
    {
      title: "Total Students",
      value: stats.totalUsers,
      icon: GraduationCap,
      iconColor: "orange" as const,
    },
  ];

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-8 bg-gray-200 rounded mb-2"></div>
              <div className="h-6 bg-gray-200 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <>
      {/* IVR Learning System Dashboard */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
          <Phone className="h-8 w-8 text-stat-blue" />
          IVR Learning System Dashboard
          <Badge variant="secondary" className="animate-pulse-glow bg-stat-green/20 text-stat-green border-stat-green/30">
            Live Data
          </Badge>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.slice(0, 4).map((stat, index) => (
            <div key={index} style={{ animationDelay: `${index * 0.1}s` }}>
              <StatCard
                title={stat.title}
                value={stat.value}
                icon={stat.icon}
                iconColor={stat.iconColor}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Session Analytics & Peer Learning */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-stat-purple" />
          Session Analytics & Peer Learning
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.slice(4).map((stat, index) => (
            <div key={index + 4} style={{ animationDelay: `${(index + 4) * 0.1}s` }}>
              <StatCard
                title={stat.title}
                value={stat.value}
                icon={stat.icon}
                iconColor={stat.iconColor}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <DataChart />
        <DataChart />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <WelcomeSection />
          <ActivityFeed />
        </div>
        <div className="space-y-6">
          <ProfileCard userProfile={userProfile} />
          <QuickActions onActionClick={onActionClick || (() => {})} />
        </div>
      </div>
    </>
  );
};
