
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authAPI } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { StatCard } from "@/components/dashboard/StatCard";
import { WelcomeSection } from "@/components/dashboard/WelcomeSection";
import { ProfileCard } from "@/components/dashboard/ProfileCard";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { DataChart } from "@/components/dashboard/DataChart";
import { Users, Building2, Activity, TrendingUp } from "lucide-react";
import { UserManagement } from "@/components/dashboard/UserManagement";
import { OrganizationManagement } from "@/components/dashboard/OrganizationManagement";
import { Settings } from "@/components/dashboard/Settings";
import { Team } from "@/components/dashboard/Team";
import { GovernmentDemoManagement } from "@/components/dashboard/GovernmentDemoManagement";
import { ContactSubmissionsManagement } from "@/components/dashboard/ContactSubmissionsManagement";
import { NewsletterManagement } from "@/components/dashboard/NewsletterManagement";
import { AnalyticsDashboard } from "@/components/dashboard/AnalyticsDashboard";
import { EnterpriseAdminDashboard } from "@/components/dashboard/EnterpriseAdminDashboard";
import { GovernmentAdminDashboard } from "@/components/dashboard/GovernmentAdminDashboard";
import { SchoolAdminDashboard } from "@/components/dashboard/SchoolAdminDashboard";
import { PrivateUserDashboard } from "@/components/dashboard/PrivateUserDashboard";
import { ContentManagement } from "@/components/dashboard/ContentManagement";
import { AuditLogs } from "@/components/dashboard/AuditLogs";
import { BackupManagement } from "@/components/dashboard/BackupManagement";
import { NotificationCenter } from "@/components/dashboard/NotificationCenter";
import { FileManagement } from "@/components/dashboard/FileManagement";
import { APIManagement } from "@/components/dashboard/APIManagement";
import { PerformanceMonitoring } from "@/components/dashboard/PerformanceMonitoring";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export type UserProfile = {
  id: string;
  email: string;
  full_name: string | null;
  organization: string | null;
  role: 'admin' | 'creator' | 'manager' | 'school' | 'government' | 'ngo';
  created_at: string;
  updated_at: string;
};

// Auth state cleanup utility for security
const cleanupAuthState = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

