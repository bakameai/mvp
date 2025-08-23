
import { useState, useEffect } from 'react';
import { adminAPI } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { UserProfile } from '@/pages/AdminDashboard';

interface AnalyticsSummary {
  totalPageViews: number;
  uniqueVisitors: number;
  totalSessions: number;
  avgPagesPerSession: number;
  topPages: Array<{ page: string; views: number }>;
  recentEvents: Array<{ event_type: string; count: number }>;
}

interface AnalyticsDashboardProps {
  userProfile: UserProfile;
}

export const AnalyticsDashboard = ({ userProfile }: AnalyticsDashboardProps) => {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const data = await adminAPI.getAnalytics();
      
      setAnalytics({
        totalPageViews: data.total_page_views || 0,
        uniqueVisitors: data.unique_visitors || 0,
        totalSessions: data.total_sessions || 0,
        avgPagesPerSession: data.avg_pages_per_session || 0,
        topPages: data.top_pages || [],
        recentEvents: data.recent_events || []
      });
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (userProfile.role !== 'admin') {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Access denied. Admin privileges required.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Unable to load analytics data.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Analytics Dashboard</h2>

      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-blue-600">{analytics.totalPageViews}</div>
            <p className="text-sm text-gray-600">Total Page Views</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-green-600">{analytics.uniqueVisitors}</div>
            <p className="text-sm text-gray-600">Unique Visitors</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-purple-600">{analytics.totalSessions}</div>
            <p className="text-sm text-gray-600">Total Sessions</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-orange-600">{analytics.avgPagesPerSession}</div>
            <p className="text-sm text-gray-600">Avg Pages/Session</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Top Pages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analytics.topPages.map((page, index) => (
                <div key={page.page} className="flex justify-between items-center">
                  <span className="text-sm font-medium">
                    {index + 1}. {page.page === '/' ? 'Homepage' : page.page}
                  </span>
                  <span className="text-sm text-gray-600">{page.views} views</span>
                </div>
              ))}
              {analytics.topPages.length === 0 && (
                <p className="text-sm text-gray-600">No page data available</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analytics.recentEvents.map((event, index) => (
                <div key={event.event_type} className="flex justify-between items-center">
                  <span className="text-sm font-medium">
                    {index + 1}. {event.event_type.replace('_', ' ')}
                  </span>
                  <span className="text-sm text-gray-600">{event.count} times</span>
                </div>
              ))}
              {analytics.recentEvents.length === 0 && (
                <p className="text-sm text-gray-600">No event data available</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
