
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Search, X, SortAsc } from "lucide-react";

interface ResourceFiltersProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  selectedCategory: string;
  onCategoryChange: (value: string) => void;
  selectedType: string;
  onTypeChange: (value: string) => void;
  selectedTags: string[];
  onTagToggle: (tag: string) => void;
  availableCategories: string[];
  availableTypes: string[];
  availableTags: string[];
  onClearFilters: () => void;
  sortBy: "newest" | "oldest" | "popular" | "featured";
  onSortChange: (value: "newest" | "oldest" | "popular" | "featured") => void;
}

export const ResourceFilters = ({
  searchTerm,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  selectedType,
  onTypeChange,
  selectedTags,
  onTagToggle,
  availableCategories,
  availableTypes,
  availableTags,
  onClearFilters,
  sortBy,
  onSortChange
}: ResourceFiltersProps) => {
  const hasActiveFilters = searchTerm || selectedCategory !== 'all' || selectedType !== 'all' || selectedTags.length > 0;

  return (
    <div className="space-y-4 mb-8">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/50" />
        <Input
          placeholder="Search resources..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10 bg-white/5 border-white/10 text-white placeholder:text-white/50 transition-all duration-300 focus:bg-white/10 focus:border-blue-500/30"
        />
      </div>

      <div className="flex flex-wrap gap-4">
        <Select value={selectedCategory} onValueChange={onCategoryChange}>
          <SelectTrigger className="w-48 bg-white/5 border-white/10 text-white hover:bg-white/10 transition-all duration-300">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent className="bg-gray-900 border-white/10">
            <SelectItem value="all">All Categories</SelectItem>
            {availableCategories.map(category => (
              <SelectItem key={category} value={category} className="text-white hover:bg-white/10">
                {category}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={selectedType} onValueChange={onTypeChange}>
          <SelectTrigger className="w-48 bg-white/5 border-white/10 text-white hover:bg-white/10 transition-all duration-300">
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent className="bg-gray-900 border-white/10">
            <SelectItem value="all">All Types</SelectItem>
            {availableTypes.map(type => (
              <SelectItem key={type} value={type} className="text-white hover:bg-white/10">
                {type}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={sortBy} onValueChange={onSortChange}>
          <SelectTrigger className="w-48 bg-white/5 border-white/10 text-white hover:bg-white/10 transition-all duration-300">
            <SortAsc className="h-4 w-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-gray-900 border-white/10">
            <SelectItem value="featured" className="text-white hover:bg-white/10">Featured First</SelectItem>
            <SelectItem value="popular" className="text-white hover:bg-white/10">Most Popular</SelectItem>
            <SelectItem value="newest" className="text-white hover:bg-white/10">Newest First</SelectItem>
            <SelectItem value="oldest" className="text-white hover:bg-white/10">Oldest First</SelectItem>
          </SelectContent>
        </Select>

        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="flex items-center px-3 py-2 text-sm text-white/70 hover:text-white transition-colors hover:bg-white/10 rounded border border-white/20"
          >
            <X className="h-4 w-4 mr-1" />
            Clear Filters
          </button>
        )}
      </div>

      {availableTags.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-white/70">Tags</h4>
          <div className="flex flex-wrap gap-2">
            {availableTags.map(tag => (
              <Badge
                key={tag}
                variant={selectedTags.includes(tag) ? "default" : "outline"}
                className={`cursor-pointer transition-all duration-300 transform hover:scale-105 ${
                  selectedTags.includes(tag)
                    ? "bg-blue-500 text-white hover:bg-blue-600"
                    : "border-white/20 text-white/70 hover:bg-white/10 hover:border-blue-500/30"
                }`}
                onClick={() => onTagToggle(tag)}
              >
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
