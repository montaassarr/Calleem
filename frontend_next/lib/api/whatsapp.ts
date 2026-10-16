/**
 * WhatsApp (Meta Cloud API) and the Chat Test: both talk to the same AI receptionist.
 */

import api from '@/lib/api';

export interface WhatsAppStatus {
    configured: boolean;
    status: 'connected' | 'not_configured';
    phone_number: string | null;
    verified_name: string | null;
    phone_number_id: string | null;
    waba_id: string | null;
    uses_own_token: boolean;
    has_app_secret: boolean;
    connected_at: string | null;
    last_message_at: string | null;
    platform_ready: boolean;
    webhook_url: string;
    verify_token: string | null;
}

export interface WhatsAppConnectionInput {
    phone_number_id: string;
    waba_id?: string;
    access_token?: string;
    app_secret?: string;
}

export interface WhatsAppConversation {
    id: string;
    customer_phone: string | null;
    customer_name: string | null;
    updated_at: string;
    transcript: { role: 'customer' | 'assistant'; text: string; at: string; tools?: string[] }[];
}

export interface TestChatReply {
    response: string;
    tools_used: string[];
    appointment_id: string | null;
}

export const whatsappApi = {
    getStatus: (): Promise<WhatsAppStatus> => api.get<WhatsAppStatus>('/whatsapp/status'),

    connect: (data: WhatsAppConnectionInput): Promise<WhatsAppStatus> =>
        api.put<WhatsAppStatus>('/whatsapp/connection', data),

    disconnect: (): Promise<{ success: boolean }> => api.delete('/whatsapp/connection'),

    listConversations: (limit = 20): Promise<WhatsAppConversation[]> =>
        api.get<WhatsAppConversation[]>('/whatsapp/conversations', { params: { limit } }),

    testChat: (message: string, sessionId: string): Promise<TestChatReply> =>
        api.post<TestChatReply>('/whatsapp/test-chat', { message, session_id: sessionId }),

    resetTestChat: (sessionId: string): Promise<{ success: boolean }> =>
        api.delete(`/whatsapp/test-chat/${sessionId}`),
};
