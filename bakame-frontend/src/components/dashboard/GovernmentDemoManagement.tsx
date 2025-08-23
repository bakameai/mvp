import { useState, useEffect } from 'react';
import { authAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { UserProfile } from '@/pages/AdminDashboard';

interface GovernmentDemoRequest {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  organization: string;
  position: string;
  agency_type: string;
  citizen_size: string | null;
  current_systems: string | null;
  primary_use_case: string;
  timeline: string | null;
  budget: string | null;
  status: string;
  created_at: string;
}

interface GovernmentDemoManagementProps {
  userProfile: UserProfile;
}

export const GovernmentDemoManagement = ({ userProfile }: GovernmentDemoManagementProps) => {
  const [requests, setRequests] = useState<GovernmentDemoRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      // Use type assertion for the new table
      const { data, error } = await (supabase as any)
        .from('government_demo_requests')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching government demo requests:', error);
        toast({
          title: "Error",
          description: "Failed to load government demo requests",
          variant: "destructive",
        });
      } else {
        setRequests(data || []);
      }
    } catch (error) {
      console.error('Error fetching requests:', error);
      // If the table doesn't exist, show empty state
      setRequests([]);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (id: string, newStatus: string) => {
    setUpdating(id);
    try {
      const { error } = await (supabase as any)
        .from('government_demo_requests')
        .update({ status: newStatus })
        .eq('id', id);

      if (error) {
        console.error('Error updating status:', error);
        toast({
          title: "Error",
          description: "Failed to update status",
          variant: "destructive",
        });
      } else {
        setRequests(prev => 
          prev.map(req => 
            req.id === id ? { ...req, status: newStatus } : req
          )
        );
        toast({
          title: "Status Updated",
          description: "Request status has been updated successfully",
        });
      }
    } catch (error) {
      console.error('Error updating status:', error);
    } finally {
      setUpdating(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500';
      case 'contacted': return 'bg-blue-500';
      case 'demo_scheduled': return 'bg-purple-500';
      case 'completed': return 'bg-green-500';
      case 'rejected': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (userProfile.role !== 'admin') {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Access denied. Admin privileges required.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Government Demo Requests</h2>
        <Badge variant="outline" className="text-sm">
          {requests.length} Total Requests
        </Badge>
      </div>

      <div className="grid gap-6">
        {requests.map((request) => (
          <Card key={request.id} className="shadow-sm">
            <CardHeader className="pb-4">
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">
                    {request.first_name} {request.last_name}
                  </CardTitle>
                  <p className="text-sm text-gray-600 mt-1">
                    {request.position} at {request.organization}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <Badge className={`${getStatusColor(request.status)} text-white`}>
                    {request.status.replace('_', ' ').toUpperCase()}
                  </Badge>
                  <p className="text-xs text-gray-500">
                    {formatDate(request.created_at)}
                  </p>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <strong>Email:</strong> {request.email}
                </div>
                <div>
                  <strong>Phone:</strong> {request.phone || 'Not provided'}
                </div>
                <div>
                  <strong>Agency Type:</strong> {request.agency_type}
                </div>
                <div>
                  <strong>Citizens Served:</strong> {request.citizen_size || 'Not specified'}
                </div>
                <div>
                  <strong>Primary Use Case:</strong> {request.primary_use_case}
                </div>
                <div>
                  <strong>Timeline:</strong> {request.timeline || 'Not specified'}
                </div>
                <div>
                  <strong>Budget:</strong> {request.budget || 'Not specified'}
                </div>
              </div>

              {request.current_systems && (
                <div>
                  <strong className="text-sm">Current Systems & Challenges:</strong>
                  <p className="text-sm text-gray-600 mt-1 bg-gray-50 p-3 rounded">
                    {request.current_systems}
                  </p>
                </div>
              )}

              <div className="flex justify-between items-center pt-4 border-t">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Status:</span>
                  <Select
                    value={request.status}
                    onValueChange={(value) => updateStatus(request.id, value)}
                    disabled={updating === request.id}
                  >
                    <SelectTrigger className="w-40">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="contacted">Contacted</SelectItem>
                      <SelectItem value="demo_scheduled">Demo Scheduled</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="rejected">Rejected</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => window.open(`mailto:${request.email}?subject=Bakame AI Government Demo Request`)}
                >
                  Contact
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}

        {requests.length === 0 && (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-gray-600">No government demo requests found.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
