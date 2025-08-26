
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { UserProfile } from "@/pages/AdminDashboard";

interface DashboardLayoutProps {
  children: React.ReactNode;
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
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background">
        <AppSidebar 
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onSignOut={onSignOut}
          userProfile={userProfile}
        />
        <main className="flex-1 flex flex-col overflow-hidden">
          <header className="h-16 flex items-center border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
            <div className="flex items-center gap-4 px-6">
              <SidebarTrigger className="text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground" />
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-stat-green rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-muted-foreground">Super Admin Dashboard</span>
              </div>
            </div>
          </header>
          <div className="flex-1 overflow-auto">
            <div className="p-8">
              {children}
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
};
