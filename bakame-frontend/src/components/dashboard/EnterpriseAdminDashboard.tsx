
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Building2, 
  Users, 
  PhoneCall, 
  BarChart3, 
  Settings,
  TrendingUp,
  AlertCircle,
  CheckCircle
} from "lucide-react";

export const EnterpriseAdminDashboard = () => {
  const mockData = {
    totalEmployees: 2500,
    activeUsers: 1847,
    monthlyCallVolume: 12450,
    systemUptime: 99.8,
    pendingTickets: 23,
    resolvedTickets: 187,
    departments: [
      { name: "Customer Service", users: 450, calls: 3200 },
      { name: "Sales", users: 230, calls: 1800 },
      { name: "Technical Support", users: 180, calls: 2100 },
      { name: "HR", users: 120, calls: 450 }
    ]
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Enterprise Dashboard</h1>
          <p className="text-muted-foreground">Manage your organization's IVR systems and users</p>
        </div>
        <Button className="flex items-center space-x-2">
          <Settings className="w-4 h-4" />
          <span>Configure System</span>
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.totalEmployees.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Registered in system</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.activeUsers.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Monthly Calls</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.monthlyCallVolume.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+12%</span> from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.systemUptime}%</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
      </div>

      {/* Department Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Building2 className="w-5 h-5" />
            <span>Department Overview</span>
          </CardTitle>
          <CardDescription>Usage statistics by department</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockData.departments.map((dept, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Users className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-medium">{dept.name}</h3>
                    <p className="text-sm text-muted-foreground">{dept.users} users</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium">{dept.calls.toLocaleString()} calls</div>
                  <div className="text-sm text-muted-foreground">This month</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5" />
              <span>Support Tickets</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>Pending Tickets</span>
                <Badge variant="destructive">{mockData.pendingTickets}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span>Resolved This Month</span>
                <Badge variant="secondary">{mockData.resolvedTickets}</Badge>
              </div>
              <Button className="w-full">View All Tickets</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5" />
              <span>Quick Actions</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <PhoneCall className="w-4 h-4 mr-2" />
                Configure IVR Flow
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Users className="w-4 h-4 mr-2" />
                Manage User Permissions
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <BarChart3 className="w-4 h-4 mr-2" />
                Generate Reports
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
