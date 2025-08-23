
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  GraduationCap, 
  Users, 
  BookOpen, 
  Phone, 
  Calendar,
  MessageSquare,
  AlertCircle,
  TrendingUp
} from "lucide-react";

export const SchoolAdminDashboard = () => {
  const mockData = {
    totalStudents: 1250,
    totalParents: 2100,
    monthlyInteractions: 3450,
    attendanceRate: 94.2,
    pendingMessages: 28,
    scheduledCalls: 15,
    emergencyContacts: 98.7,
    grades: [
      { name: "Kindergarten", students: 120, attendance: 96.5 },
      { name: "Elementary (1-5)", students: 480, attendance: 95.1 },
      { name: "Middle School (6-8)", students: 360, attendance: 93.2 },
      { name: "High School (9-12)", students: 290, attendance: 91.8 }
    ]
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">School Admin Dashboard</h1>
          <p className="text-muted-foreground">Parent communication and student management system</p>
        </div>
        <Button className="flex items-center space-x-2">
          <MessageSquare className="w-4 h-4" />
          <span>Send Announcement</span>
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.totalStudents.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Enrolled this year</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Parent Contacts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.totalParents.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Registered in system</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Monthly Interactions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.monthlyInteractions.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+15%</span> from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Attendance Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.attendanceRate}%</div>
            <p className="text-xs text-muted-foreground">School average</p>
          </CardContent>
        </Card>
      </div>

      {/* Communication Status */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-blue-800">
            <Phone className="w-5 h-5" />
            <span>Communication Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-800">{mockData.pendingMessages}</div>
              <p className="text-blue-600 text-sm">Pending Messages</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-800">{mockData.scheduledCalls}</div>
              <p className="text-blue-600 text-sm">Scheduled Calls</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-800">{mockData.emergencyContacts}%</div>
              <p className="text-blue-600 text-sm">Emergency Contact Coverage</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Grade Level Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <GraduationCap className="w-5 h-5" />
            <span>Grade Level Overview</span>
          </CardTitle>
          <CardDescription>Student distribution and attendance by grade</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {mockData.grades.map((grade, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium">{grade.name}</h3>
                    <p className="text-sm text-muted-foreground">{grade.students} students</p>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{grade.attendance}%</div>
                    <div className="text-sm text-muted-foreground">Attendance</div>
                  </div>
                </div>
                <Progress value={grade.attendance} className="h-2" />
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
              <Calendar className="w-5 h-5" />
              <span>Today's Activities</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <AlertCircle className="w-5 h-5 text-orange-500" />
                <div>
                  <p className="font-medium">Parent-Teacher Conferences</p>
                  <p className="text-sm text-muted-foreground">2:00 PM - 6:00 PM</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <MessageSquare className="w-5 h-5 text-blue-500" />
                <div>
                  <p className="font-medium">Attendance Notifications</p>
                  <p className="text-sm text-muted-foreground">Send at 10:00 AM</p>
                </div>
              </div>
              <Button className="w-full">View Full Schedule</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5" />
              <span>Communication Tools</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Phone className="w-4 h-4 mr-2" />
                Parent Notification System
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <MessageSquare className="w-4 h-4 mr-2" />
                Emergency Broadcast
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <BookOpen className="w-4 h-4 mr-2" />
                Academic Updates
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
