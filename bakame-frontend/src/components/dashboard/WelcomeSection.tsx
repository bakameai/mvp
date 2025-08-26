import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function WelcomeSection() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Welcome to Bakame AI Learning Platform</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground leading-relaxed">
          Manage your offline AI-powered English learning system for schools and track student progress across all partner institutions.
        </p>
        <ul className="mt-4 space-y-2 text-sm">
          <li className="flex items-center gap-2 text-muted-foreground">
            <div className="w-2 h-2 bg-stat-blue rounded-full"></div>
            Monitor student speaking confidence and progress
          </li>
          <li className="flex items-center gap-2 text-muted-foreground">
            <div className="w-2 h-2 bg-stat-green rounded-full"></div>
            Manage partner schools and teacher accounts
          </li>
          <li className="flex items-center gap-2 text-muted-foreground">
            <div className="w-2 h-2 bg-stat-purple rounded-full"></div>
            Configure IVR system and offline lesson content
          </li>
        </ul>
      </CardContent>
    </Card>
  );
}
