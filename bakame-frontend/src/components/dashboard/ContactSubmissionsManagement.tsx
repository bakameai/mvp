
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { ContactSubmissionCard } from './contact-submissions/ContactSubmissionCard';
import { useContactSubmissions } from '@/hooks/useContactSubmissions';
import { UserProfile } from '@/pages/AdminDashboard';

interface ContactSubmissionsManagementProps {
  userProfile: UserProfile;
}

export const ContactSubmissionsManagement = ({ userProfile }: ContactSubmissionsManagementProps) => {
  const { submissions, loading, updating, updateStatus } = useContactSubmissions();

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
        <h2 className="text-2xl font-bold">Contact Submissions</h2>
        <Badge variant="outline" className="text-sm">
          {submissions.length} Total Submissions
        </Badge>
      </div>

      <div className="grid gap-6">
        {submissions.map((submission) => (
          <ContactSubmissionCard
            key={submission.id}
            submission={submission}
            onStatusUpdate={updateStatus}
            isUpdating={updating === submission.id}
          />
        ))}

        {submissions.length === 0 && (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-gray-600">No contact submissions found.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
