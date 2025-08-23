
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { UserProfile } from "@/pages/AdminDashboard";
import { Mail, Calendar, MapPin } from "lucide-react";

interface TeamProps {
  userProfile: UserProfile;
}

// Updated team data based on the provided reference
const teamMembers = [
  {
    id: "1",
    name: "Happy Herman",
    role: "CEO",
    email: "happy@bakame.ai",
    joinDate: "2023-01-15",
    location: "Rwanda",
    status: "active",
    avatar: "HH",
    description: "Ex. Rwandan Civics Ambassador to Qatar, Economics + Finance Double Degree at TCU"
  },
  {
    id: "2",
    name: "Aime Byiringiro",
    role: "CTO",
    email: "aime@bakame.ai",
    joinDate: "2023-01-15",
    location: "Rwanda",
    status: "active",
    avatar: "AB",
    description: "Software Engineer at Dell"
  },
  {
    id: "3",
    name: "Chretien Igiraneza",
    role: "GRAPHIC DESIGNER",
    email: "chretien@bakame.ai",
    joinDate: "2023-02-01",
    location: "Rwanda",
    status: "active",
    avatar: "CI",
    description: "CEO, Co-founder of KORIKORI CREATIVE AGENCY"
  }
];

const advisors = [
  {
    id: "4",
    name: "Twagirayezu Gaspard",
    role: "ADVISOR (STRATEGY)",
    email: "gaspard@bakame.ai",
    joinDate: "2023-03-01",
    location: "Rwanda",
    status: "advisor",
    avatar: "TG",
    description: "CEO of Rwanda Space Agency and Former Minister of Education"
  },
  {
    id: "5",
    name: "Natasha Harris",
    role: "ADVISOR (VENTURES)",
    email: "natasha@bakame.ai",
    joinDate: "2023-03-01",
    location: "USA",
    status: "advisor",
    avatar: "NH",
    description: "Principle of Biegert Group, Inc. and Chairperson of Hope Haven"
  },
  {
    id: "6",
    name: "J. Dr. Jean Pierre",
    role: "ADVISOR (COMPLIANCY)",
    email: "jeanpierre@bakame.ai",
    joinDate: "2023-03-01",
    location: "Rwanda",
    status: "advisor",
    avatar: "JP",
    description: "President of the High Court of the Republic of Rwanda, and Chair of the AU Constitutional Steering Committee"
  }
];

export const Team = ({ userProfile }: TeamProps) => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Team</h1>
        <p className="text-gray-600 mt-2">
          We've built civic, cloud, and scalable systems
        </p>
      </div>

      {/* Team Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Core Team</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{teamMembers.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Advisors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{advisors.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Funding Round</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$100K</div>
            <p className="text-xs text-muted-foreground">Seed Round</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Founded</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">June 2025</div>
          </CardContent>
        </Card>
      </div>

      {/* Core Team Members */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Leadership Team</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {teamMembers.map((member) => (
            <Card key={member.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4 mb-4">
                  <Avatar className="h-16 w-16">
                    <AvatarFallback className="bg-blue-500 text-white font-semibold text-lg">
                      {member.avatar}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-lg">{member.name}</h3>
                    <p className="text-sm font-medium text-blue-600 uppercase tracking-wide">{member.role}</p>
                    <Badge 
                      variant="default"
                      className="bg-green-100 text-green-800 mt-1"
                    >
                      {member.status}
                    </Badge>
                  </div>
                </div>

                <p className="text-sm text-gray-600 mb-4">{member.description}</p>

                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <Mail className="h-4 w-4" />
                    <span>{member.email}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4" />
                    <span>Joined {new Date(member.joinDate).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4" />
                    <span>{member.location}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Advisory Board */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Advisory Board</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {advisors.map((advisor) => (
            <Card key={advisor.id} className="hover:shadow-md transition-shadow border-orange-200">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4 mb-4">
                  <Avatar className="h-16 w-16">
                    <AvatarFallback className="bg-orange-500 text-white font-semibold text-lg">
                      {advisor.avatar}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-lg">{advisor.name}</h3>
                    <p className="text-sm font-medium text-orange-600 uppercase tracking-wide">{advisor.role}</p>
                    <Badge 
                      variant="secondary"
                      className="bg-orange-100 text-orange-800 mt-1"
                    >
                      {advisor.status}
                    </Badge>
                  </div>
                </div>

                <p className="text-sm text-gray-600 mb-4">{advisor.description}</p>

                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-2">
                    <Mail className="h-4 w-4" />
                    <span>{advisor.email}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4" />
                    <span>Joined {new Date(advisor.joinDate).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4" />
                    <span>{advisor.location}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