const AdminDashboard = () => {
  const [user, setUser] = useState<any>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [showThemeToggle, setShowThemeToggle] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check for existing session
        const { session, user } = authAPI.getSession();
        
        if (!session || !user) {
          setIsAuthenticated(false);
          setIsLoading(false);
          return;
        }

        try {
          const backendUser = await authAPI.getCurrentUser();
          setUser(backendUser);
          setUserProfile({
            id: backendUser.id.toString(),
            email: backendUser.email,
            full_name: backendUser.full_name,
            organization: backendUser.organization,
            role: backendUser.role as any,
            created_at: backendUser.created_at,
            updated_at: backendUser.created_at
          });
          setIsAuthenticated(true);
        } catch (error: any) {
          console.error('Backend verification failed:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          setIsAuthenticated(false);
        }

      } catch (error: any) {
        console.error('Auth initialization error:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, [navigate, toast]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoggingIn(true);

    try {
      const response = await authAPI.login({ email: loginForm.email, password: loginForm.password });
      
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        
        const user = await authAPI.getCurrentUser();
        setUser(user);
        setUserProfile({
          id: user.id.toString(),
          email: user.email,
          full_name: user.full_name,
          organization: user.organization,
          role: user.role as any,
          created_at: user.created_at,
          updated_at: user.created_at
        });
        setIsAuthenticated(true);
        
        toast({
          title: "Success",
          description: "Successfully logged in",
        });
      }
    } catch (error: any) {
      console.error('Login error:', error);
      let errorMessage = "Invalid credentials";
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map((err: any) => err.msg || err).join(', ');
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast({
        title: "Login Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleSignOut = async () => {
    try {
      // Clean up auth state first
      cleanupAuthState();
      
      // Attempt global sign out
      try {
        await authAPI.logout();
      } catch (error) {
        console.error('Sign out error:', error);
        // Continue with cleanup even if signOut fails
      }

      setIsAuthenticated(false);
      setUser(null);
      setUserProfile(null);
      
      toast({
        title: "Success",
        description: "Successfully signed out",
      });
    } catch (error: any) {
      console.error('Sign out exception:', error);
      setIsAuthenticated(false);
      setUser(null);
      setUserProfile(null);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Admin Login</CardTitle>
            <CardDescription>
              Sign in to access the BAKAME admin dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={loginForm.email}
                  onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                  placeholder="admin@bakame.org"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  placeholder="Enter your password"
                  required
                />
              </div>
              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoggingIn}
              >
                {isLoggingIn ? "Signing in..." : "Sign In"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!user || !userProfile) {
    return null;
  }

  // Role-specific dashboard routing
  const getRoleSpecificDashboard = () => {
    switch (userProfile.role) {
      case 'government':
        return <GovernmentAdminDashboard />;
      case 'school':
        return <SchoolAdminDashboard />;
      case 'ngo':
        return <EnterpriseAdminDashboard />;
      case 'manager':
        return <EnterpriseAdminDashboard />;
      case 'creator':
        return <PrivateUserDashboard />;
      default:
        return renderActiveTab(); // Admin users get full admin dashboard
    }
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardStats userProfile={userProfile} onActionClick={setActiveTab} />;
      case "users":
        return <UserManagement userProfile={userProfile} />;
      case "organizations":
        return <OrganizationManagement userProfile={userProfile} />;
      case "team":
        return <Team userProfile={userProfile} />;
      case "government-demos":
        return <GovernmentDemoManagement userProfile={userProfile} />;
      case "contact-submissions":
        return <ContactSubmissionsManagement userProfile={userProfile} />;
      case "newsletter":
        return <NewsletterManagement userProfile={userProfile} />;
      case "analytics":
        return <AnalyticsDashboard userProfile={userProfile} />;
      case "content":
        return <ContentManagement userProfile={userProfile} />;
      case "audit":
        return <AuditLogs userProfile={userProfile} />;
      case "backup":
        return <BackupManagement userProfile={userProfile} />;
      case "notifications":
        return <NotificationCenter userProfile={userProfile} />;
      case "files":
        return <FileManagement userProfile={userProfile} />;
      case "api":
        return <APIManagement userProfile={userProfile} />;
      case "performance":
        return <PerformanceMonitoring userProfile={userProfile} />;
      case "settings":
        return (
          <Settings 
            userProfile={userProfile} 
            showThemeToggle={showThemeToggle}
            onThemeToggleChange={setShowThemeToggle}
          />
        );
      default:
        return <DashboardStats userProfile={userProfile} />;
    }
  };

  // For non-admin users, show role-specific dashboard without navigation
  if (userProfile.role !== 'admin') {
    return (
      <div className="min-h-screen bg-background">
        <div className="p-8">
          {getRoleSpecificDashboard()}
        </div>
      </div>
    );
  }

  // Admin users get the full dashboard with navigation
  return (
    <div className="min-h-screen bg-background">
      <DashboardLayout>
        {activeTab === "dashboard" ? (
          <>
            <div className="p-8 space-y-8">
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  { title: "Active Students", value: "1,247", icon: Users, iconColor: "blue" as const },
                  { title: "Partner Schools", value: "23", icon: Building2, iconColor: "green" as const },
                  { title: "Lessons Today", value: "89", icon: Activity, iconColor: "purple" as const },
                  { title: "Speaking Hours", value: "156", icon: TrendingUp, iconColor: "orange" as const },
                ].map((stat, index) => (
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

              {/* Charts Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <DataChart title="Student Progress" type="bar" />
                <DataChart title="Speaking Confidence Trends" type="line" />
              </div>

              {/* Main Content Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                  <WelcomeSection />
                  <ActivityFeed />
                </div>
                <div className="space-y-6">
                  <ProfileCard userProfile={userProfile} />
                  <QuickActions onActionClick={setActiveTab} />
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="p-8 space-y-8">
            {renderActiveTab()}
          </div>
        )}
      </DashboardLayout>
    </div>
  );
};

export default AdminDashboard;
