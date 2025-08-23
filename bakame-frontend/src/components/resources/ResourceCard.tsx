
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, ExternalLink, FileText, Video, Headphones, Code, Star } from "lucide-react";
import { Resource } from "@/hooks/useResources";

interface ResourceCardProps {
  resource: Resource;
  onDownload: (resourceId: string) => void;
}

export const ResourceCard = ({ resource, onDownload }: ResourceCardProps) => {
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
      case "pdf": return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "mp3": return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200";
      case "mp4": return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "zip": return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      default: return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  const ResourceIcon = getIconForType(resource.type);

  // Simulate file size based on type for display
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
    <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300 group cursor-pointer relative">
      {resource.is_featured && (
        <div className="absolute top-2 right-2 z-10">
          <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
        </div>
      )}
      
      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <ResourceIcon className="h-5 w-5 text-blue-400" />
          <div className="flex items-center space-x-2">
            <Badge className={getTypeColor(resource.type)}>
              {resource.type}
            </Badge>
            <span className="text-xs text-white/50">{getFileSize(resource.type)}</span>
          </div>
        </div>
        <CardTitle className="text-lg text-white group-hover:text-blue-300 transition-colors">
          {resource.title}
        </CardTitle>
        <CardDescription className="text-white/70">
          {resource.description}
        </CardDescription>
        
        {resource.tags && resource.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {resource.tags.slice(0, 3).map((tag, index) => (
              <Badge key={index} variant="outline" className="text-xs border-white/20 text-white/60">
                {tag}
              </Badge>
            ))}
            {resource.tags.length > 3 && (
              <Badge variant="outline" className="text-xs border-white/20 text-white/60">
                +{resource.tags.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardHeader>
      
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button 
              size="sm" 
              variant="outline" 
              className="border-white/20 text-white hover:bg-white/10"
              onClick={() => onDownload(resource.id)}
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <span className="text-xs text-white/50">
              {resource.download_count} downloads
            </span>
          </div>
          <ExternalLink className="h-4 w-4 text-white/40 group-hover:text-blue-400 transition-colors" />
        </div>
      </CardContent>
    </Card>
  );
};
