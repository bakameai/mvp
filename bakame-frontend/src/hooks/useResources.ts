
import { useState, useEffect } from 'react';
import { authAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

export interface Resource {
  id: string;
  title: string;
  description: string;
  type: string;
  category: string;
  file_url?: string;
  external_url?: string;
  download_count: number;
  is_featured: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export const useResources = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchResources = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('resources')
        .select('*')
        .order('is_featured', { ascending: false })
        .order('created_at', { ascending: false });

      if (error) throw error;
      setResources(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch resources');
      toast({
        title: "Error",
        description: "Failed to load resources",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadResource = async (resourceId: string) => {
    try {
      // Update download count by fetching current count and incrementing
      const { data: currentResource, error: fetchError } = await supabase
        .from('resources')
        .select('download_count')
        .eq('id', resourceId)
        .single();

      if (fetchError) throw fetchError;

      const newCount = (currentResource?.download_count || 0) + 1;
      
      const { error } = await supabase
        .from('resources')
        .update({ download_count: newCount })
        .eq('id', resourceId);

      if (error) throw error;

      // Refresh resources to show updated count
      fetchResources();

      toast({
        title: "Download Started",
        description: "Your download will begin shortly",
      });
    } catch (err) {
      toast({
        title: "Download Failed",
        description: "Failed to start download",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchResources();
  }, []);

  return {
    resources,
    loading,
    error,
    downloadResource,
    refetch: fetchResources
  };
};
