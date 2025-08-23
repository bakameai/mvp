
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Search, Plus, Edit, Trash2, Users, Settings, Shield, Building2 } from "lucide-react";
import { adminAPI } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { UserProfile } from "@/pages/AdminDashboard";

interface Organization {
  id: string;
  name: string;
  type: string;
  description: string | null;
  contact_email: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
  departments?: Department[];
  permissions?: OrganizationPermission[];
  user_count?: number;
}

interface Department {
  id: string;
  name: string;
  description: string | null;
  organization_id: string;
  manager_id: string | null;
  created_at: string;
}

interface OrganizationPermission {
  id: string;
  organization_id: string;
  feature: string;
  access_level: 'none' | 'read' | 'write' | 'admin';
  custom_roles?: string[];
}

interface OrganizationManagementProps {
  userProfile: UserProfile;
}

export const OrganizationManagement = ({ userProfile }: OrganizationManagementProps) => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isPermissionsDialogOpen, setIsPermissionsDialogOpen] = useState(false);
  const [isDepartmentsDialogOpen, setIsDepartmentsDialogOpen] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  const [newOrg, setNewOrg] = useState({
    name: "",
    type: "",
    description: "",
    contact_email: "",
  });
  const [newDepartment, setNewDepartment] = useState({
    name: "",
    description: "",
    manager_id: "",
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      const data = await adminAPI.getOrganizations();
      setOrganizations(data || []);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to fetch organizations",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createOrganization = async () => {
    try {
      const data = await adminAPI.createOrganization({
        ...newOrg,
        created_by: userProfile.id,
      });

      setOrganizations([data, ...organizations]);
      setIsCreateDialogOpen(false);
      setNewOrg({ name: "", type: "", description: "", contact_email: "" });

      toast({
        title: "Success",
        description: "Organization created successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to create organization",
        variant: "destructive",
      });
    }
  };

  const deleteOrganization = async (id: string) => {
    try {
      await adminAPI.deleteOrganization(id);

      setOrganizations(organizations.filter(org => org.id !== id));

      toast({
        title: "Success",
        description: "Organization deleted successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to delete organization",
        variant: "destructive",
      });
    }
  };

  const createDepartment = async () => {
    if (!selectedOrg) return;
    
    try {
      const data = await adminAPI.createDepartment(selectedOrg.id, newDepartment);
      
      setOrganizations(organizations.map(org => 
        org.id === selectedOrg.id 
          ? { ...org, departments: [...(org.departments || []), data] }
          : org
      ));
      
      setNewDepartment({ name: "", description: "", manager_id: "" });
      
      toast({
        title: "Success",
        description: "Department created successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to create department",
        variant: "destructive",
      });
    }
  };

  const updatePermissions = async (orgId: string, permissions: OrganizationPermission[]) => {
    try {
      await adminAPI.updateOrganizationPermissions(orgId, permissions);
      
      setOrganizations(organizations.map(org => 
        org.id === orgId 
          ? { ...org, permissions }
          : org
      ));
      
      toast({
        title: "Success",
        description: "Permissions updated successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to update permissions",
        variant: "destructive",
      });
    }
  };

  const filteredOrganizations = organizations.filter(org => {
    const matchesSearch = org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         org.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         org.contact_email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === "all" || org.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const getTypeBadgeColor = (type: string) => {
    switch (type) {
      case 'school': return 'bg-blue-100 text-blue-800';
      case 'government': return 'bg-red-100 text-red-800';
      case 'ngo': return 'bg-green-100 text-green-800';
      case 'enterprise': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Organization Management</span>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Organization
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Organization</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="org-name">Name</Label>
                    <Input
                      id="org-name"
                      value={newOrg.name}
                      onChange={(e) => setNewOrg({ ...newOrg, name: e.target.value })}
                      placeholder="Organization name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="org-type">Type</Label>
                    <Select value={newOrg.type} onValueChange={(value) => setNewOrg({ ...newOrg, type: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select organization type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="school">School</SelectItem>
                        <SelectItem value="government">Government</SelectItem>
                        <SelectItem value="ngo">NGO</SelectItem>
                        <SelectItem value="enterprise">Enterprise</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="org-email">Contact Email</Label>
                    <Input
                      id="org-email"
                      type="email"
                      value={newOrg.contact_email}
                      onChange={(e) => setNewOrg({ ...newOrg, contact_email: e.target.value })}
                      placeholder="contact@organization.com"
                    />
                  </div>
                  <div>
                    <Label htmlFor="org-description">Description</Label>
                    <Textarea
                      id="org-description"
                      value={newOrg.description}
                      onChange={(e) => setNewOrg({ ...newOrg, description: e.target.value })}
                      placeholder="Organization description"
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={createOrganization} disabled={!newOrg.name || !newOrg.type}>
                      Create
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search organizations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="school">School</SelectItem>
                <SelectItem value="government">Government</SelectItem>
                <SelectItem value="ngo">NGO</SelectItem>
                <SelectItem value="enterprise">Enterprise</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Organization</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Users</TableHead>
                  <TableHead>Departments</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOrganizations.map((org) => (
                  <TableRow key={org.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{org.name}</div>
                        {org.description && (
                          <div className="text-sm text-gray-500 max-w-xs truncate">
                            {org.description}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getTypeBadgeColor(org.type)}>
                        {org.type}
                      </Badge>
                    </TableCell>
                    <TableCell>{org.contact_email || 'Not set'}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Users className="h-4 w-4 text-gray-400" />
                        <span>{org.user_count || 0}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Building2 className="h-4 w-4 text-gray-400" />
                        <span>{org.departments?.length || 0}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {new Date(org.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setSelectedOrg(org);
                            setIsDepartmentsDialogOpen(true);
                          }}
                          title="Manage Departments"
                        >
                          <Building2 className="h-4 w-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setSelectedOrg(org);
                            setIsPermissionsDialogOpen(true);
                          }}
                          title="Manage Permissions"
                        >
                          <Shield className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => deleteOrganization(org.id)}
                          disabled={userProfile.role !== 'admin' && org.created_by !== userProfile.id}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {filteredOrganizations.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No organizations found matching your criteria.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Departments Management Dialog */}
      <Dialog open={isDepartmentsDialogOpen} onOpenChange={setIsDepartmentsDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Manage Departments - {selectedOrg?.name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">Departments</h3>
              <Button size="sm" onClick={() => setNewDepartment({ name: "", description: "", manager_id: "" })}>
                <Plus className="h-4 w-4 mr-2" />
                Add Department
              </Button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="dept-name">Department Name</Label>
                  <Input
                    id="dept-name"
                    value={newDepartment.name}
                    onChange={(e) => setNewDepartment({ ...newDepartment, name: e.target.value })}
                    placeholder="Engineering, Sales, Marketing..."
                  />
                </div>
                <div>
                  <Label htmlFor="dept-description">Description</Label>
                  <Input
                    id="dept-description"
                    value={newDepartment.description}
                    onChange={(e) => setNewDepartment({ ...newDepartment, description: e.target.value })}
                    placeholder="Department description"
                  />
                </div>
                <div className="flex items-end">
                  <Button onClick={createDepartment} disabled={!newDepartment.name}>
                    Create Department
                  </Button>
                </div>
              </div>
            </div>

            <div className="border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Department</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Manager</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {selectedOrg?.departments?.map((dept) => (
                    <TableRow key={dept.id}>
                      <TableCell className="font-medium">{dept.name}</TableCell>
                      <TableCell>{dept.description || 'No description'}</TableCell>
                      <TableCell>{dept.manager_id || 'Not assigned'}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )) || (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-gray-500">
                        No departments created yet
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Permissions Management Dialog */}
      <Dialog open={isPermissionsDialogOpen} onOpenChange={setIsPermissionsDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Manage Permissions - {selectedOrg?.name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-6">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Feature Access Controls</h3>
              
              <div className="border rounded-lg">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Feature</TableHead>
                      <TableHead>Access Level</TableHead>
                      <TableHead>Custom Roles</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {[
                      { feature: 'Telephony System', description: 'Access to voice learning modules' },
                      { feature: 'Analytics Dashboard', description: 'View usage and performance metrics' },
                      { feature: 'User Management', description: 'Manage organization users' },
                      { feature: 'Content Management', description: 'Edit learning content and materials' },
                      { feature: 'Billing & Payments', description: 'Access to billing and subscription management' },
                      { feature: 'API Access', description: 'Programmatic access to BAKAME APIs' },
                    ].map((item) => (
                      <TableRow key={item.feature}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{item.feature}</div>
                            <div className="text-sm text-gray-500">{item.description}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Select defaultValue="read">
                            <SelectTrigger className="w-32">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="none">None</SelectItem>
                              <SelectItem value="read">Read</SelectItem>
                              <SelectItem value="write">Write</SelectItem>
                              <SelectItem value="admin">Admin</SelectItem>
                            </SelectContent>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Input placeholder="manager, supervisor..." className="w-40" />
                        </TableCell>
                        <TableCell>
                          <Button size="sm" variant="outline">
                            <Settings className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setIsPermissionsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={() => {
                  if (selectedOrg) {
                    updatePermissions(selectedOrg.id, []);
                    setIsPermissionsDialogOpen(false);
                  }
                }}>
                  Save Permissions
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default OrganizationManagement;
