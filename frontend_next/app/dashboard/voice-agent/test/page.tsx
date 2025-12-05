'use client';

import { useMemo, useEffect, useState } from 'react';
import { TokenSource } from 'livekit-client';
import {
  RoomAudioRenderer,
  SessionProvider,
  StartAudio,
  useSession,
} from '@livekit/components-react';
import { useAuth } from '@/contexts/AuthContext';
import { ViewController } from '@/components/voice-agent/view-controller';
import { Toaster } from '@/components/livekit/toaster';
import type { AppConfig } from '@/app-config';

/**
 * Multi-tenant Voice Agent Test Page
 * Uses the full agent-starter-react template design
 */

interface VoiceAgentAppProps {
  tenantId: string;
}

function VoiceAgentApp({ tenantId }: VoiceAgentAppProps) {
  // App configuration matching agent-starter-react style
  const appConfig: AppConfig = useMemo(() => ({
    companyName: 'AI Receptionist',
    pageTitle: 'Voice Agent Test',
    pageDescription: 'Talk to your AI receptionist',
    supportsChatInput: true,
    supportsVideoInput: false,
    supportsScreenShare: false,
    isPreConnectBufferEnabled: true,
    logo: '/logo.svg',
    accent: '#002cf2',
    logoDark: '/logo.svg',
    accentDark: '#1fd5f9',
    startButtonText: 'Start Call',
  }), []);

  // Create token source for this tenant
  const tokenSource = useMemo(() => {
    return TokenSource.custom(async () => {
      const res = await fetch('/api/connection-details', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_id: tenantId }),
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Failed to get connection details: ${errorText}`);
      }
      
      return await res.json();
    });
  }, [tenantId]);

  // Create session from token source
  const session = useSession(tokenSource);

  return (
    <SessionProvider session={session}>
      {/* Full height container that respects dashboard layout */}
      <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden bg-background">
        <ViewController appConfig={appConfig} />
      </div>
      <StartAudio label="Start Audio" />
      <RoomAudioRenderer />
      <Toaster />
    </SessionProvider>
  );
}

export default function VoiceAgentTestPage() {
  const { user, isLoading } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)] bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (!user?.tenant_id) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-4rem)] bg-background">
        <h2 className="text-2xl font-bold mb-4">No Tenant Found</h2>
        <p className="text-muted-foreground">Please log in to test the voice agent.</p>
      </div>
    );
  }

  return <VoiceAgentApp tenantId={user.tenant_id} />;
}
