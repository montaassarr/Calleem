"use client";

import React, { useEffect, useState } from 'react';
import { VapiProvider } from '@/components/vapi/VapiProvider';
import { CallButton } from '@/components/vapi/CallButton';
import { useAuth } from '@/contexts/AuthContext';
import { vapiApi } from '@/lib/api-endpoints';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2, Mic, Settings, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import LiveCallMonitor from '@/components/dashboard/LiveCallMonitor';

export default function VoiceAgentTestPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [assistantId, setAssistantId] = useState<string | null>(null);
  const [configLoading, setConfigLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get Vapi Public Key from env
  const apiKey = process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY || "";

  useEffect(() => {
    async function fetchAssistant() {
      if (!user) return;
      try {
        const data = await vapiApi.getMyAssistant();
        if (data && data.assistant_id) {
          setAssistantId(data.assistant_id);
        } else {
          setError("No assistant configured");
        }
      } catch (err) {
        console.error("Failed to fetch assistant", err);
        setError("Failed to load assistant configuration");
      } finally {
        setConfigLoading(false);
      }
    }

    if (!authLoading && user) {
      fetchAssistant();
    }
  }, [user, authLoading]);

  if (authLoading || configLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    );
  }

  if (!apiKey) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-4rem)] p-6 text-center">
        <h2 className="text-2xl font-bold mb-4 text-destructive">Configuration Error</h2>
        <p className="max-w-md text-muted-foreground mb-6">
          Vapi Public Key is missing. Please contact the administrator to configure the platform.
        </p>
      </div>
    );
  }

  return (
    <VapiProvider apiKey={apiKey}>
      <div className="flex h-[calc(100vh-4rem)] bg-gradient-to-b from-background to-muted/20 p-6 gap-6">

        {/* Left Column: Call Controls */}
        <div className="flex-1 flex items-center justify-center">
          <Card className="w-full max-w-md shadow-lg border-primary/20">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto bg-primary/10 p-4 rounded-full mb-4 w-20 h-20 flex items-center justify-center">
                <Mic className="h-10 w-10 text-primary" />
              </div>
              <CardTitle className="text-2xl">Test Your AI Receptionist</CardTitle>
              <CardDescription>
                {assistantId
                  ? "Microphone access is required. Speak normally."
                  : "No assistant configured yet."}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center gap-6 pt-6">
              {error ? (
                <div className="text-center space-y-4">
                  <p className="text-destructive font-medium">{error}</p>
                  <Button asChild variant="outline">
                    <Link href="/dashboard/voice-agent/control-center">
                      <Settings className="mr-2 h-4 w-4" />
                      Configure Assistant
                    </Link>
                  </Button>
                </div>
              ) : assistantId ? (
                <div className="flex flex-col items-center gap-4 w-full">
                  <CallButton
                    assistantId={assistantId}
                    className="w-full h-14 text-lg"
                  />
                  <p className="text-sm text-muted-foreground text-center">
                    Click to start a conversation. The AI will respond as configured.
                  </p>
                  <Button asChild variant="outline" className="w-full mt-3">
                    <Link href="/dashboard/voice-agent/chat">
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Try Chat Instead
                    </Link>
                  </Button>
                </div>
              ) : (
                <Button asChild>
                  <Link href="/dashboard/voice-agent/control-center">
                    Configure Assistant First
                  </Link>
                </Button>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Live Monitor */}
        <div className="flex-1 max-w-2xl h-full">
          <LiveCallMonitor />
        </div>

      </div>
    </VapiProvider>
  );
}
