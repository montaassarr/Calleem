'use client';

import { App } from '@/components/app/app';
import type { AppConfig } from '@/app-config';

export default function VoiceAgentChatPage() {
  // Configure the LiveKit voice agent with your multi-tenant settings
  const appConfig: AppConfig = {
    companyName: 'AI Receptionist',
    pageTitle: 'AI Receptionist - Voice Chat',
    pageDescription: 'Talk to your AI receptionist for appointment booking and inquiries',
    
    supportsChatInput: true,
    supportsVideoInput: false,
    supportsScreenShare: false,
    isPreConnectBufferEnabled: true,
    
    logo: '/logo.svg',
    accent: '#002cf2',
    logoDark: '/logo.svg',
    accentDark: '#1fd5f9',
    startButtonText: 'Start Chat',
  };

  return (
    <div className="h-screen w-full bg-background">
      <App appConfig={appConfig} />
    </div>
  );
}
