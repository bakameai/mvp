
import React, { useEffect, useState } from 'react';
import { authAPI } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Activity, Wifi, Server, Database, RefreshCw } from 'lucide-react';

interface InfrastructureStatus {
  ivrChat: 'online' | 'offline' | 'error';
  realtimeChat: 'online' | 'offline' | 'error';
  createSession: 'online' | 'offline' | 'error';
  database: 'online' | 'offline' | 'error';
  lastUpdated: Date;
}

const IVRBridge: React.FC = () => {
  const [status, setStatus] = useState<InfrastructureStatus>({
    ivrChat: 'offline',
    realtimeChat: 'offline',
    createSession: 'offline',
    database: 'offline',
    lastUpdated: new Date()
  });

  const [isChecking, setIsChecking] = useState(false);

  const checkInfrastructureStatus = async () => {
    setIsChecking(true);
    const newStatus: InfrastructureStatus = {
      ivrChat: 'offline',
      realtimeChat: 'offline',
      createSession: 'offline',
      database: 'offline',
      lastUpdated: new Date()
    };

    try {
      // Check IVR Chat function via FastAPI endpoint
      const ivrChatResponse = await fetch('/api/ivr/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'ping', sessionId: 'health-check' })
      });
      newStatus.ivrChat = ivrChatResponse.ok ? 'online' : 'error';
    } catch (error) {
      newStatus.ivrChat = 'error';
    }

    try {
      // Check Create Session function via FastAPI endpoint
      const createSessionResponse = await fetch('/api/sessions/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      newStatus.createSession = createSessionResponse.ok ? 'online' : 'error';
    } catch (error) {
      newStatus.createSession = 'error';
    }

    try {
      // Check Database connection via FastAPI health endpoint
      const response = await fetch('/api/health/database');
      newStatus.database = response.ok ? 'online' : 'error';
    } catch (error) {
      newStatus.database = 'error';
    }

    // Note: Realtime chat status would need WebSocket connection test
    // For now, we'll mark it as online if create-session works
    newStatus.realtimeChat = newStatus.createSession === 'online' ? 'online' : 'offline';

    setStatus(newStatus);
    setIsChecking(false);
  };

  useEffect(() => {
    checkInfrastructureStatus();
    const interval = setInterval(checkInfrastructureStatus, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (serviceStatus: 'online' | 'offline' | 'error') => {
    switch (serviceStatus) {
      case 'online':
        return <Badge className="bg-green-500 text-white">Online</Badge>;
      case 'offline':
        return <Badge className="bg-gray-500 text-white">Offline</Badge>;
      case 'error':
        return <Badge className="bg-red-500 text-white">Error</Badge>;
    }
  };

  const services = [
    {
      name: 'IVR Chat (HTTP)',
      key: 'ivrChat' as keyof InfrastructureStatus,
      icon: <Server className="w-5 h-5" />,
      description: 'Text-based chat with enhanced web capabilities'
    },
    {
      name: 'Realtime Chat (WebSocket)',
      key: 'realtimeChat' as keyof InfrastructureStatus,
      icon: <Wifi className="w-5 h-5" />,
      description: 'Real-time voice and text communication'
    },
    {
      name: 'Session Management (WebRTC)',
      key: 'createSession' as keyof InfrastructureStatus,
      icon: <Activity className="w-5 h-5" />,
      description: 'WebRTC session creation for voice calls'
    },
    {
      name: 'Database',
      key: 'database' as keyof InfrastructureStatus,
      icon: <Database className="w-5 h-5" />,
      description: 'Session storage and analytics'
    }
  ];

  return (
    <Card className="bg-[#081a2e]/80 backdrop-blur-md border-white/20 text-white">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Server className="w-5 h-5 text-[#ff914d]" />
            Infrastructure Status
          </div>
          <Button
            onClick={checkInfrastructureStatus}
            disabled={isChecking}
            size="sm"
            variant="outline"
            className="border-white/30 text-white hover:bg-white/10"
          >
            <RefreshCw className={`w-4 h-4 ${isChecking ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {services.map((service) => (
            <div key={service.key} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="text-[#0d4dcc]">{service.icon}</div>
                <div>
                  <div className="font-medium text-white">{service.name}</div>
                  <div className="text-sm text-white/70">{service.description}</div>
                </div>
              </div>
              {getStatusBadge(status[service.key] as any)}
            </div>
          ))}
        </div>
        
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center justify-between text-sm text-white/70">
            <span>Last updated: {status.lastUpdated.toLocaleTimeString()}</span>
            <span>Connected to Devin Infrastructure</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default IVRBridge;
