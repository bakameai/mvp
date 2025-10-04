
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authAPI } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
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
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const initializeAuth = async () => {
      try {

        // THEN check for existing session
        const { session } = authAPI.getSession();
        
        if (!session) {
          navigate('/admin');
          return;
        }

        try {
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
        } catch (error) {
          console.error('Profile error:', error);
          toast({
            title: "Error",
            description: "Failed to load user profile. Please try refreshing the page.",
            variant: "destructive",
          });
        }

      } catch (error: any) {
        console.error('Auth initialization error:', error);
        toast({
          title: "Authentication Error",
          description: "Failed to initialize authentication. Please try again.",
          variant: "destructive",
        });
        navigate('/admin');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, [navigate, toast]);

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

      toast({
        title: "Success",
        description: "Successfully signed out",
      });
      
      // Force page reload for clean state
      window.location.href = '/admin';
    } catch (error: any) {
      console.error('Sign out exception:', error);
      // Force navigation even if there's an error
      window.location.href = '/admin';
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
        return <DashboardStats userProfile={userProfile} />;
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
    <DashboardLayout
      userProfile={userProfile}
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      onSignOut={handleSignOut}
      showThemeToggle={showThemeToggle}
    >
      {renderActiveTab()}
    </DashboardLayout>
  );
};

export default AdminDashboard;
