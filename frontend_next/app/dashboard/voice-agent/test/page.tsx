"use client";

import React, { useEffect, useState } from 'react';
import { VapiProvider } from '@/components/vapi/VapiProvider';
import { CallButton } from '@/components/vapi/CallButton';
import { useAuth } from '@/contexts/AuthContext';
import { assistantApi, vapiApi } from '@/lib/api-endpoints';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2, Mic, Settings, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function VoiceAgentTestPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [assistantId, setAssistantId] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState<string>(process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY || "");
  const [configLoading, setConfigLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [callError, setCallError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAssistantConfig() {
      if (!user) return;
      try {
        const data = await assistantApi.getTestConfig();
        if (data?.assistant_id) {
          setAssistantId(data.assistant_id);
        } else {
          setError("No assistant configured");
        }

        if (data?.public_key) {
          setApiKey(data.public_key);
        } else if (!process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY) {
          setError("Vapi Public Key is missing. Configure it in Voice Agent settings.");
        }
      } catch (err) {
        console.error("Failed to fetch assistant test config", err);
        try {
          const assistant = await vapiApi.getMyAssistant();
          if (assistant?.assistant_id) {
            setAssistantId(assistant.assistant_id);
          }
        } catch (assistantErr) {
          console.error("Failed to fetch assistant", assistantErr);
          setError("Failed to load assistant configuration");
        }
      } finally {
        setConfigLoading(false);
      }
    }

    if (!authLoading && user) {
      fetchAssistantConfig();
    }
  }, [user, authLoading]);

  if (authLoading || configLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <VapiProvider apiKey={apiKey}>
      <div className="flex h-[calc(100vh-4rem)] bg-gradient-to-b from-background to-muted/20 p-6">

        <div className="w-full flex items-center justify-center">
          <Card className="bg-white border-slate-200 shadow-sm w-full max-w-md shadow-lg border-primary/20">
            <CardHeader className="bg-white border-slate-200 shadow-sm text-center pb-2">
              <div className="mx-auto bg-primary/10 p-4 rounded-full mb-4 w-20 h-20 flex items-center justify-center">
                <Mic className="h-10 w-10 text-primary" />
              </div>
              <CardTitle className="bg-white border-slate-200 shadow-sm text-2xl">Test Your AI Receptionist</CardTitle>
              <CardDescription>
                {assistantId
                  ? "Microphone access is required. Speak normally."
                  : "No assistant configured yet."}
              </CardDescription>
            </CardHeader>
            <CardContent className="bg-white border-slate-200 shadow-sm flex flex-col items-center gap-6 pt-6">
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
                    onCallStart={() => setCallError(null)}
                    onError={(message) => setCallError(message)}
                    className="w-full h-14 text-lg"
                  />
                  {callError ? (
                    <p className="text-sm text-destructive text-center">{callError}</p>
                  ) : null}
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
      </div>
    </VapiProvider>
  );
}
