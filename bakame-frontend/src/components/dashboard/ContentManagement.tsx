import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { adminAPI } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { UserProfile } from "@/pages/AdminDashboard";
import { Edit, Plus, Save, Eye, History } from "lucide-react";

interface ContentPage {
  id: string;
  page_name: string;
  section: string;
  content: string;
  updated_at: string;
  updated_by: string;
}

interface ContentManagementProps {
  userProfile: UserProfile;
}

export const ContentManagement = ({ userProfile }: ContentManagementProps) => {
  const [pages, setPages] = useState<ContentPage[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPage, setSelectedPage] = useState<ContentPage | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editContent, setEditContent] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    fetchPages();
  }, []);

  const fetchPages = async () => {
    try {
      const data = await adminAPI.getContentPages();
      setPages(data || []);
    } catch (error) {
      console.error('Error fetching content pages:', error);
      toast({
        title: "Error",
        description: "Failed to load content pages",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const updateContent = async () => {
    if (!selectedPage) return;

    try {
      await adminAPI.updateContent(selectedPage.page_name, editContent);
      await fetchPages();
      setIsEditDialogOpen(false);
      setSelectedPage(null);
      toast({
        title: "Success",
        description: "Content updated successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update content",
        variant: "destructive",
      });
    }
  };

  const openEditor = (page: ContentPage) => {
    setSelectedPage(page);
    setEditContent(page.content);
    setIsEditDialogOpen(true);
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
        <h2 className="text-2xl font-bold">Content Management System</h2>
        <Badge variant="outline">WordPress-like CMS</Badge>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Website Content Pages</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : pages.length === 0 ? (
              <p className="text-center py-8 text-gray-600">No content pages found.</p>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pages.map((page) => (
                  <Card key={page.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div>
                          <h3 className="font-semibold">{page.page_name}</h3>
                          <p className="text-sm text-gray-600">{page.section}</p>
                        </div>
                        <div className="text-xs text-gray-500">
                          Last updated: {new Date(page.updated_at).toLocaleDateString()}
                          <br />
                          By: {page.updated_by}
                        </div>
                        <div className="flex space-x-2">
                          <Button size="sm" onClick={() => openEditor(page)}>
                            <Edit className="h-4 w-4 mr-1" />
                            Edit
                          </Button>
                          <Button size="sm" variant="outline">
                            <Eye className="h-4 w-4 mr-1" />
                            Preview
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Content: {selectedPage?.page_name}</DialogTitle>
          </DialogHeader>
          {selectedPage && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Page Name</Label>
                  <Input value={selectedPage.page_name} disabled />
                </div>
                <div>
                  <Label>Section</Label>
                  <Input value={selectedPage.section} disabled />
                </div>
              </div>
              <div>
                <Label htmlFor="content-editor">Content</Label>
                <Textarea
                  id="content-editor"
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  rows={15}
                  className="font-mono text-sm"
                  placeholder="Enter HTML content or plain text..."
                />
              </div>
              <div className="flex justify-between">
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <History className="h-4 w-4 mr-1" />
                    Version History
                  </Button>
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-1" />
                    Live Preview
                  </Button>
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={updateContent}>
                    <Save className="h-4 w-4 mr-1" />
                    Save Changes
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};
