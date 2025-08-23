
import { useState, useEffect } from 'react';
import { authAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { UserProfile } from '@/pages/AdminDashboard';

interface NewsletterSubscription {
  id: string;
  email: string;
  name: string | null;
  subscribed_at: string;
  status: string;
  source: string | null;
}

interface NewsletterManagementProps {
  userProfile: UserProfile;
}

export const NewsletterManagement = ({ userProfile }: NewsletterManagementProps) => {
  const [subscriptions, setSubscriptions] = useState<NewsletterSubscription[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const fetchSubscriptions = async () => {
    try {
      // Use type assertion for the newsletter subscriptions table
      const { data, error } = await (supabase as any)
        .from('newsletter_subscriptions')
        .select('*')
        .order('subscribed_at', { ascending: false });

      if (error) {
        console.error('Error fetching newsletter subscriptions:', error);
        toast({
          title: "Error",
          description: "Failed to load newsletter subscriptions",
          variant: "destructive",
        });
      } else {
        setSubscriptions(data || []);
      }
    } catch (error) {
      console.error('Error fetching subscriptions:', error);
      // If the table doesn't exist, show empty state
      setSubscriptions([]);
    } finally {
      setLoading(false);
    }
  };

  const exportSubscriptions = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Name,Email,Status,Source,Subscribed At\n"
      + subscriptions.map(sub => 
          `"${sub.name || ''}","${sub.email}","${sub.status}","${sub.source || ''}","${sub.subscribed_at}"`
        ).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "newsletter_subscriptions.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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

  const activeSubscriptions = subscriptions.filter(sub => sub.status === 'active');
  const unsubscribedCount = subscriptions.filter(sub => sub.status === 'unsubscribed').length;

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
        <h2 className="text-2xl font-bold">Newsletter Management</h2>
        <Button onClick={exportSubscriptions} variant="outline">
          Export CSV
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-green-600">{activeSubscriptions.length}</div>
            <p className="text-sm text-gray-600">Active Subscribers</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-red-600">{unsubscribedCount}</div>
            <p className="text-sm text-gray-600">Unsubscribed</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-blue-600">{subscriptions.length}</div>
            <p className="text-sm text-gray-600">Total Subscriptions</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Subscriptions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {subscriptions.slice(0, 20).map((subscription) => (
              <div key={subscription.id} className="flex justify-between items-center p-4 border rounded-lg">
                <div>
                  <div className="font-medium">
                    {subscription.name || subscription.email}
                  </div>
                  {subscription.name && (
                    <div className="text-sm text-gray-600">{subscription.email}</div>
                  )}
                  <div className="text-xs text-gray-500">
                    {formatDate(subscription.subscribed_at)} • Source: {subscription.source || 'Unknown'}
                  </div>
                </div>
                <Badge 
                  variant={subscription.status === 'active' ? 'default' : 'secondary'}
                >
                  {subscription.status}
                </Badge>
              </div>
            ))}

            {subscriptions.length === 0 && (
              <div className="text-center py-8">
                <p className="text-gray-600">No newsletter subscriptions found.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
