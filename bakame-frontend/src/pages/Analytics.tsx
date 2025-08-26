import React, { useState } from "react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AdvancedFilters } from "@/components/analytics/AdvancedFilters";
import { MetricsGrid } from "@/components/analytics/MetricsGrid";
import { DetailedCharts } from "@/components/analytics/DetailedCharts";
import { DataTables } from "@/components/analytics/DataTables";
import { AdminControls } from "@/components/analytics/AdminControls";
import { ExportControls } from "@/components/analytics/ExportControls";
import { BarChart3, Settings, Users, Database, Activity, Download } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Analytics = () => {
  const [filters, setFilters] = useState({
    timeframe: "7d",
    userType: "all",
    platform: "all",
    status: "all",
    dateRange: {}
  });
  const [activeTab, setActiveTab] = useState("overview");
  const [isRealTime, setIsRealTime] = useState(true);

  const { toast } = useToast();

  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
    toast({
      title: "Filters Applied",
      description: "Analytics data refreshed with new filter criteria."
    });
  };

  const handleRefresh = () => {
    toast({
      title: "Data Refreshed",
      description: "Latest analytics data has been loaded."
    });
  };

  const handleExport = () => {
    toast({
      title: "Export Started",
      description: "Analytics report is being generated. You'll receive an email when complete."
    });
  };

  return (
    <DashboardLayout>
      <div className="p-8 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">IVR Learning Analytics</h1>
            <p className="text-muted-foreground mt-2">
              Comprehensive IVR system analytics with real-time monitoring and admin controls
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Badge 
              variant={isRealTime ? "default" : "secondary"} 
              className="animate-pulse-glow"
            >
              {isRealTime ? "● Live Data" : "○ Static Data"}
            </Badge>
            <Button
              variant="outline"
              onClick={() => setIsRealTime(!isRealTime)}
            >
              <Activity className="h-4 w-4 mr-2" />
              Toggle Real-time
            </Button>
          </div>
        </div>

        <AdvancedFilters 
          onFilterChange={handleFilterChange}
          onRefresh={handleRefresh}
          onExport={handleExport}
        />

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Students
            </TabsTrigger>
            <TabsTrigger value="sessions" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              IVR Sessions
            </TabsTrigger>
            <TabsTrigger value="data" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              Data Tables
            </TabsTrigger>
            <TabsTrigger value="export" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Export
            </TabsTrigger>
            <TabsTrigger value="admin" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Admin Controls
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-8">
            <MetricsGrid />
            <DetailedCharts />
          </TabsContent>

          <TabsContent value="users" className="space-y-6">
            <DataTables type="users" />
          </TabsContent>

          <TabsContent value="sessions" className="space-y-6">
            <DataTables type="sessions" />
          </TabsContent>

          <TabsContent value="data" className="space-y-6">
            <div className="grid grid-cols-1 gap-8">
              <DataTables type="users" />
              <DataTables type="sessions" />
            </div>
          </TabsContent>

          <TabsContent value="export" className="space-y-6">
            <ExportControls />
          </TabsContent>

          <TabsContent value="admin" className="space-y-6">
            <AdminControls />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

export default Analytics;
