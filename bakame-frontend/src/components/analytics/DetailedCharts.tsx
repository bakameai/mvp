import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";

const sessionData = [
  { name: "Mon", sessions: 45, duration: 12.5, completion: 85 },
  { name: "Tue", sessions: 52, duration: 14.2, completion: 88 },
  { name: "Wed", sessions: 48, duration: 13.8, completion: 82 },
  { name: "Thu", sessions: 61, duration: 15.1, completion: 91 },
  { name: "Fri", sessions: 55, duration: 13.9, completion: 87 },
  { name: "Sat", sessions: 38, duration: 11.2, completion: 79 },
  { name: "Sun", sessions: 42, duration: 12.8, completion: 83 }
];

const moduleData = [
  { name: "English", value: 45, color: "#3b82f6" },
  { name: "Math", value: 25, color: "#10b981" },
  { name: "Reading", value: 20, color: "#8b5cf6" },
  { name: "Debate", value: 10, color: "#f59e0b" }
];

const hourlyData = [
  { hour: "00", calls: 2, sms: 5 },
  { hour: "01", calls: 1, sms: 3 },
  { hour: "02", calls: 0, sms: 2 },
  { hour: "03", calls: 1, sms: 1 },
  { hour: "04", calls: 3, sms: 4 },
  { hour: "05", calls: 8, sms: 12 },
  { hour: "06", calls: 15, sms: 18 },
  { hour: "07", calls: 25, sms: 22 },
  { hour: "08", calls: 35, sms: 28 },
  { hour: "09", calls: 42, sms: 35 },
  { hour: "10", calls: 38, sms: 32 },
  { hour: "11", calls: 45, sms: 38 },
  { hour: "12", calls: 48, sms: 42 },
  { hour: "13", calls: 52, sms: 45 },
  { hour: "14", calls: 55, sms: 48 },
  { hour: "15", calls: 58, sms: 52 },
  { hour: "16", calls: 62, sms: 55 },
  { hour: "17", calls: 65, sms: 58 },
  { hour: "18", calls: 68, sms: 62 },
  { hour: "19", calls: 45, sms: 48 },
  { hour: "20", calls: 35, sms: 38 },
  { hour: "21", calls: 25, sms: 28 },
  { hour: "22", calls: 15, sms: 18 },
  { hour: "23", calls: 8, sms: 12 }
];

export function DetailedCharts() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <Card className="animate-fade-in">
        <CardHeader>
          <CardTitle>Session Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="sessions" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="sessions">Sessions</TabsTrigger>
              <TabsTrigger value="duration">Duration</TabsTrigger>
              <TabsTrigger value="completion">Completion</TabsTrigger>
            </TabsList>
            
            <TabsContent value="sessions" className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={sessionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="sessions" 
                    stroke="#3b82f6" 
                    fill="#3b82f6" 
                    fillOpacity={0.1}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </TabsContent>
            
            <TabsContent value="duration" className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sessionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="duration" 
                    stroke="#10b981" 
                    strokeWidth={3}
                  />
                </LineChart>
              </ResponsiveContainer>
            </TabsContent>
            
            <TabsContent value="completion" className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sessionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="completion" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Card className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
        <CardHeader>
          <CardTitle>Learning Module Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={moduleData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {moduleData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-4">
            {moduleData.map((module, index) => (
              <div key={index} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: module.color }}
                />
                <span className="text-sm text-muted-foreground">{module.name}</span>
                <span className="text-sm font-medium ml-auto">{module.value}%</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="lg:col-span-2 animate-fade-in" style={{ animationDelay: "0.2s" }}>
        <CardHeader>
          <CardTitle>Hourly Activity Pattern</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="calls" fill="#3b82f6" name="Voice Calls" />
                <Bar dataKey="sms" fill="#10b981" name="SMS Messages" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
