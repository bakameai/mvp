
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Mail, Linkedin, Twitter, MapPin, Calendar } from "lucide-react";

interface TeamMember {
  name: string;
  title: string;
  bio: string;
  image: string;
  department: string;
  joinDate: string;
  location: string;
  email: string;
  linkedin?: string;
  twitter?: string;
  skills: string[];
  achievements: string[];
  fullBio: string;
}

interface TeamMemberCardProps {
  member: TeamMember;
  index: number;
}

export const TeamMemberCard = ({ member, index }: TeamMemberCardProps) => {
  const [isHovered, setIsHovered] = useState(false);

  const getDepartmentColor = (department: string) => {
    const colors = {
      "Executive": "from-purple-500 to-pink-500",
      "Technology": "from-blue-500 to-cyan-500",
      "Research": "from-green-500 to-emerald-500",
      "Engineering": "from-orange-500 to-red-500",
      "Operations": "from-indigo-500 to-purple-500",
      "Partnerships": "from-yellow-500 to-orange-500"
    };
    return colors[department as keyof typeof colors] || "from-gray-500 to-gray-600";
  };

  return (
    <div
      className={`group transform transition-all duration-500 hover:scale-105 hover:-translate-y-2 ${
        isHovered ? "z-10" : ""
      }`}
      style={{
        animationDelay: `${index * 150}ms`,
        animation: "fadeInUp 0.6s ease-out forwards"
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Card className="relative bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-all duration-300 overflow-hidden h-full">
        {/* Animated gradient border */}
        <div className={`absolute inset-0 bg-gradient-to-r ${getDepartmentColor(member.department)} opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-2xl`} />
        
        {/* Floating particles effect */}
        <div className="absolute inset-0 overflow-hidden rounded-2xl">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className={`absolute w-1 h-1 bg-white/30 rounded-full animate-pulse opacity-0 group-hover:opacity-100 transition-opacity duration-1000`}
              style={{
                top: `${20 + i * 30}%`,
                left: `${10 + i * 25}%`,
                animationDelay: `${i * 0.5}s`
              }}
            />
          ))}
        </div>

        <CardContent className="p-6 relative z-10">
          <div className="mb-6">
            <div className="w-24 h-24 mx-auto mb-4 rounded-full overflow-hidden border-2 border-white/20 group-hover:border-white/40 transition-all duration-300 relative">
              <img
                src={member.image}
                alt={member.name}
                className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500 group-hover:scale-110"
              />
              {/* Hover overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
            
            <div className="text-center">
              <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-blue-200 transition-all duration-300">
                {member.name}
              </h3>
              <Badge className={`bg-gradient-to-r ${getDepartmentColor(member.department)} text-white border-0 mb-2`}>
                {member.title}
              </Badge>
              <p className="text-sm text-blue-400 font-medium mb-2">{member.department}</p>
            </div>
          </div>

          <p className="text-white/70 text-sm leading-relaxed text-center mb-4 line-clamp-3">
            {member.bio}
          </p>

          {/* Skills preview */}
          <div className="flex flex-wrap gap-1 justify-center mb-4 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
            {member.skills.slice(0, 3).map((skill, idx) => (
              <Badge key={idx} variant="secondary" className="text-xs bg-white/10 text-white/80 border-white/20">
                {skill}
              </Badge>
            ))}
          </div>

          {/* Social links */}
          <div className="flex justify-center space-x-3 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-4 group-hover:translate-y-0">
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0 text-white/60 hover:text-white hover:bg-white/10"
              asChild
            >
              <a href={`mailto:${member.email}`}>
                <Mail className="h-4 w-4" />
              </a>
            </Button>
            {member.linkedin && (
              <Button
                size="sm"
                variant="ghost"
                className="h-8 w-8 p-0 text-white/60 hover:text-white hover:bg-white/10"
                asChild
              >
                <a href={member.linkedin} target="_blank" rel="noopener noreferrer">
                  <Linkedin className="h-4 w-4" />
                </a>
              </Button>
            )}
            {member.twitter && (
              <Button
                size="sm"
                variant="ghost"
                className="h-8 w-8 p-0 text-white/60 hover:text-white hover:bg-white/10"
                asChild
              >
                <a href={member.twitter} target="_blank" rel="noopener noreferrer">
                  <Twitter className="h-4 w-4" />
                </a>
              </Button>
            )}
          </div>

          {/* Expandable modal */}
          <Dialog>
            <DialogTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="w-full mt-4 bg-white/5 border-white/20 text-white hover:bg-white/10 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-4 group-hover:translate-y-0"
              >
                Learn More
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl bg-gray-900 border-gray-700 text-white">
              <DialogHeader>
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-16 h-16 rounded-full overflow-hidden border-2 border-white/20">
                    <img
                      src={member.image}
                      alt={member.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <DialogTitle className="text-2xl font-bold text-white mb-1">
                      {member.name}
                    </DialogTitle>
                    <p className="text-blue-400 font-medium">{member.title}</p>
                    <Badge className={`bg-gradient-to-r ${getDepartmentColor(member.department)} text-white border-0 mt-1`}>
                      {member.department}
                    </Badge>
                  </div>
                </div>
              </DialogHeader>
              
              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-semibold mb-2 text-white">About</h4>
                  <p className="text-white/80 leading-relaxed">{member.fullBio}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center text-white/70">
                      <MapPin className="h-4 w-4 mr-2" />
                      <span>{member.location}</span>
                    </div>
                    <div className="flex items-center text-white/70">
                      <Calendar className="h-4 w-4 mr-2" />
                      <span>Joined {member.joinDate}</span>
                    </div>
                    <div className="flex items-center text-white/70">
                      <Mail className="h-4 w-4 mr-2" />
                      <span>{member.email}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-lg font-semibold mb-3 text-white">Expertise</h4>
                  <div className="flex flex-wrap gap-2">
                    {member.skills.map((skill, idx) => (
                      <Badge key={idx} variant="secondary" className="bg-white/10 text-white border-white/20">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-lg font-semibold mb-3 text-white">Key Achievements</h4>
                  <ul className="space-y-2">
                    {member.achievements.map((achievement, idx) => (
                      <li key={idx} className="text-white/80 flex items-start">
                        <span className="text-blue-400 mr-2">•</span>
                        {achievement}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>
    </div>
  );
};
