import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, TrendingUp } from "lucide-react";

export function DataChart() {
  return (
    <Card className="animate-fade-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-stat-blue" />
          IVR Usage Analytics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-stat-blue/5 rounded-lg border border-stat-blue/20">
            <div>
              <p className="text-sm font-medium text-foreground">Daily Sessions</p>
              <p className="text-2xl font-bold text-stat-blue">247</p>
            </div>
            <TrendingUp className="h-8 w-8 text-stat-blue" />
          </div>
          
          <div className="flex items-center justify-between p-4 bg-stat-green/5 rounded-lg border border-stat-green/20">
            <div>
              <p className="text-sm font-medium text-foreground">Success Rate</p>
              <p className="text-2xl font-bold text-stat-green">94.2%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-stat-green" />
          </div>
          
          <div className="flex items-center justify-between p-4 bg-stat-purple/5 rounded-lg border border-stat-purple/20">
            <div>
              <p className="text-sm font-medium text-foreground">Avg Duration</p>
              <p className="text-2xl font-bold text-stat-purple">4.7m</p>
            </div>
            <TrendingUp className="h-8 w-8 text-stat-purple" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
