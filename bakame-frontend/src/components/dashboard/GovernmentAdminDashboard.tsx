
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Shield, 
  Users, 
  FileText, 
  Phone, 
  AlertTriangle,
  Clock,
  CheckCircle,
  Globe
} from "lucide-react";

export const GovernmentAdminDashboard = () => {
  const mockData = {
    totalCitizens: 45000,
    monthlyInquiries: 8750,
    averageResponseTime: "2.3 min",
    serviceAvailability: 99.9,
    emergencyAlerts: 3,
    pendingRequests: 156,
    completedServices: 2340,
    departments: [
      { name: "Public Health", inquiries: 1200, status: "active" },
      { name: "Social Services", inquiries: 890, status: "active" },
      { name: "Public Works", inquiries: 750, status: "maintenance" },
      { name: "Emergency Services", inquiries: 2100, status: "active" }
    ]
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Government Dashboard</h1>
          <p className="text-muted-foreground">Citizen services and emergency communication management</p>
        </div>
        <Button variant="destructive" className="flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4" />
          <span>Emergency Broadcast</span>
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Registered Citizens</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.totalCitizens.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">In system database</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Monthly Inquiries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.monthlyInquiries.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+8%</span> from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.averageResponseTime}</div>
            <p className="text-xs text-muted-foreground">Service requests</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Service Availability</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.serviceAvailability}%</div>
            <p className="text-xs text-muted-foreground">24/7 uptime</p>
          </CardContent>
        </Card>
      </div>

      {/* Emergency Status */}
      <Card className="border-orange-200 bg-orange-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-orange-800">
            <AlertTriangle className="w-5 h-5" />
            <span>Emergency Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-800 font-medium">
                {mockData.emergencyAlerts} Active Emergency Alerts
              </p>
              <p className="text-orange-600 text-sm">Last updated 5 minutes ago</p>
            </div>
            <Button variant="outline" className="border-orange-300 text-orange-800">
              View Details
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Department Services */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="w-5 h-5" />
            <span>Department Services</span>
          </CardTitle>
          <CardDescription>Service status across government departments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockData.departments.map((dept, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-medium">{dept.name}</h3>
                    <p className="text-sm text-muted-foreground">{dept.inquiries} inquiries this month</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge 
                    variant={dept.status === 'active' ? 'default' : 'secondary'}
                    className={dept.status === 'active' ? 'bg-green-100 text-green-800' : ''}
                  >
                    {dept.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Service Management */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Service Requests</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>Pending Requests</span>
                <Badge variant="secondary">{mockData.pendingRequests}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span>Completed This Month</span>
                <Badge className="bg-green-100 text-green-800">{mockData.completedServices}</Badge>
              </div>
              <Button className="w-full">Manage Requests</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="w-5 h-5" />
              <span>Citizen Services</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Phone className="w-4 h-4 mr-2" />
                Configure Service Hotlines
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Users className="w-4 h-4 mr-2" />
                Citizen Registration
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Emergency Protocols
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
