import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FileText, Download, Table, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export function ExportControls() {
  const { toast } = useToast();
  const [exportConfig, setExportConfig] = useState({
    format: "csv",
    dateRange: "7d",
    includeMetadata: true,
    compression: false
  });

  const handleExport = (type: string) => {
    toast({
      title: "Export Started",
      description: `${type} export is being generated. You'll receive an email when complete.`
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <Card className="animate-fade-in">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Quick Exports
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button 
            onClick={() => handleExport("IVR Sessions")} 
            className="w-full justify-start"
            variant="outline"
          >
            <Table className="h-4 w-4 mr-2" />
            Export All IVR Sessions
          </Button>
          
          <Button 
            onClick={() => handleExport("Student Data")} 
            className="w-full justify-start"
            variant="outline"
          >
            <FileText className="h-4 w-4 mr-2" />
            Export Student Data
          </Button>
          
          <Button 
            onClick={() => handleExport("Analytics Report")} 
            className="w-full justify-start"
            variant="outline"
          >
            <Zap className="h-4 w-4 mr-2" />
            Generate Analytics Report
          </Button>
          
          <Button 
            onClick={() => handleExport("Performance Metrics")} 
            className="w-full justify-start"
            variant="outline"
          >
            <Download className="h-4 w-4 mr-2" />
            Export Performance Metrics
          </Button>
        </CardContent>
      </Card>

      <Card className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Custom Export
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Export Format</Label>
            <Select 
              value={exportConfig.format} 
              onValueChange={(value) => setExportConfig({...exportConfig, format: value})}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="csv">CSV</SelectItem>
                <SelectItem value="xlsx">Excel (XLSX)</SelectItem>
                <SelectItem value="json">JSON</SelectItem>
                <SelectItem value="pdf">PDF Report</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Date Range</Label>
            <Select 
              value={exportConfig.dateRange} 
              onValueChange={(value) => setExportConfig({...exportConfig, dateRange: value})}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1d">Last 24 Hours</SelectItem>
                <SelectItem value="7d">Last 7 Days</SelectItem>
                <SelectItem value="30d">Last 30 Days</SelectItem>
                <SelectItem value="90d">Last 90 Days</SelectItem>
                <SelectItem value="all">All Time</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Email Address (Optional)</Label>
            <Input placeholder="your@email.com" />
          </div>

          <Button 
            onClick={() => handleExport("Custom")} 
            className="w-full"
          >
            <Download className="h-4 w-4 mr-2" />
            Generate Custom Export
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
