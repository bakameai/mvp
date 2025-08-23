import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { adminAPI } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { UserProfile } from "@/pages/AdminDashboard";
import { Key, Webhook, Settings, Plus, Copy, Trash2, Activity } from "lucide-react";

interface APIKey {
  id: string;
  name: string;
  key: string;
  permissions: string[];
  created_at: string;
  last_used: string;
  is_active: boolean;
}

interface WebhookEndpoint {
  id: string;
  name: string;
  url: string;
  events: string[];
  secret: string;
  is_active: boolean;
  created_at: string;
}

interface APIManagementProps {
  userProfile: UserProfile;
}

export const APIManagement = ({ userProfile }: APIManagementProps) => {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [webhooks, setWebhooks] = useState<WebhookEndpoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateKeyDialogOpen, setIsCreateKeyDialogOpen] = useState(false);
  const [isCreateWebhookDialogOpen, setIsCreateWebhookDialogOpen] = useState(false);
  const [newApiKey, setNewApiKey] = useState({
    name: "",
    permissions: [] as string[]
  });
  const [newWebhook, setNewWebhook] = useState({
    name: "",
    url: "",
    events: [] as string[]
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchAPIKeys();
    fetchWebhooks();
  }, []);

  const fetchAPIKeys = async () => {
    try {
      const data = await adminAPI.getAPIKeys();
      setApiKeys(data || []);
    } catch (error) {
      console.error('Error fetching API keys:', error);
      toast({
        title: "Error",
        description: "Failed to load API keys",
        variant: "destructive",
      });
    }
  };

  const fetchWebhooks = async () => {
    try {
      const data = await adminAPI.getWebhooks();
      setWebhooks(data || []);
    } catch (error) {
      console.error('Error fetching webhooks:', error);
      toast({
        title: "Error",
        description: "Failed to load webhooks",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createAPIKey = async () => {
    try {
      const data = await adminAPI.createAPIKey(newApiKey);
      setApiKeys([data, ...apiKeys]);
      setIsCreateKeyDialogOpen(false);
      setNewApiKey({ name: "", permissions: [] });
      toast({
        title: "Success",
        description: "API key created successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create API key",
        variant: "destructive",
      });
    }
  };

  const createWebhook = async () => {
    try {
      const data = await adminAPI.createWebhook(newWebhook);
      setWebhooks([data, ...webhooks]);
      setIsCreateWebhookDialogOpen(false);
      setNewWebhook({ name: "", url: "", events: [] });
      toast({
        title: "Success",
        description: "Webhook created successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create webhook",
        variant: "destructive",
      });
    }
  };

  const toggleAPIKey = async (keyId: string, isActive: boolean) => {
    try {
      await adminAPI.toggleAPIKey(keyId, isActive);
      setApiKeys(apiKeys.map(key => 
        key.id === keyId ? { ...key, is_active: isActive } : key
      ));
      toast({
        title: "Success",
        description: `API key ${isActive ? 'activated' : 'deactivated'}`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update API key",
        variant: "destructive",
      });
    }
  };

  const deleteAPIKey = async (keyId: string) => {
    if (!confirm("Are you sure you want to delete this API key?")) return;

    try {
      await adminAPI.deleteAPIKey(keyId);
      setApiKeys(apiKeys.filter(key => key.id !== keyId));
      toast({
        title: "Success",
        description: "API key deleted successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete API key",
        variant: "destructive",
      });
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied",
      description: "API key copied to clipboard",
    });
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
        <h2 className="text-2xl font-bold">API Management</h2>
        <Badge variant="outline">Third-party Integrations</Badge>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Key className="h-5 w-5" />
                <span>API Keys</span>
              </div>
              <Dialog open={isCreateKeyDialogOpen} onOpenChange={setIsCreateKeyDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Create Key
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create API Key</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="key-name">Key Name</Label>
                      <Input
                        id="key-name"
                        value={newApiKey.name}
                        onChange={(e) => setNewApiKey({ ...newApiKey, name: e.target.value })}
                        placeholder="Enter key name"
                      />
                    </div>
                    <div>
                      <Label>Permissions</Label>
                      <div className="space-y-2 mt-2">
                        {['read', 'write', 'admin', 'analytics'].map((permission) => (
                          <div key={permission} className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id={permission}
                              checked={newApiKey.permissions.includes(permission)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setNewApiKey({
                                    ...newApiKey,
                                    permissions: [...newApiKey.permissions, permission]
                                  });
                                } else {
                                  setNewApiKey({
                                    ...newApiKey,
                                    permissions: newApiKey.permissions.filter(p => p !== permission)
                                  });
                                }
                              }}
                            />
                            <Label htmlFor={permission} className="capitalize">{permission}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setIsCreateKeyDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={createAPIKey} disabled={!newApiKey.name}>
                        Create Key
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : apiKeys.length === 0 ? (
              <p className="text-center py-8 text-gray-600">No API keys created.</p>
            ) : (
              <div className="space-y-4">
                {apiKeys.map((key) => (
                  <div key={key.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{key.name}</h4>
                      <div className="flex items-center space-x-2">
                        <Switch
                          checked={key.is_active}
                          onCheckedChange={(checked) => toggleAPIKey(key.id, checked)}
                        />
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => deleteAPIKey(key.id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded flex-1">
                          {key.key.substring(0, 20)}...
                        </code>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => copyToClipboard(key.key)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {key.permissions.map((permission) => (
                          <Badge key={permission} variant="secondary" className="text-xs">
                            {permission}
                          </Badge>
                        ))}
                      </div>
                      <p className="text-xs text-gray-500">
                        Created: {new Date(key.created_at).toLocaleDateString()}
                        {key.last_used && (
                          <> • Last used: {new Date(key.last_used).toLocaleDateString()}</>
                        )}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Webhook className="h-5 w-5" />
                <span>Webhooks</span>
              </div>
              <Dialog open={isCreateWebhookDialogOpen} onOpenChange={setIsCreateWebhookDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Webhook
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Webhook</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="webhook-name">Webhook Name</Label>
                      <Input
                        id="webhook-name"
                        value={newWebhook.name}
                        onChange={(e) => setNewWebhook({ ...newWebhook, name: e.target.value })}
                        placeholder="Enter webhook name"
                      />
                    </div>
                    <div>
                      <Label htmlFor="webhook-url">Endpoint URL</Label>
                      <Input
                        id="webhook-url"
                        value={newWebhook.url}
                        onChange={(e) => setNewWebhook({ ...newWebhook, url: e.target.value })}
                        placeholder="https://your-app.com/webhook"
                      />
                    </div>
                    <div>
                      <Label>Events</Label>
                      <div className="space-y-2 mt-2">
                        {['user.created', 'user.updated', 'payment.completed', 'system.alert'].map((event) => (
                          <div key={event} className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id={event}
                              checked={newWebhook.events.includes(event)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setNewWebhook({
                                    ...newWebhook,
                                    events: [...newWebhook.events, event]
                                  });
                                } else {
                                  setNewWebhook({
                                    ...newWebhook,
                                    events: newWebhook.events.filter(ev => ev !== event)
                                  });
                                }
                              }}
                            />
                            <Label htmlFor={event}>{event}</Label>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setIsCreateWebhookDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={createWebhook} disabled={!newWebhook.name || !newWebhook.url}>
                        Create Webhook
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {webhooks.length === 0 ? (
              <p className="text-center py-8 text-gray-600">No webhooks configured.</p>
            ) : (
              <div className="space-y-4">
                {webhooks.map((webhook) => (
                  <div key={webhook.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{webhook.name}</h4>
                      <Badge variant={webhook.is_active ? 'default' : 'secondary'}>
                        {webhook.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600">{webhook.url}</p>
                      <div className="flex flex-wrap gap-1">
                        {webhook.events.map((event) => (
                          <Badge key={event} variant="outline" className="text-xs">
                            {event}
                          </Badge>
                        ))}
                      </div>
                      <p className="text-xs text-gray-500">
                        Created: {new Date(webhook.created_at).toLocaleDateString()}
                      </p>
                    </div>
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
