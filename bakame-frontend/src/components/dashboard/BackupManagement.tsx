import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { adminAPI } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { UserProfile } from "@/pages/AdminDashboard";
import { Download, Upload, Database, HardDrive, Clock, CheckCircle, AlertCircle } from "lucide-react";

interface BackupInfo {
  id: string;
  name: string;
  type: 'full' | 'incremental' | 'users' | 'content';
  size: string;
  created_at: string;
  status: 'completed' | 'in_progress' | 'failed';
}

interface BackupManagementProps {
  userProfile: UserProfile;
}

export const BackupManagement = ({ userProfile }: BackupManagementProps) => {
  const [backups, setBackups] = useState<BackupInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [backupProgress, setBackupProgress] = useState(0);
  const [isBackingUp, setIsBackingUp] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchBackups();
  }, []);

  const fetchBackups = async () => {
    try {
      const data = await adminAPI.getBackups();
      setBackups(data || []);
    } catch (error) {
      console.error('Error fetching backups:', error);
      toast({
        title: "Error",
        description: "Failed to load backup information",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createBackup = async (type: 'full' | 'incremental' | 'users' | 'content') => {
    setIsBackingUp(true);
    setBackupProgress(0);

    try {
      const progressInterval = setInterval(() => {
        setBackupProgress(prev => Math.min(prev + 10, 90));
      }, 500);

      await adminAPI.createBackup(type);
      
      clearInterval(progressInterval);
      setBackupProgress(100);
      
      setTimeout(() => {
        setIsBackingUp(false);
        setBackupProgress(0);
        fetchBackups();
      }, 1000);

      toast({
        title: "Success",
        description: `${type} backup created successfully`,
      });
    } catch (error) {
      setIsBackingUp(false);
      setBackupProgress(0);
      toast({
        title: "Error",
        description: "Failed to create backup",
        variant: "destructive",
      });
    }
  };

  const downloadBackup = async (backupId: string, backupName: string) => {
    try {
      const blob = await adminAPI.downloadBackup(backupId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${backupName}.zip`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download backup",
        variant: "destructive",
      });
    }
  };

  const restoreBackup = async (backupId: string) => {
    if (!confirm("Are you sure you want to restore this backup? This will overwrite current data.")) {
      return;
    }

    try {
      await adminAPI.restoreBackup(backupId);
      toast({
        title: "Success",
        description: "Backup restored successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to restore backup",
        variant: "destructive",
      });
    }
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
        <h2 className="text-2xl font-bold">Backup & Recovery</h2>
        <Badge variant="outline">Data Protection</Badge>
      </div>

      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <Button 
              className="w-full" 
              onClick={() => createBackup('full')}
              disabled={isBackingUp}
            >
              <Database className="h-4 w-4 mr-2" />
              Full Backup
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <Button 
              className="w-full" 
              variant="outline"
              onClick={() => createBackup('incremental')}
              disabled={isBackingUp}
            >
              <HardDrive className="h-4 w-4 mr-2" />
              Incremental
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <Button 
              className="w-full" 
              variant="outline"
              onClick={() => createBackup('users')}
              disabled={isBackingUp}
            >
              <Database className="h-4 w-4 mr-2" />
              Users Only
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <Button 
              className="w-full" 
              variant="outline"
              onClick={() => createBackup('content')}
              disabled={isBackingUp}
            >
              <Database className="h-4 w-4 mr-2" />
              Content Only
            </Button>
          </CardContent>
        </Card>
      </div>

      {isBackingUp && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Creating backup...</span>
                <span className="text-sm text-gray-600">{backupProgress}%</span>
              </div>
              <Progress value={backupProgress} className="w-full" />
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Backup History</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : backups.length === 0 ? (
            <p className="text-center py-8 text-gray-600">No backups found.</p>
          ) : (
            <div className="space-y-4">
              {backups.map((backup) => (
                <div key={backup.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {backup.status === 'completed' ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : backup.status === 'failed' ? (
                        <AlertCircle className="h-5 w-5 text-red-600" />
                      ) : (
                        <Clock className="h-5 w-5 text-yellow-600" />
                      )}
                      <div>
                        <p className="font-medium">{backup.name}</p>
                        <p className="text-sm text-gray-600">
                          {new Date(backup.created_at).toLocaleString()} • {backup.size}
                        </p>
                      </div>
                    </div>
                    <Badge variant="outline">{backup.type}</Badge>
                    <Badge 
                      variant={
                        backup.status === 'completed' ? 'default' : 
                        backup.status === 'failed' ? 'destructive' : 'secondary'
                      }
                    >
                      {backup.status}
                    </Badge>
                  </div>
                  <div className="flex space-x-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => downloadBackup(backup.id, backup.name)}
                      disabled={backup.status !== 'completed'}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => restoreBackup(backup.id)}
                      disabled={backup.status !== 'completed'}
                    >
                      <Upload className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
