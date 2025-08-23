
import { useMemo } from "react";
import { Resource } from "@/hooks/useResources";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Download, Star, FileText, Zap } from "lucide-react";

interface ResourceStatsProps {
  resources: Resource[];
  filteredResources: Resource[];
}

export const ResourceStats = ({ resources, filteredResources }: ResourceStatsProps) => {
  const stats = useMemo(() => {
    const totalDownloads = resources.reduce((sum, resource) => sum + (resource.download_count || 0), 0);
    const featuredCount = resources.filter(r => r.is_featured).length;
    const categoryCount = new Set(resources.map(r => r.category)).size;
    const averageDownloads = Math.round(totalDownloads / resources.length) || 0;

    return {
      totalDownloads,
      featuredCount,
      categoryCount,
      averageDownloads
    };
  }, [resources]);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
        <CardContent className="p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            <FileText className="h-5 w-5 text-blue-400 mr-2" />
            <Badge variant="outline" className="border-blue-500/30 text-blue-300">
              {filteredResources.length}
            </Badge>
          </div>
          <p className="text-xs text-white/70">Resources Shown</p>
        </CardContent>
      </Card>

      <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
        <CardContent className="p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            <Download className="h-5 w-5 text-green-400 mr-2" />
            <Badge variant="outline" className="border-green-500/30 text-green-300">
              {stats.totalDownloads.toLocaleString()}
            </Badge>
          </div>
          <p className="text-xs text-white/70">Total Downloads</p>
        </CardContent>
      </Card>

      <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
        <CardContent className="p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            <Star className="h-5 w-5 text-yellow-400 mr-2" />
            <Badge variant="outline" className="border-yellow-500/30 text-yellow-300">
              {stats.featuredCount}
            </Badge>
          </div>
          <p className="text-xs text-white/70">Featured</p>
        </CardContent>
      </Card>

      <Card className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
        <CardContent className="p-4 text-center">
          <div className="flex items-center justify-center mb-2">
            <Zap className="h-5 w-5 text-purple-400 mr-2" />
            <Badge variant="outline" className="border-purple-500/30 text-purple-300">
              {stats.averageDownloads}
            </Badge>
          </div>
          <p className="text-xs text-white/70">Avg Downloads</p>
        </CardContent>
      </Card>
    </div>
  );
};
