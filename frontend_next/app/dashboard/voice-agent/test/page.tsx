"use client";

import React, { useEffect, useState } from 'react';
import { VapiProvider } from '@/components/vapi/VapiProvider';
import { CallButton } from '@/components/vapi/CallButton';
import { useAuth } from '@/contexts/AuthContext';
import { assistantApi, vapiApi } from '@/lib/api-endpoints';
import { Loader2, Mic, Settings, MessageSquare, ArrowLeft, Phone } from 'lucide-react';
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
        if (data?.assistant_id) setAssistantId(data.assistant_id);
        else setError("No assistant configured");
        if (data?.public_key) setApiKey(data.public_key);
        else if (!process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY) setError("Vapi Public Key is missing.");
      } catch (err) {
        console.error("Failed to fetch assistant test config", err);
        try { const assistant = await vapiApi.getMyAssistant(); if (assistant?.assistant_id) setAssistantId(assistant.assistant_id); }
        catch { setError("Failed to load assistant configuration"); }
      } finally { setConfigLoading(false); }
    }
    if (!authLoading && user) fetchAssistantConfig();
  }, [user, authLoading]);

  if (authLoading || configLoading) {
    return <div className="flex items-center justify-center h-[calc(100vh-4rem)]"><Loader2 className="h-12 w-12 animate-spin text-[#0a4c2f]" /></div>;
  }

  return (
    <VapiProvider apiKey={apiKey}>
      <div className="flex flex-col h-[calc(100vh-200px)] items-center justify-center">
        <div className="w-full max-w-md bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 overflow-hidden">
          {/* Card Header */}
          <div className="text-center pt-10 pb-2 px-6">
            {/* Animated mic circle */}
            <div className="relative mx-auto mb-6 w-24 h-24">
              <div className="absolute inset-0 rounded-full bg-[#0a4c2f]/5 animate-ping" style={{ animationDuration: '3s' }}></div>
              <div className="absolute inset-2 rounded-full bg-[#0a4c2f]/10"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#187848] to-[#0a4c2f] flex items-center justify-center shadow-[0_4px_16px_rgba(10,76,47,0.3)]">
                  <Mic className="h-7 w-7 text-white" />
                </div>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Test Your AI Receptionist</h2>
            <p className="text-sm text-gray-500 mt-2">
              {assistantId ? "Microphone access required. Speak naturally." : "No assistant configured yet."}
            </p>
          </div>

          {/* Content */}
          <div className="flex flex-col items-center gap-4 p-6 pt-4">
            {error ? (
              <div className="text-center space-y-4 w-full">
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <p className="text-red-700 font-medium text-sm">{error}</p>
                </div>
                <Link href="/dashboard/voice-agent/control-center" className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm">
                  <Settings className="h-4 w-4" />Configure Assistant
                </Link>
              </div>
            ) : assistantId ? (
              <div className="flex flex-col items-center gap-4 w-full">
                <CallButton
                  assistantId={assistantId}
                  onCallStart={() => setCallError(null)}
                  onError={(message) => setCallError(message)}
                  className="w-full h-14 text-lg rounded-xl"
                />
                {callError && (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-3 w-full">
                    <p className="text-sm text-red-700 text-center">{callError}</p>
                  </div>
                )}
                <p className="text-sm text-gray-500 text-center">Click to start a conversation. The AI will respond as configured.</p>

                <div className="w-full border-t border-gray-100 pt-4 flex gap-2">
                  <Link href="/dashboard/voice-agent/chat" className="flex-1 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center justify-center gap-2">
                    <MessageSquare className="w-4 h-4" />Chat Test
                  </Link>
                  <Link href="/dashboard/voice-agent/control-center" className="flex-1 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center justify-center gap-2">
                    <ArrowLeft className="w-4 h-4" />Back
                  </Link>
                </div>
              </div>
            ) : (
              <Link href="/dashboard/voice-agent/control-center" className="w-full px-6 py-3 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-xl font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] relative overflow-hidden text-center block">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                <span className="relative z-10">Configure Assistant First</span>
              </Link>
            )}
          </div>
        </div>
      </div>
    </VapiProvider>
  );
}
