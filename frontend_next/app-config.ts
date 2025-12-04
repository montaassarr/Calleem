export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'AI Receptionist',
  pageTitle: 'AI Receptionist - Voice Agent',
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

  // Agent configuration - will be set per tenant
  sandboxId: undefined,
  agentName: undefined,
};
