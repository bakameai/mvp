
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { StatusSelector } from './StatusSelector';
import { getStatusColor, formatDate } from './utils';

interface ContactSubmission {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  company: string | null;
  subject: string | null;
  message: string;
  solution_type: string | null;
  status: string | null;
  created_at: string;
}

interface ContactSubmissionCardProps {
  submission: ContactSubmission;
  onStatusUpdate: (id: string, newStatus: string) => void;
  isUpdating: boolean;
}

export const ContactSubmissionCard = ({ 
  submission, 
  onStatusUpdate, 
  isUpdating 
}: ContactSubmissionCardProps) => {
  const handleStatusChange = (newStatus: string) => {
    onStatusUpdate(submission.id, newStatus);
  };

  const handleReplyClick = () => {
    window.open(`mailto:${submission.email}?subject=Re: ${submission.subject || 'Your inquiry'}`);
  };

  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-4">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{submission.name}</CardTitle>
            <p className="text-sm text-gray-600 mt-1">
              {submission.company && `${submission.company} • `}{submission.email}
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Badge className={`${getStatusColor(submission.status)} text-white`}>
              {(submission.status || 'new').replace('_', ' ').toUpperCase()}
            </Badge>
            <p className="text-xs text-gray-500">
              {formatDate(submission.created_at)}
            </p>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <strong>Phone:</strong> {submission.phone || 'Not provided'}
          </div>
          <div>
            <strong>Solution Interest:</strong> {submission.solution_type || 'General'}
          </div>
          {submission.subject && (
            <div className="md:col-span-2">
              <strong>Subject:</strong> {submission.subject}
            </div>
          )}
        </div>

        <div>
          <strong className="text-sm">Message:</strong>
          <p className="text-sm text-gray-600 mt-1 bg-gray-50 p-3 rounded">
            {submission.message}
          </p>
        </div>

        <div className="flex justify-between items-center pt-4 border-t">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Status:</span>
            <StatusSelector
              status={submission.status}
              onStatusChange={handleStatusChange}
              disabled={isUpdating}
            />
          </div>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleReplyClick}
          >
            Reply
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
