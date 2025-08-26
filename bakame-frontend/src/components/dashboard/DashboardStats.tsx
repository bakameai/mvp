
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Building2, TrendingUp, Activity } from "lucide-react";
import { adminAPI } from "@/services/api";
import { UserProfile } from "@/pages/AdminDashboard";
import { StatCard } from "./StatCard";
import { ActivityFeed } from "./ActivityFeed";
import { QuickActions } from "./QuickActions";
import { WelcomeSection } from "./WelcomeSection";
import { ProfileCard } from "./ProfileCard";

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
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Only admins can see all user stats
        if (userProfile.role === 'admin') {
          const adminStats = await adminAPI.getAdminStats();
          
          setStats({
            totalUsers: adminStats.total_users || 0,
            totalOrganizations: adminStats.total_organizations || 0,
            activeUsers: adminStats.active_users || 0,
            newUsersThisMonth: adminStats.new_users_this_month || 0,
          });
        } else {
          // For non-admin users, show limited stats
          setStats({
            totalUsers: 1, // Just themselves
            totalOrganizations: 1, // Their organization
            activeUsers: 1,
            newUsersThisMonth: 0,
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
      title: "Total Users",
      value: stats.totalUsers,
      icon: Users,
      iconColor: "blue" as const,
    },
    {
      title: "Organizations",
      value: stats.totalOrganizations,
      icon: Building2,
      iconColor: "green" as const,
    },
    {
      title: "Active Users",
      value: stats.activeUsers,
      icon: Activity,
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
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <div key={stat.title} style={{ animationDelay: `${index * 0.1}s` }}>
            <StatCard
              title={stat.title}
              value={stat.value}
              icon={stat.icon}
              iconColor={stat.iconColor}
            />
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <WelcomeSection />
          <ActivityFeed />
        </div>
        <div className="space-y-6">
          <ProfileCard userProfile={userProfile} />
          <QuickActions onActionClick={onActionClick || (() => {})} />
        </div>
      </div>
    </div>
  );
};
