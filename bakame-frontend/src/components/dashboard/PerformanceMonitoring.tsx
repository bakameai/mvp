import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { adminAPI } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { UserProfile } from "@/pages/AdminDashboard";
import { Activity, Server, Database, Zap, AlertTriangle, CheckCircle, Clock } from "lucide-react";

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_io: number;
  response_time: number;
  uptime: number;
  active_connections: number;
  error_rate: number;
}

interface HealthCheck {
  service: string;
  status: 'healthy' | 'warning' | 'critical';
  response_time: number;
  last_check: string;
  message: string;
}

interface PerformanceMonitoringProps {
  userProfile: UserProfile;
}

export const PerformanceMonitoring = ({ userProfile }: PerformanceMonitoringProps) => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [healthChecks, setHealthChecks] = useState<HealthCheck[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchMetrics();
    fetchHealthChecks();
    
    const interval = setInterval(() => {
      fetchMetrics();
      fetchHealthChecks();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const data = await adminAPI.getSystemMetrics();
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching system metrics:', error);
      toast({
        title: "Error",
        description: "Failed to load system metrics",
        variant: "destructive",
      });
    }
  };

  const fetchHealthChecks = async () => {
    try {
      const data = await adminAPI.getHealthChecks();
      setHealthChecks(data || []);
    } catch (error) {
      console.error('Error fetching health checks:', error);
      toast({
        title: "Error",
        description: "Failed to load health checks",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-600" />;
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  if (userProfile.role !== 'admin') {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Access denied. Admin privileges required.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Performance Monitoring</h2>
        <Badge variant="outline">Real-time System Health</Badge>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          <div className="grid md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Server className="h-8 w-8 text-blue-600" />
                  <div className="flex-1">
                    <div className="text-2xl font-bold text-blue-600">
                      {metrics?.cpu_usage || 0}%
                    </div>
                    <p className="text-sm text-gray-600">CPU Usage</p>
                    <Progress value={metrics?.cpu_usage || 0} className="mt-2" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Database className="h-8 w-8 text-green-600" />
                  <div className="flex-1">
                    <div className="text-2xl font-bold text-green-600">
                      {metrics?.memory_usage || 0}%
                    </div>
                    <p className="text-sm text-gray-600">Memory Usage</p>
                    <Progress value={metrics?.memory_usage || 0} className="mt-2" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Activity className="h-8 w-8 text-purple-600" />
                  <div className="flex-1">
                    <div className="text-2xl font-bold text-purple-600">
                      {metrics?.response_time || 0}ms
                    </div>
                    <p className="text-sm text-gray-600">Response Time</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Zap className="h-8 w-8 text-orange-600" />
                  <div className="flex-1">
                    <div className="text-2xl font-bold text-orange-600">
                      {metrics?.active_connections || 0}
                    </div>
                    <p className="text-sm text-gray-600">Active Connections</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>System Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Disk Usage</span>
                  <span className="text-sm text-gray-600">{metrics?.disk_usage || 0}%</span>
                </div>
                <Progress value={metrics?.disk_usage || 0} />

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Network I/O</span>
                  <span className="text-sm text-gray-600">{metrics?.network_io || 0} MB/s</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Error Rate</span>
                  <span className="text-sm text-gray-600">{metrics?.error_rate || 0}%</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Uptime</span>
                  <span className="text-sm text-gray-600">
                    {formatUptime(metrics?.uptime || 0)}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Service Health Checks</CardTitle>
              </CardHeader>
              <CardContent>
                {healthChecks.length === 0 ? (
                  <p className="text-center py-8 text-gray-600">No health checks configured.</p>
                ) : (
                  <div className="space-y-4">
                    {healthChecks.map((check, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(check.status)}
                          <div>
                            <p className="font-medium">{check.service}</p>
                            <p className="text-sm text-gray-600">{check.message}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge 
                            variant={
                              check.status === 'healthy' ? 'default' : 
                              check.status === 'warning' ? 'secondary' : 'destructive'
                            }
                          >
                            {check.status}
                          </Badge>
                          <p className="text-xs text-gray-500 mt-1">
                            {check.response_time}ms
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
};
