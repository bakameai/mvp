
import { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { 
  BarChart3, 
  Users, 
  Building2, 
  Settings, 
  UsersIcon,
  FileText,
  Mail,
  MessageSquare,
  TrendingUp,
  LogOut
} from "lucide-react";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { UserProfile } from "@/pages/AdminDashboard";

interface DashboardLayoutProps {
  children: ReactNode;
  userProfile: UserProfile;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onSignOut: () => void;
  showThemeToggle?: boolean;
}

export const DashboardLayout = ({ 
  children, 
  userProfile, 
  activeTab, 
  setActiveTab, 
  onSignOut,
  showThemeToggle = false
}: DashboardLayoutProps) => {
  const navigationItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "analytics", label: "Analytics", icon: TrendingUp },
    { id: "government-demos", label: "Gov Demos", icon: FileText },
    { id: "contact-submissions", label: "Contact Forms", icon: MessageSquare },
    { id: "newsletter", label: "Newsletter", icon: Mail },
    { id: "users", label: "Users", icon: Users },
    { id: "organizations", label: "Organizations", icon: Building2 },
    { id: "team", label: "Team", icon: UsersIcon },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <div className="w-64 bg-card shadow-sm border-r border-border">
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-foreground">Bakame AI</h1>
              <p className="text-sm text-muted-foreground mt-1">Admin Dashboard</p>
            </div>
            {showThemeToggle && <ThemeToggle />}
          </div>
        </div>
        
        <nav className="p-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-2 rounded-lg text-left transition-colors duration-200 ${
                  activeTab === item.id
                    ? "bg-primary/10 text-primary border border-primary/20"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            );
          })}
        </nav>
        
        <div className="absolute bottom-0 w-64 p-4 border-t border-border bg-card">
          <div className="mb-4">
            <p className="text-sm font-medium text-foreground">
              {userProfile.full_name || userProfile.email}
            </p>
            <p className="text-xs text-muted-foreground capitalize">{userProfile.role}</p>
          </div>
          <Button
            onClick={onSignOut}
            variant="outline"
            size="sm"
            className="w-full flex items-center space-x-2"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {children}
        </div>
      </div>
    </div>
  );
};
