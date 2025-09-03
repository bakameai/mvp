import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UserProfile } from "@/pages/AdminDashboard";

interface ProfileCardProps {
  userProfile: UserProfile;
}

export function ProfileCard({ userProfile }: ProfileCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Your Profile</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="text-sm text-muted-foreground mb-1">Name</p>
          <p className="font-medium text-foreground">{userProfile.full_name || 'Not set'}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground mb-1">Email</p>
          <p className="font-medium text-foreground">{userProfile.email}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground mb-1">Role</p>
          <p className="font-medium text-foreground capitalize">{userProfile.role}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground mb-1">Organization</p>
          <p className="font-medium text-foreground">{userProfile.organization || 'BAKAME'}</p>
        </div>
      </CardContent>
    </Card>
  );
}
