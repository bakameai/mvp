import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  iconColor: "blue" | "green" | "purple" | "orange";
}

export function StatCard({ title, value, icon: Icon, iconColor }: StatCardProps) {
  const colorClasses = {
    blue: "text-stat-blue bg-stat-blue/10",
    green: "text-stat-green bg-stat-green/10", 
    purple: "text-stat-purple bg-stat-purple/10",
    orange: "text-stat-orange bg-stat-orange/10"
  };

  return (
    <Card className="p-6 hover:shadow-lg transition-all duration-300 hover:scale-105 animate-fade-in">
      <CardContent className="p-0">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-1">{title}</p>
            <p className="text-3xl font-bold text-foreground animate-scale-in">{value}</p>
          </div>
          <div className={`p-3 rounded-lg transition-all duration-300 hover:scale-110 ${colorClasses[iconColor]}`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
