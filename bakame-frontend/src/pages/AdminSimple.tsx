import React, { useState, useEffect } from 'react';
import { Phone, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface CallLog {
  call_sid: string;
  from_number: string;
  message: string;
  ai_response: string;
  timestamp: string;
}

const AdminSimple = () => {
  const [calls, setCalls] = useState<CallLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'unknown' | 'healthy' | 'error'>('unknown');

  const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.hostname.replace('-00-', '-01-')}:8000`;

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      if (response.ok) {
        setBackendStatus('healthy');
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      setBackendStatus('error');
    }
  };

  const fetchCalls = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/calls`);
      const data = await response.json();
      setCalls(data.calls || []);
    } catch (error) {
      console.error('Failed to fetch calls:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkBackendHealth();
    fetchCalls();
    const interval = setInterval(fetchCalls, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
              Bakame AI Admin
            </h1>
            <p className="text-muted-foreground mt-2">Monitor voice call interactions</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant={backendStatus === 'healthy' ? 'default' : 'destructive'}>
              {backendStatus === 'healthy' ? (
                <>
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Backend Online
                </>
              ) : (
                <>
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Backend Offline
                </>
              )}
            </Badge>
            <Button onClick={fetchCalls} disabled={loading} size="sm">
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        <div className="grid gap-6 mb-8 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Calls</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{calls.length}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Unique Callers</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {new Set(calls.map(c => c.from_number).filter(Boolean)).size}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">AI Responses</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {calls.filter(c => c.ai_response).length}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent Calls</CardTitle>
            <CardDescription>All voice call interactions with Bakame AI</CardDescription>
          </CardHeader>
          <CardContent>
            {calls.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Phone className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No calls yet. Make your first test call!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {calls.slice().reverse().map((call, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4 text-primary" />
                        <span className="font-mono text-sm">{call.from_number || 'Unknown'}</span>
                      </div>
                      <Badge variant="outline">{call.timestamp || 'Just now'}</Badge>
                    </div>
                    
                    {call.message && (
                      <div className="bg-muted/50 rounded p-3">
                        <p className="text-sm font-medium mb-1">User:</p>
                        <p className="text-sm">{call.message}</p>
                      </div>
                    )}
                    
                    {call.ai_response && (
                      <div className="bg-primary/10 rounded p-3">
                        <p className="text-sm font-medium mb-1">AI Response:</p>
                        <p className="text-sm">{call.ai_response}</p>
                      </div>
                    )}
                    
                    {call.call_sid && (
                      <p className="text-xs text-muted-foreground font-mono">
                        Call ID: {call.call_sid}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminSimple;
