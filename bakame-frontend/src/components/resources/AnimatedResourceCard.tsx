
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, ExternalLink, FileText, Video, Headphones, Eye, EyeOff, Star } from "lucide-react";
import { Resource } from "@/hooks/useResources";

interface AnimatedResourceCardProps {
  resource: Resource;
  onDownload: (resourceId: string) => void;
  index: number;
}

export const AnimatedResourceCard = ({ resource, onDownload, index }: AnimatedResourceCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const getIconForType = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf": return FileText;
      case "mp3": return Headphones;
      case "mp4": return Video;
      case "zip": return Download;
      default: return FileText;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf": return "bg-red-500/20 text-red-300 border-red-500/30";
      case "mp3": return "bg-purple-500/20 text-purple-300 border-purple-500/30";
      case "mp4": return "bg-blue-500/20 text-blue-300 border-blue-500/30";
      case "zip": return "bg-green-500/20 text-green-300 border-green-500/30";
      default: return "bg-gray-500/20 text-gray-300 border-gray-500/30";
    }
  };

  const ResourceIcon = getIconForType(resource.type);

  const getFileSize = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf": return "2.5 MB";
      case "mp3": return "8.2 MB";
      case "mp4": return "125 MB";
      case "zip": return "45 MB";
      default: return "1.2 MB";
    }
  };

  return (
    <Card 
      className={`bg-white/5 border-white/10 backdrop-blur-sm transition-all duration-500 group cursor-pointer relative overflow-hidden animate-fadeInUp
        ${isHovered ? 'bg-white/10 scale-105 shadow-2xl border-blue-500/30' : ''}
        ${isExpanded ? 'row-span-2' : ''}
      `}
      style={{
        animationDelay: `${index * 100}ms`,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Animated background gradient */}
      <div className={`absolute inset-0 opacity-0 transition-opacity duration-500 ${isHovered ? 'opacity-20' : ''}`}>
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20 animate-pulse"></div>
      </div>
      
      {resource.is_featured && (
        <div className="absolute top-2 right-2 z-10">
          <Star className="h-4 w-4 text-yellow-400 fill-yellow-400 animate-pulse" />
        </div>
      )}
      
      <CardHeader className="relative z-10 pb-4">
        <div className="flex items-center justify-between mb-2">
          <ResourceIcon className={`h-5 w-5 transition-colors duration-300 ${isHovered ? 'text-blue-300' : 'text-blue-400'}`} />
          <div className="flex items-center space-x-2">
            <Badge className={`${getTypeColor(resource.type)} border transition-all duration-300`}>
              {resource.type}
            </Badge>
            <span className="text-xs text-white/50">{getFileSize(resource.type)}</span>
          </div>
        </div>
        <CardTitle className={`text-lg transition-colors duration-300 ${isHovered ? 'text-blue-300' : 'text-white'}`}>
          {resource.title}
        </CardTitle>
        <CardDescription className={`text-white/70 transition-all duration-300 ${isExpanded ? '' : 'line-clamp-2'}`}>
          {resource.description}
        </CardDescription>
        
        {resource.tags && resource.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {(isExpanded ? resource.tags : resource.tags.slice(0, 3)).map((tag, tagIndex) => (
              <Badge 
                key={tagIndex} 
                variant="outline" 
                className={`text-xs border-white/20 text-white/60 transition-all duration-300 hover:bg-white/10 hover:border-blue-500/30
                  ${isHovered ? 'border-blue-500/30' : ''}
                `}
                style={{
                  animationDelay: `${tagIndex * 50}ms`,
                }}
              >
                {tag}
              </Badge>
            ))}
            {!isExpanded && resource.tags.length > 3 && (
              <Badge variant="outline" className="text-xs border-white/20 text-white/60">
                +{resource.tags.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardHeader>
      
      <CardContent className="relative z-10 pt-0">
        <div className="flex flex-col space-y-3">
          <div className="flex items-center justify-between">
            <Button 
              size="sm" 
              variant="outline" 
              className={`
                border-white/30 text-white bg-white/5 hover:bg-blue-500/20 hover:border-blue-400/50
                transition-all duration-300 transform backdrop-blur-sm
                ${isHovered ? 'scale-105 shadow-lg border-blue-400/40 bg-blue-500/10' : ''}
              `}
              onClick={(e) => {
                e.stopPropagation();
                onDownload(resource.id);
              }}
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <span className="text-xs text-white/50 transition-colors duration-300">
              {resource.download_count} downloads
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className="text-white/40 hover:text-blue-400 hover:bg-white/10 transition-colors"
            >
              {isExpanded ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
              {isExpanded ? 'Less' : 'More'}
            </Button>
            <ExternalLink className={`h-4 w-4 transition-colors duration-300 ${isHovered ? 'text-blue-400' : 'text-white/40'}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
