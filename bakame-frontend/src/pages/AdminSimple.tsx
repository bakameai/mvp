import React, { useState, useEffect } from 'react';
import { Phone, RefreshCw, CheckCircle, AlertCircle, DollarSign, MessageSquare, Clock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface CallLog {
  call_sid: string;
  from_number: string;
  message: string;
  ai_response: string;
  timestamp: string;
  event_type: string;
}

interface OpenAILog {
  call_sid: string;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  request_type: string;
  timestamp: string;
}

interface TwilioCall {
  call_sid: string;
  from_number: string;
  to_number: string;
  call_status: string;
  direction: string;
  from_city: string;
  from_state: string;
  from_country: string;
  start_time: string;
  end_time?: string;
  interactions: number;
}

interface DashboardStats {
  calls: {
    total: number;
    unique_callers: number;
    conversations: number;
    active_sessions: number;
  };
  openai: {
    total_requests: number;
    total_tokens: number;
    estimated_cost: number;
  };
  twilio: {
    total_calls: number;
    completed_calls: number;
  };
}

const AdminSimple = () => {
  const [calls, setCalls] = useState<CallLog[]>([]);
  const [openaiLogs, setOpenaiLogs] = useState<OpenAILog[]>([]);
  const [twilioCall, setTwilioCalls] = useState<TwilioCall[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'unknown' | 'healthy' | 'error'>('unknown');

  const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.hostname}:8000`;

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

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [callsRes, openaiRes, twilioRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/calls`),
        fetch(`${API_BASE}/api/openai-usage`),
        fetch(`${API_BASE}/api/twilio-calls`),
        fetch(`${API_BASE}/api/dashboard-stats`)
      ]);

      const callsData = await callsRes.json();
      const openaiData = await openaiRes.json();
      const twilioData = await twilioRes.json();
      const statsData = await statsRes.json();

      setCalls(callsData.calls || []);
      setOpenaiLogs(openaiData.logs || []);
      setTwilioCalls(twilioData.calls || []);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkBackendHealth();
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const conversationLogs = calls.filter(c => c.event_type === 'conversation');

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
              Bakame AI Admin Dashboard
            </h1>
            <p className="text-muted-foreground mt-2">Comprehensive monitoring and analytics</p>
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
            <Button onClick={fetchAllData} disabled={loading} size="sm">
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {stats && (
          <div className="grid gap-6 mb-8 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  Total Calls
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.twilio.total_calls}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stats.calls.unique_callers} unique callers
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  Conversations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.calls.conversations}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stats.calls.active_sessions} active sessions
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <DollarSign className="h-4 w-4" />
                  OpenAI Cost
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">${stats.openai.estimated_cost.toFixed(4)}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stats.openai.total_tokens.toLocaleString()} tokens
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  API Requests
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.openai.total_requests}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  GPT-4o interactions
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        <Tabs defaultValue="conversations" className="space-y-4">
          <TabsList>
            <TabsTrigger value="conversations">Conversations</TabsTrigger>
            <TabsTrigger value="twilio">Twilio Calls</TabsTrigger>
            <TabsTrigger value="openai">OpenAI Usage</TabsTrigger>
            <TabsTrigger value="all-logs">All Logs</TabsTrigger>
          </TabsList>

          <TabsContent value="conversations" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Conversation History</CardTitle>
                <CardDescription>User questions and AI responses</CardDescription>
              </CardHeader>
              <CardContent>
                {conversationLogs.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No conversations yet</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Time</TableHead>
                        <TableHead>Caller</TableHead>
                        <TableHead>User Message</TableHead>
                        <TableHead>AI Response</TableHead>
                        <TableHead>Call ID</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {conversationLogs.slice().reverse().map((log, idx) => (
                        <TableRow key={idx}>
                          <TableCell className="text-xs whitespace-nowrap">
                            {formatTimestamp(log.timestamp)}
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {log.from_number || 'Unknown'}
                          </TableCell>
                          <TableCell className="max-w-xs">
                            <div className="truncate" title={log.message}>
                              {log.message}
                            </div>
                          </TableCell>
                          <TableCell className="max-w-xs">
                            <div className="truncate" title={log.ai_response}>
                              {log.ai_response}
                            </div>
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {log.call_sid?.substring(0, 10)}...
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="twilio" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Twilio Call Details</CardTitle>
                <CardDescription>Complete call metadata from Twilio</CardDescription>
              </CardHeader>
              <CardContent>
                {twilioCall.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Phone className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No calls yet</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Call SID</TableHead>
                        <TableHead>From</TableHead>
                        <TableHead>Location</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Interactions</TableHead>
                        <TableHead>Start Time</TableHead>
                        <TableHead>End Time</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {twilioCall.slice().reverse().map((call, idx) => (
                        <TableRow key={idx}>
                          <TableCell className="font-mono text-xs">
                            {call.call_sid?.substring(0, 10)}...
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {call.from_number}
                          </TableCell>
                          <TableCell>
                            {call.from_city && call.from_state
                              ? `${call.from_city}, ${call.from_state}`
                              : call.from_country || 'Unknown'}
                          </TableCell>
                          <TableCell>
                            <Badge variant={call.call_status === 'completed' ? 'default' : 'secondary'}>
                              {call.call_status}
                            </Badge>
                          </TableCell>
                          <TableCell>{call.interactions}</TableCell>
                          <TableCell className="text-xs whitespace-nowrap">
                            {formatTimestamp(call.start_time)}
                          </TableCell>
                          <TableCell className="text-xs whitespace-nowrap">
                            {call.end_time ? formatTimestamp(call.end_time) : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="openai" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>OpenAI API Usage</CardTitle>
                <CardDescription>Token usage and cost tracking</CardDescription>
              </CardHeader>
              <CardContent>
                {openaiLogs.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <DollarSign className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No API usage yet</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Time</TableHead>
                        <TableHead>Model</TableHead>
                        <TableHead>Request Type</TableHead>
                        <TableHead>Prompt Tokens</TableHead>
                        <TableHead>Completion Tokens</TableHead>
                        <TableHead>Total Tokens</TableHead>
                        <TableHead>Cost (USD)</TableHead>
                        <TableHead>Call ID</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {openaiLogs.slice().reverse().map((log, idx) => (
                        <TableRow key={idx}>
                          <TableCell className="text-xs whitespace-nowrap">
                            {formatTimestamp(log.timestamp)}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{log.model}</Badge>
                          </TableCell>
                          <TableCell className="capitalize">
                            {log.request_type.replace(/_/g, ' ')}
                          </TableCell>
                          <TableCell>{log.prompt_tokens.toLocaleString()}</TableCell>
                          <TableCell>{log.completion_tokens.toLocaleString()}</TableCell>
                          <TableCell className="font-semibold">
                            {log.total_tokens.toLocaleString()}
                          </TableCell>
                          <TableCell className="text-green-600 font-mono">
                            ${log.estimated_cost.toFixed(6)}
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {log.call_sid?.substring(0, 10)}...
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="all-logs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>All System Logs</CardTitle>
                <CardDescription>Complete event log including system events</CardDescription>
              </CardHeader>
              <CardContent>
                {calls.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Phone className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No logs yet</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Time</TableHead>
                        <TableHead>Event Type</TableHead>
                        <TableHead>From</TableHead>
                        <TableHead>Message</TableHead>
                        <TableHead>AI Response</TableHead>
                        <TableHead>Call ID</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {calls.slice().reverse().map((log, idx) => (
                        <TableRow key={idx}>
                          <TableCell className="text-xs whitespace-nowrap">
                            {formatTimestamp(log.timestamp)}
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">{log.event_type}</Badge>
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {log.from_number || '-'}
                          </TableCell>
                          <TableCell className="max-w-xs">
                            <div className="truncate" title={log.message}>
                              {log.message || '-'}
                            </div>
                          </TableCell>
                          <TableCell className="max-w-xs">
                            <div className="truncate" title={log.ai_response}>
                              {log.ai_response || '-'}
                            </div>
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {log.call_sid?.substring(0, 10)}...
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminSimple;
