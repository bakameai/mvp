
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Building2, TrendingUp, Activity, Phone, BookOpen, Clock, Target } from "lucide-react";
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
    activeIVRSessions: 0,
    completedLessons: 0,
    averageSessionDuration: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Only admins can see all user stats
        if (userProfile.role === 'admin') {
          const adminStats = await adminAPI.getAdminStats();
          
          const ivrResponse = await fetch('/api/admin/peer-learning-sessions', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
          });
          const ivrData = await ivrResponse.json();
          const sessions = ivrData.data?.sessions || [];
          
          setStats({
            totalUsers: adminStats.total_users || 0,
            totalOrganizations: adminStats.total_organizations || 0,
            activeUsers: adminStats.active_users || 0,
            newUsersThisMonth: adminStats.new_users_this_month || 0,
            totalIVRSessions: sessions.length || 0,
            activeIVRSessions: sessions.filter((s: any) => s.status === 'active').length || 0,
            completedLessons: sessions.filter((s: any) => s.status === 'completed').length || 0,
            averageSessionDuration: sessions.length > 0 ? Math.round(sessions.reduce((acc: number, s: any) => acc + (s.duration || 15), 0) / sessions.length) : 0,
          });
        } else {
          // For non-admin users, show limited stats
          setStats({
            totalUsers: 1, // Just themselves
            totalOrganizations: 1, // Their organization
            activeUsers: 1,
            newUsersThisMonth: 0,
            totalIVRSessions: 0,
            activeIVRSessions: 0,
            completedLessons: 0,
            averageSessionDuration: 0,
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
      title: "Active Sessions",
      value: stats.activeIVRSessions,
      icon: Activity,
      iconColor: "green" as const,
    },
    {
      title: "Completed Lessons",
      value: stats.completedLessons,
      icon: BookOpen,
      iconColor: "purple" as const,
    },
    {
      title: "Avg Session (min)",
      value: stats.averageSessionDuration,
      icon: Clock,
      iconColor: "orange" as const,
    },
    {
      title: "Total Students",
      value: stats.totalUsers,
      icon: Users,
      iconColor: "blue" as const,
    },
    {
      title: "Partner Schools",
      value: stats.totalOrganizations,
      icon: Building2,
      iconColor: "green" as const,
    },
    {
      title: "Active Learners",
      value: stats.activeUsers,
      icon: Target,
      iconColor: "purple" as const,
    },
    {
      title: "New This Month",
      value: stats.newUsersThisMonth,
      icon: TrendingUp,
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
      {/* IVR Stats Grid */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
          <Phone className="h-8 w-8 text-stat-blue" />
          IVR Learning System Dashboard
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

      {/* User Management Stats */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <Users className="h-6 w-6 text-stat-green" />
          User Management Overview
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
