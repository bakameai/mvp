import React, { useState, useEffect } from 'react';
import { Phone, RefreshCw, CheckCircle, AlertCircle, Download } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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

interface UnifiedRow {
  timestamp: string;
  call_sid: string;
  from_number: string;
  event_type: string;
  user_message: string;
  ai_response: string;
  call_status: string;
  location: string;
  interactions: number;
  openai_model: string;
  tokens_used: number;
  cost_usd: string;
}

const AdminSimple = () => {
  const [calls, setCalls] = useState<CallLog[]>([]);
  const [openaiLogs, setOpenaiLogs] = useState<OpenAILog[]>([]);
  const [twilioCalls, setTwilioCalls] = useState<TwilioCall[]>([]);
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
      const [callsRes, openaiRes, twilioRes] = await Promise.all([
        fetch(`${API_BASE}/api/calls`),
        fetch(`${API_BASE}/api/openai-usage`),
        fetch(`${API_BASE}/api/twilio-calls`)
      ]);

      const callsData = await callsRes.json();
      const openaiData = await openaiRes.json();
      const twilioData = await twilioRes.json();

      setCalls(callsData.calls || []);
      setOpenaiLogs(openaiData.logs || []);
      setTwilioCalls(twilioData.calls || []);
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

  const buildUnifiedData = (): UnifiedRow[] => {
    const rows = new Map<string, UnifiedRow>();
    
    const getOrCreateRow = (
      uniqueId: string,
      timestamp: string,
      callSid: string
    ): UnifiedRow => {
      if (!rows.has(uniqueId)) {
        rows.set(uniqueId, {
          timestamp,
          call_sid: callSid,
          from_number: '-',
          event_type: '-',
          user_message: '-',
          ai_response: '-',
          call_status: '-',
          location: '-',
          interactions: 0,
          openai_model: '-',
          tokens_used: 0,
          cost_usd: '-'
        });
      }
      return rows.get(uniqueId)!;
    };

    calls.forEach((call, idx) => {
      const uniqueId = `call-${call.call_sid}-${call.timestamp}-${idx}`;
      const row = getOrCreateRow(uniqueId, call.timestamp, call.call_sid);
      
      row.from_number = call.from_number || '-';
      row.event_type = call.event_type || '-';
      row.user_message = call.message || '-';
      row.ai_response = call.ai_response || '-';
      
      const twilioCall = twilioCalls.find(tc => tc.call_sid === call.call_sid);
      if (twilioCall) {
        row.call_status = twilioCall.call_status;
        row.location = `${twilioCall.from_city || ''} ${twilioCall.from_state || ''} ${twilioCall.from_country || ''}`.trim() || '-';
        row.interactions = twilioCall.interactions;
      }
    });

    openaiLogs.forEach((log, idx) => {
      const uniqueId = `openai-${log.call_sid}-${log.timestamp}-${idx}`;
      const row = getOrCreateRow(uniqueId, log.timestamp, log.call_sid);
      
      row.openai_model = log.model;
      row.tokens_used = log.total_tokens;
      row.cost_usd = `$${log.estimated_cost.toFixed(6)}`;
      row.event_type = row.event_type === '-' ? `openai_${log.request_type}` : row.event_type;
      
      const twilioCall = twilioCalls.find(tc => tc.call_sid === log.call_sid);
      if (twilioCall && row.from_number === '-') {
        row.from_number = twilioCall.from_number;
        row.call_status = twilioCall.call_status;
        row.location = `${twilioCall.from_city || ''} ${twilioCall.from_state || ''} ${twilioCall.from_country || ''}`.trim() || '-';
        row.interactions = twilioCall.interactions;
      }
    });

    twilioCalls.forEach((twilioCall, idx) => {
      const uniqueId = `twilio-${twilioCall.call_sid}-${twilioCall.start_time}-${idx}`;
      const row = getOrCreateRow(uniqueId, twilioCall.start_time, twilioCall.call_sid);
      
      row.from_number = twilioCall.from_number;
      row.call_status = twilioCall.call_status;
      row.event_type = 'twilio_call';
      row.location = `${twilioCall.from_city || ''} ${twilioCall.from_state || ''} ${twilioCall.from_country || ''}`.trim() || '-';
      row.interactions = twilioCall.interactions;
    });

    return Array.from(rows.values()).sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  };

  const downloadCSV = () => {
    const data = buildUnifiedData();
    
    if (data.length === 0) {
      alert('No data to download');
      return;
    }

    const headers = [
      'Timestamp',
      'Call SID',
      'Phone Number',
      'Event Type',
      'User Message',
      'AI Response',
      'Call Status',
      'Location',
      'Interactions',
      'OpenAI Model',
      'Tokens Used',
      'Cost (USD)'
    ];

    const escapeCSV = (value: string | number) => {
      const stringValue = String(value);
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      return stringValue;
    };

    const csvRows = [
      headers.join(','),
      ...data.map(row => [
        escapeCSV(formatTimestamp(row.timestamp)),
        escapeCSV(row.call_sid),
        escapeCSV(row.from_number),
        escapeCSV(row.event_type),
        escapeCSV(row.user_message),
        escapeCSV(row.ai_response),
        escapeCSV(row.call_status),
        escapeCSV(row.location),
        escapeCSV(row.interactions),
        escapeCSV(row.openai_model),
        escapeCSV(row.tokens_used),
        escapeCSV(row.cost_usd)
      ].join(','))
    ];

    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `bakame_ai_logs_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const unifiedData = buildUnifiedData();
  const totalCalls = twilioCalls.length;
  const uniqueCallers = new Set(calls.map(c => c.from_number).filter(Boolean)).size;
  const totalConversations = calls.filter(c => c.event_type === 'conversation').length;
  const totalTokens = openaiLogs.reduce((sum, log) => sum + log.total_tokens, 0);
  const totalCost = openaiLogs.reduce((sum, log) => sum + log.estimated_cost, 0);

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
              Bakame AI Admin Dashboard
            </h1>
            <p className="text-muted-foreground mt-2">Comprehensive call monitoring and analytics</p>
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
            <Button onClick={fetchAllData} disabled={loading} size="sm" variant="outline">
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button onClick={downloadCSV} size="sm" disabled={unifiedData.length === 0}>
              <Download className="h-4 w-4 mr-2" />
              Download CSV
            </Button>
          </div>
        </div>

        <div className="grid gap-6 mb-8 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Calls</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{totalCalls}</div>
              <p className="text-xs text-muted-foreground mt-1">{uniqueCallers} unique callers</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Conversations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{totalConversations}</div>
              <p className="text-xs text-muted-foreground mt-1">AI interactions</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Tokens</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{totalTokens.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground mt-1">OpenAI usage</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Cost</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">${totalCost.toFixed(4)}</div>
              <p className="text-xs text-muted-foreground mt-1">Estimated spend</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>All Call Data</CardTitle>
            <CardDescription>
              Complete log of all calls, conversations, and AI interactions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {unifiedData.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Phone className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No call data yet. Make your first test call!</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Phone Number</TableHead>
                      <TableHead>Event Type</TableHead>
                      <TableHead>User Message</TableHead>
                      <TableHead>AI Response</TableHead>
                      <TableHead>Call Status</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Interactions</TableHead>
                      <TableHead>Model</TableHead>
                      <TableHead>Tokens</TableHead>
                      <TableHead>Cost</TableHead>
                      <TableHead>Call SID</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {unifiedData.slice().reverse().map((row, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="text-xs whitespace-nowrap">
                          {formatTimestamp(row.timestamp)}
                        </TableCell>
                        <TableCell className="font-mono text-sm">{row.from_number}</TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-xs">
                            {row.event_type}
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-xs">
                          <div className="truncate" title={row.user_message}>
                            {row.user_message}
                          </div>
                        </TableCell>
                        <TableCell className="max-w-xs">
                          <div className="truncate" title={row.ai_response}>
                            {row.ai_response}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={row.call_status === 'completed' ? 'default' : 'outline'}
                            className="text-xs"
                          >
                            {row.call_status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">{row.location}</TableCell>
                        <TableCell className="text-center">{row.interactions}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-xs">{row.openai_model}</Badge>
                        </TableCell>
                        <TableCell className="text-right">{row.tokens_used.toLocaleString()}</TableCell>
                        <TableCell className="text-right font-mono text-xs text-green-600">
                          {row.cost_usd}
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {row.call_sid.substring(0, 10)}...
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminSimple;
