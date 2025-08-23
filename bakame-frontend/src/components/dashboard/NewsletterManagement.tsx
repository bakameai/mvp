
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { adminAPI } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { UserProfile } from "@/pages/AdminDashboard";
import { Download, Mail, Users, Plus, Send } from "lucide-react";

interface NewsletterSubscription {
  id: string;
  email: string;
  subscribed_at: string;
  is_active: boolean;
}

interface NewsletterCampaign {
  id: string;
  title: string;
  subject: string;
  content: string;
  created_at: string;
  sent_at?: string;
  recipient_count: number;
  status: 'draft' | 'sent' | 'scheduled';
}

interface NewsletterManagementProps {
  userProfile: UserProfile;
}

export const NewsletterManagement = ({ userProfile }: NewsletterManagementProps) => {
  const [subscriptions, setSubscriptions] = useState<NewsletterSubscription[]>([]);
  const [campaigns, setCampaigns] = useState<NewsletterCampaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateCampaignOpen, setIsCreateCampaignOpen] = useState(false);
  const [newCampaign, setNewCampaign] = useState({
    title: "",
    subject: "",
    content: ""
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchSubscriptions();
    fetchCampaigns();
  }, []);

  const fetchSubscriptions = async () => {
    try {
      const data = await adminAPI.getNewsletterSubscriptions();
      setSubscriptions(data || []);
    } catch (error) {
      console.error('Error fetching subscriptions:', error);
      toast({
        title: "Error",
        description: "Failed to load newsletter subscriptions",
        variant: "destructive",
      });
    }
  };

  const fetchCampaigns = async () => {
    try {
      const data = await adminAPI.getNewsletterCampaigns();
      setCampaigns(data || []);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      toast({
        title: "Error",
        description: "Failed to load newsletter campaigns",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createCampaign = async () => {
    try {
      const data = await adminAPI.createNewsletterCampaign(newCampaign);
      setCampaigns([data, ...campaigns]);
      setIsCreateCampaignOpen(false);
      setNewCampaign({ title: "", subject: "", content: "" });
      toast({
        title: "Success",
        description: "Newsletter campaign created successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create newsletter campaign",
        variant: "destructive",
      });
    }
  };

  const sendCampaign = async (campaignId: string) => {
    try {
      await adminAPI.sendNewsletterCampaign(campaignId);
      await fetchCampaigns();
      toast({
        title: "Success",
        description: "Newsletter campaign sent successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send newsletter campaign",
        variant: "destructive",
      });
    }
  };

  const exportSubscriptions = () => {
    const csvContent = [
      ['Email', 'Subscribed At', 'Status'],
      ...subscriptions.map(sub => [
        sub.email,
        new Date(sub.subscribed_at).toLocaleDateString(),
        sub.is_active ? 'Active' : 'Unsubscribed'
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'newsletter_subscriptions.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (userProfile.role !== 'admin') {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Access denied. Admin privileges required.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Newsletter Management</h2>
        <div className="flex space-x-2">
          <Dialog open={isCreateCampaignOpen} onOpenChange={setIsCreateCampaignOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Campaign
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create Newsletter Campaign</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="campaign-title">Campaign Title</Label>
                  <Input
                    id="campaign-title"
                    value={newCampaign.title}
                    onChange={(e) => setNewCampaign({ ...newCampaign, title: e.target.value })}
                    placeholder="Enter campaign title"
                  />
                </div>
                <div>
                  <Label htmlFor="campaign-subject">Email Subject</Label>
                  <Input
                    id="campaign-subject"
                    value={newCampaign.subject}
                    onChange={(e) => setNewCampaign({ ...newCampaign, subject: e.target.value })}
                    placeholder="Enter email subject"
                  />
                </div>
                <div>
                  <Label htmlFor="campaign-content">Email Content</Label>
                  <Textarea
                    id="campaign-content"
                    value={newCampaign.content}
                    onChange={(e) => setNewCampaign({ ...newCampaign, content: e.target.value })}
                    placeholder="Enter email content"
                    rows={8}
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsCreateCampaignOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={createCampaign} disabled={!newCampaign.title || !newCampaign.subject}>
                    Create Campaign
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          <Button onClick={exportSubscriptions} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Subscriptions
          </Button>
        </div>
      </div>

      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Users className="h-8 w-8 text-blue-600" />
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {subscriptions.filter(sub => sub.is_active).length}
                </div>
                <p className="text-sm text-gray-600">Active Subscribers</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Mail className="h-8 w-8 text-green-600" />
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {subscriptions.length}
                </div>
                <p className="text-sm text-gray-600">Total Subscriptions</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Send className="h-8 w-8 text-purple-600" />
              <div>
                <div className="text-2xl font-bold text-purple-600">
                  {campaigns.filter(c => c.status === 'sent').length}
                </div>
                <p className="text-sm text-gray-600">Campaigns Sent</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Users className="h-8 w-8 text-red-600" />
              <div>
                <div className="text-2xl font-bold text-red-600">
                  {subscriptions.filter(sub => !sub.is_active).length}
                </div>
                <p className="text-sm text-gray-600">Unsubscribed</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Newsletter Campaigns</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : campaigns.length === 0 ? (
              <p className="text-center py-8 text-gray-600">No campaigns created yet.</p>
            ) : (
              <div className="space-y-4">
                {campaigns.map((campaign) => (
                  <div key={campaign.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">{campaign.title}</p>
                      <p className="text-sm text-gray-600">{campaign.subject}</p>
                      <p className="text-xs text-gray-500">
                        Created: {new Date(campaign.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={campaign.status === 'sent' ? 'default' : campaign.status === 'draft' ? 'secondary' : 'outline'}>
                        {campaign.status}
                      </Badge>
                      {campaign.status === 'draft' && (
                        <Button size="sm" onClick={() => sendCampaign(campaign.id)}>
                          <Send className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Subscriptions</CardTitle>
          </CardHeader>
          <CardContent>
            {subscriptions.length === 0 ? (
              <p className="text-center py-8 text-gray-600">No newsletter subscriptions found.</p>
            ) : (
              <div className="space-y-4">
                {subscriptions.slice(0, 10).map((subscription) => (
                  <div key={subscription.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">{subscription.email}</p>
                      <p className="text-sm text-gray-600">
                        Subscribed: {new Date(subscription.subscribed_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Badge variant={subscription.is_active ? "default" : "secondary"}>
                      {subscription.is_active ? "Active" : "Unsubscribed"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
