import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Search, Filter, Download, Eye } from "lucide-react";
import { adminAPI } from "@/services/api";

interface DataTablesProps {
  type: "users" | "sessions";
}

export function DataTables({ type }: DataTablesProps) {
  const [data, setData] = useState<any[]>([]);
  const [filteredData, setFilteredData] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (type === "sessions") {
          const sessions = await adminAPI.getUserSessions();
          setData(sessions);
          setFilteredData(sessions);
        } else {
          const stats = await adminAPI.getAdminStats();
          const mockUsers = [
            {
              id: 1,
              phone_number: "+250 XXX XXX XXX",
              sessions_count: 12,
              last_active: "2 hours ago",
              status: "active",
              total_duration: 145
            },
            {
              id: 2,
              phone_number: "+250 YYY YYY YYY",
              sessions_count: 8,
              last_active: "1 day ago",
              status: "inactive",
              total_duration: 98
            }
          ];
          setData(mockUsers);
          setFilteredData(mockUsers);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setData([]);
        setFilteredData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [type]);

  useEffect(() => {
    if (searchTerm) {
      const filtered = data.filter((item: any) => {
        if (type === "sessions") {
          return item.phone_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                 item.module_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                 item.interaction_type?.toLowerCase().includes(searchTerm.toLowerCase());
        } else {
          return item.phone_number?.toLowerCase().includes(searchTerm.toLowerCase());
        }
      });
      setFilteredData(filtered);
    } else {
      setFilteredData(data);
    }
  }, [searchTerm, data, type]);

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'completed':
        return 'bg-stat-green/10 text-stat-green';
      case 'inactive':
      case 'abandoned':
        return 'bg-stat-orange/10 text-stat-orange';
      case 'pending':
        return 'bg-stat-blue/10 text-stat-blue';
      default:
        return 'bg-muted/50 text-muted-foreground';
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    if (!timestamp) return 'Unknown';
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} days ago`;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading {type === "sessions" ? "IVR Sessions" : "Students"}...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-gray-200 rounded animate-pulse"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="animate-fade-in">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{type === "sessions" ? "IVR Sessions" : "Students"}</CardTitle>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder={`Search ${type}...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                {type === "sessions" ? (
                  <>
                    <TableHead>Phone Number</TableHead>
                    <TableHead>Module</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </>
                ) : (
                  <>
                    <TableHead>Phone Number</TableHead>
                    <TableHead>Sessions</TableHead>
                    <TableHead>Total Duration</TableHead>
                    <TableHead>Last Active</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </>
                )}
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={type === "sessions" ? 7 : 6} className="text-center py-8">
                    No {type} found
                  </TableCell>
                </TableRow>
              ) : (
                filteredData.map((item: any, index) => (
                  <TableRow key={index}>
                    {type === "sessions" ? (
                      <>
                        <TableCell className="font-medium">{item.phone_number}</TableCell>
                        <TableCell>{item.module_name || 'Unknown'}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className={item.interaction_type === 'voice' ? 'text-stat-blue' : 'text-stat-green'}>
                            {item.interaction_type || 'Unknown'}
                          </Badge>
                        </TableCell>
                        <TableCell>{item.session_duration ? `${Math.round(item.session_duration)}min` : 'N/A'}</TableCell>
                        <TableCell>{formatTimeAgo(item.timestamp)}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(item.session_duration > 0 ? 'completed' : 'abandoned')}>
                            {item.session_duration > 0 ? 'Completed' : 'Abandoned'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </>
                    ) : (
                      <>
                        <TableCell className="font-medium">{item.phone_number}</TableCell>
                        <TableCell>{item.sessions_count} sessions</TableCell>
                        <TableCell>{item.total_duration}min</TableCell>
                        <TableCell>{item.last_active}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(item.status)}>
                            {item.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </>
                    )}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
