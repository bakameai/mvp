import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { 
  Settings, 
  Database, 
  Shield, 
  Zap,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export function AdminControls() {
  const { toast } = useToast();
  const [systemSettings, setSystemSettings] = useState({
    realTimeUpdates: true,
    dataRetention: "90",
    autoBackup: true,
    alertThreshold: "95"
  });

  const [maintenanceMode, setMaintenanceMode] = useState(false);

  const handleSystemAction = (action: string) => {
    toast({
      title: `${action} Initiated`,
      description: `System ${action.toLowerCase()} has been started.`
    });
  };

  const handleSettingChange = (key: string, value: any) => {
    setSystemSettings(prev => ({ ...prev, [key]: value }));
    toast({
      title: "Setting Updated",
      description: `${key} has been updated successfully.`
    });
  };

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="animate-fade-in">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-stat-green/10 rounded-lg">
                <CheckCircle className="h-5 w-5 text-stat-green" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">System Status</p>
                <p className="font-semibold text-stat-green">Operational</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-stat-blue/10 rounded-lg">
                <Database className="h-5 w-5 text-stat-blue" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Database Health</p>
                <p className="font-semibold text-stat-blue">Excellent</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="animate-fade-in" style={{ animationDelay: "0.2s" }}>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-stat-orange/10 rounded-lg">
                <Zap className="h-5 w-5 text-stat-orange" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Performance</p>
                <p className="font-semibold text-stat-orange">98.5%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="system" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="system">System Settings</TabsTrigger>
          <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="system" className="space-y-6">
          <Card className="animate-fade-in">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                System Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Real-time Updates</Label>
                  <p className="text-sm text-muted-foreground">Enable live data updates</p>
                </div>
                <Switch 
                  checked={systemSettings.realTimeUpdates}
                  onCheckedChange={(checked) => handleSettingChange("realTimeUpdates", checked)}
                />
              </div>

              <div className="space-y-2">
                <Label>Data Retention (days)</Label>
                <Input 
                  value={systemSettings.dataRetention}
                  onChange={(e) => handleSettingChange("dataRetention", e.target.value)}
                  placeholder="90"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto Backup</Label>
                  <p className="text-sm text-muted-foreground">Automatic daily backups</p>
                </div>
                <Switch 
                  checked={systemSettings.autoBackup}
                  onCheckedChange={(checked) => handleSettingChange("autoBackup", checked)}
                />
              </div>

              <div className="space-y-2">
                <Label>Alert Threshold (%)</Label>
                <Input 
                  value={systemSettings.alertThreshold}
                  onChange={(e) => handleSettingChange("alertThreshold", e.target.value)}
                  placeholder="95"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="maintenance" className="space-y-6">
          <Card className="animate-fade-in">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <RefreshCw className="h-5 w-5" />
                System Maintenance
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <Label>Maintenance Mode</Label>
                  <p className="text-sm text-muted-foreground">Temporarily disable user access</p>
                </div>
                <Switch 
                  checked={maintenanceMode}
                  onCheckedChange={setMaintenanceMode}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button 
                  onClick={() => handleSystemAction("Cache Clear")}
                  variant="outline"
                  className="w-full"
                >
                  Clear Cache
                </Button>
                
                <Button 
                  onClick={() => handleSystemAction("Database Optimization")}
                  variant="outline"
                  className="w-full"
                >
                  Optimize Database
                </Button>
                
                <Button 
                  onClick={() => handleSystemAction("Log Rotation")}
                  variant="outline"
                  className="w-full"
                >
                  Rotate Logs
                </Button>
                
                <Button 
                  onClick={() => handleSystemAction("System Restart")}
                  variant="destructive"
                  className="w-full"
                >
                  Restart System
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card className="animate-fade-in">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security Controls
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <span>Failed Login Attempts</span>
                  <Badge variant="secondary">3 today</Badge>
                </div>
                
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <span>Active Sessions</span>
                  <Badge variant="secondary">12 users</Badge>
                </div>
                
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <span>API Rate Limits</span>
                  <Badge className="bg-stat-green/10 text-stat-green">Normal</Badge>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button 
                  onClick={() => handleSystemAction("Security Scan")}
                  variant="outline"
                  className="w-full"
                >
                  Run Security Scan
                </Button>
                
                <Button 
                  onClick={() => handleSystemAction("Audit Log Export")}
                  variant="outline"
                  className="w-full"
                >
                  Export Audit Logs
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-6">
          <Card className="animate-fade-in">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                System Alerts
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <CheckCircle className="h-4 w-4 text-stat-green" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">System backup completed</p>
                    <p className="text-xs text-muted-foreground">2 hours ago</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <AlertTriangle className="h-4 w-4 text-stat-orange" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">High memory usage detected</p>
                    <p className="text-xs text-muted-foreground">5 hours ago</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <CheckCircle className="h-4 w-4 text-stat-green" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Database optimization completed</p>
                    <p className="text-xs text-muted-foreground">1 day ago</p>
                  </div>
                </div>
              </div>

              <Button 
                onClick={() => handleSystemAction("Alert Clear")}
                variant="outline"
                className="w-full"
              >
                Clear All Alerts
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
