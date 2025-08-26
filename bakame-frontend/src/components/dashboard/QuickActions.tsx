import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Users, Mail, FileText, Download, Settings, Phone, BarChart3 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface QuickActionsProps {
  onActionClick: (action: string) => void;
}

const quickActions = [
  { 
    icon: Plus, 
    label: "Add User", 
    action: "users",
    color: "text-stat-blue bg-stat-blue/10 hover:bg-stat-blue/20"
  },
  { 
    icon: Phone, 
    label: "IVR Test", 
    action: "ivr",
    color: "text-stat-green bg-stat-green/10 hover:bg-stat-green/20"
  },
  { 
    icon: BarChart3, 
    label: "Analytics", 
    action: "analytics",
    color: "text-stat-purple bg-stat-purple/10 hover:bg-stat-purple/20"
  },
  { 
    icon: Download, 
    label: "Backup", 
    action: "backup",
    color: "text-stat-orange bg-stat-orange/10 hover:bg-stat-orange/20"
  },
  { 
    icon: FileText, 
    label: "Content", 
    action: "content",
    color: "text-primary bg-primary/10 hover:bg-primary/20"
  },
  { 
    icon: Settings, 
    label: "Settings", 
    action: "settings",
    color: "text-muted-foreground bg-muted/50 hover:bg-muted"
  }
];

export function QuickActions({ onActionClick }: QuickActionsProps) {
  const { toast } = useToast();

  const handleAction = (action: typeof quickActions[0]) => {
    if (action.action === "ivr") {
      window.open("/ivr", "_blank");
      toast({
        title: "IVR Interface",
        description: "Opening IVR test interface in new tab",
      });
    } else {
      onActionClick(action.action);
      toast({
        title: "Navigation",
        description: `Switched to ${action.label}`,
      });
    }
  };

  return (
    <Card className="animate-fade-in">
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {quickActions.map((action, index) => (
            <Button
              key={action.label}
              variant="outline"
              className={`h-16 flex-col gap-2 hover:scale-105 transition-all duration-200 animate-scale-in ${action.color}`}
              style={{ animationDelay: `${index * 0.1}s` }}
              onClick={() => handleAction(action)}
            >
              <action.icon className="h-5 w-5" />
              <span className="text-xs font-medium">{action.label}</span>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
