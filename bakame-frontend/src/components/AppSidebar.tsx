import * as React from "react";
import {
  LayoutDashboard,
  BarChart3,
  GraduationCap,
  MessageSquare,
  Mail,
  Users,
  Building2,
  FileText,
  UserCheck,
  FileSearch,
  HardDrive,
  Bell,
  Shield,
  Database,
  Activity,
  LogOut,
  Crown,
  Server
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
  SidebarHeader,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const menuItems = [
  { title: "Dashboard", icon: LayoutDashboard, path: "/" },
  { title: "Analytics", icon: BarChart3, path: "/analytics" },
  { title: "School Demos", icon: GraduationCap, path: "/school-demos" },
  { title: "Users", icon: Users, path: "/users" },
  { title: "Organizations", icon: Building2, path: "/organizations" },
  { title: "Team", icon: UserCheck, path: "/team" },
  { title: "Content CMS", icon: FileText, path: "/content-cms" },
  { title: "Contact Forms", icon: MessageSquare, path: "/contact-forms" },
  { title: "Newsletter", icon: Mail, path: "/newsletter" },
  { title: "Audit Logs", icon: FileSearch, path: "/audit-logs" },
  { title: "Backup", icon: HardDrive, path: "/backup" },
  { title: "Notifications", icon: Bell, path: "/notifications" },
  { title: "System Health", icon: Activity, path: "/system-health" },
  { title: "Security", icon: Shield, path: "/security" },
  { title: "Database", icon: Database, path: "/database" },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="border-b border-sidebar-border">
        <div className="flex items-center gap-3 px-3 py-4">
          <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
            <Crown className="w-6 h-6 text-primary-foreground" />
          </div>
          {!isCollapsed && (
            <div className="flex-1">
              <h1 className="text-lg font-bold text-sidebar-foreground">Bakame AI</h1>
              <div className="flex items-center gap-2">
                <p className="text-sm text-sidebar-foreground/70">Super Admin</p>
                <Badge variant="destructive" className="text-xs px-1.5 py-0">
                  ADMIN
                </Badge>
              </div>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton>
                    <item.icon className="h-4 w-4" />
                    {!isCollapsed && <span>{item.title}</span>}
                    {item.title === "Security" && !isCollapsed && (
                      <Badge variant="outline" className="ml-auto text-xs">
                        3
                      </Badge>
                    )}
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border">
        <div className="p-3">
          {!isCollapsed && (
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-2">
                <Server className="h-4 w-4 text-stat-green" />
                <span className="text-sm font-medium text-sidebar-foreground">System Status</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-sidebar-foreground/70">
                <div className="w-2 h-2 bg-stat-green rounded-full animate-pulse"></div>
                All systems operational
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-3 mb-3">
            <div className="h-8 w-8 bg-primary/10 rounded-full flex items-center justify-center">
              <span className="text-sm font-semibold text-primary">SA</span>
            </div>
            {!isCollapsed && (
              <div className="flex-1">
                <p className="text-sm font-medium text-sidebar-foreground">Super Admin</p>
                <p className="text-xs text-sidebar-foreground/70">admin@bakame.ai</p>
              </div>
            )}
          </div>
          
          <Button 
            variant="ghost" 
            size="sm" 
            className="w-full justify-start text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50"
          >
            <LogOut className="h-4 w-4" />
            {!isCollapsed && <span className="ml-2">Sign Out</span>}
          </Button>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
