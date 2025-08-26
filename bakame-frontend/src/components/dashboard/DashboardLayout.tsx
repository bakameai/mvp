
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { DashboardHeader } from "./DashboardHeader";
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
          <DashboardHeader 
            userProfile={userProfile}
            onSignOut={onSignOut}
          />
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
