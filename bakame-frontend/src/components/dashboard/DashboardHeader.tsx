import { Bell, Settings, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { SearchBar } from "./SearchBar";
import { UserProfile } from "@/pages/AdminDashboard";

interface DashboardHeaderProps {
  userProfile: UserProfile;
  onSignOut: () => void;
}

export function DashboardHeader({ userProfile, onSignOut }: DashboardHeaderProps) {
  return (
    <header className="bg-card border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        <SearchBar />
        
        <div className="flex items-center gap-4">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="relative">
                <Bell className="h-4 w-4" />
                <Badge 
                  variant="destructive" 
                  className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs animate-pulse-glow"
                >
                  3
                </Badge>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80 bg-popover border border-border">
              <div className="p-3 border-b border-border">
                <h4 className="font-semibold text-foreground">Notifications</h4>
              </div>
              <div className="p-2">
                <div className="space-y-2">
                  <div className="p-2 hover:bg-muted rounded-lg cursor-pointer transition-colors">
                    <p className="text-sm font-medium text-foreground">New user registered</p>
                    <p className="text-xs text-muted-foreground">5 minutes ago</p>
                  </div>
                  <div className="p-2 hover:bg-muted rounded-lg cursor-pointer transition-colors">
                    <p className="text-sm font-medium text-foreground">System backup completed</p>
                    <p className="text-xs text-muted-foreground">2 hours ago</p>
                  </div>
                  <div className="p-2 hover:bg-muted rounded-lg cursor-pointer transition-colors">
                    <p className="text-sm font-medium text-foreground">IVR session completed</p>
                    <p className="text-xs text-muted-foreground">4 hours ago</p>
                  </div>
                </div>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="flex items-center gap-2">
                <div className="h-6 w-6 bg-primary rounded-full flex items-center justify-center">
                  <span className="text-xs font-semibold text-primary-foreground">
                    {userProfile.full_name ? userProfile.full_name.split(' ').map(n => n[0]).join('').toUpperCase() : 'SA'}
                  </span>
                </div>
                <span className="hidden sm:inline text-sm">{userProfile.full_name || 'Super Admin'}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-popover border border-border">
              <DropdownMenuItem className="cursor-pointer">
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer text-destructive" onClick={onSignOut}>
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
