
import { useState, useEffect } from 'react';
import { authAPI } from '@/services/api';
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
      // Get page views
      const { data: pageViews, error: pageViewsError } = await supabase
        .from('analytics')
        .select('*')
        .eq('event_type', 'page_view');

      // Get all sessions
      const { data: sessions = [], error: sessionsError } = await supabase
        .from('user_sessions')
        .select('*');

      if (sessionsError) {
        console.warn('Error fetching user sessions:', sessionsError);
      }

      // Get recent events
      const { data: events, error: eventsError } = await supabase
        .from('analytics')
        .select('event_type')
        .neq('event_type', 'page_view')
        .order('created_at', { ascending: false })
        .limit(100);

      if (pageViewsError || eventsError) {
        console.error('Error fetching analytics:', { pageViewsError, eventsError });
      } else {
        // Process page views data
        const uniqueVisitors = new Set(pageViews?.map(pv => pv.session_id)).size;
        const pageViewCounts = pageViews?.reduce((acc: Record<string, number>, pv) => {
          acc[pv.page_path] = (acc[pv.page_path] || 0) + 1;
          return acc;
        }, {}) || {};

        const topPages = Object.entries(pageViewCounts)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 5)
          .map(([page, views]) => ({ page, views }));

        // Process events data
        const eventCounts = events?.reduce((acc: Record<string, number>, event) => {
          acc[event.event_type] = (acc[event.event_type] || 0) + 1;
          return acc;
        }, {}) || {};

        const recentEvents = Object.entries(eventCounts)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 5)
          .map(([event_type, count]) => ({ event_type, count }));

        // Calculate average pages per session with fallback
        const totalPagesViewed = sessions.length > 0 
          ? sessions.reduce((acc: number, session: any) => acc + (session.pages_visited || 1), 0)
          : pageViews?.length || 0;
        const avgPagesPerSession = sessions.length 
          ? Math.round(totalPagesViewed / sessions.length * 10) / 10 
          : 1;

        setAnalytics({
          totalPageViews: pageViews?.length || 0,
          uniqueVisitors,
          totalSessions: sessions.length || uniqueVisitors,
          avgPagesPerSession,
          topPages,
          recentEvents
        });
      }
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
