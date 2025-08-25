
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Building2, TrendingUp, Activity } from "lucide-react";
import { adminAPI } from "@/services/api";
import { UserProfile } from "@/pages/AdminDashboard";
import { StatCard } from "./StatCard";
import { ActivityFeed } from "./ActivityFeed";
import { QuickActions } from "./QuickActions";

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
          <Card>
            <CardHeader>
              <CardTitle>Welcome to Bakame AI Dashboard</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                Manage your AI-powered applications and user base from this central dashboard.
              </p>
              <ul className="mt-4 space-y-2 text-sm">
                <li className="flex items-center gap-2 text-muted-foreground">
                  <div className="w-2 h-2 bg-stat-blue rounded-full"></div>
                  Monitor user activity and engagement
                </li>
                <li className="flex items-center gap-2 text-muted-foreground">
                  <div className="w-2 h-2 bg-stat-green rounded-full"></div>
                  Manage organizations and partnerships
                </li>
                <li className="flex items-center gap-2 text-muted-foreground">
                  <div className="w-2 h-2 bg-stat-purple rounded-full"></div>
                  Configure system settings and preferences
                </li>
              </ul>
            </CardContent>
          </Card>
          <ActivityFeed />
        </div>
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Your Profile</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-muted-foreground">Name</label>
                  <p className="font-medium">{userProfile.full_name || 'Not set'}</p>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Email</label>
                  <p className="font-medium">{userProfile.email}</p>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Role</label>
                  <p className="font-medium capitalize">{userProfile.role}</p>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Organization</label>
                  <p className="font-medium">{userProfile.organization || 'Not set'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <QuickActions onActionClick={onActionClick || (() => {})} />
        </div>
      </div>
    </div>
  );
};
