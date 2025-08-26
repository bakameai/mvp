import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon, Filter, RefreshCw, Download } from "lucide-react";

interface AdvancedFiltersProps {
  onFilterChange: (filters: any) => void;
  onRefresh: () => void;
  onExport: () => void;
}

export function AdvancedFilters({ onFilterChange, onRefresh, onExport }: AdvancedFiltersProps) {
  const [dateRange, setDateRange] = useState<{ from?: Date; to?: Date }>({});
  const [filters, setFilters] = useState({
    timeframe: "7d",
    module: "all",
    interactionType: "all",
    status: "all"
  });

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange({ ...newFilters, dateRange });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Filter className="h-5 w-5" />
          IVR Analytics Filters
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          <div className="space-y-2">
            <Label>Time Range</Label>
            <Select value={filters.timeframe} onValueChange={(value) => handleFilterChange("timeframe", value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1d">Last 24 Hours</SelectItem>
                <SelectItem value="7d">Last 7 Days</SelectItem>
                <SelectItem value="30d">Last 30 Days</SelectItem>
                <SelectItem value="90d">Last 90 Days</SelectItem>
                <SelectItem value="custom">Custom Range</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Learning Module</Label>
            <Select value={filters.module} onValueChange={(value) => handleFilterChange("module", value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Modules</SelectItem>
                <SelectItem value="english">English</SelectItem>
                <SelectItem value="math">Mathematics</SelectItem>
                <SelectItem value="comprehension">Reading</SelectItem>
                <SelectItem value="debate">Debate</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Interaction Type</Label>
            <Select value={filters.interactionType} onValueChange={(value) => handleFilterChange("interactionType", value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="voice">Voice Calls</SelectItem>
                <SelectItem value="sms">SMS Messages</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Session Status</Label>
            <Select value={filters.status} onValueChange={(value) => handleFilterChange("status", value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sessions</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="abandoned">Abandoned</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Custom Date Range</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="w-full justify-start text-left font-normal">
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {dateRange.from ? (
                    dateRange.to ? (
                      <>
                        {dateRange.from.toLocaleDateString()} -{" "}
                        {dateRange.to.toLocaleDateString()}
                      </>
                    ) : (
                      dateRange.from.toLocaleDateString()
                    )
                  ) : (
                    <span>Pick a date range</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  initialFocus
                  mode="range"
                  defaultMonth={dateRange.from}
                  selected={dateRange as any}
                  onSelect={setDateRange as any}
                  numberOfMonths={2}
                />
              </PopoverContent>
            </Popover>
          </div>

          <div className="flex items-end gap-2">
            <Button onClick={onRefresh} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button onClick={onExport} variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
