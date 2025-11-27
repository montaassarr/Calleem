import api from '@/lib/api';
import type {
    VoiceStartCallRequest,
    VoiceStartCallResponse,
    VoiceTestResponse,
    VoiceCallHistoryResponse,
    VoiceWebRTCResponse,
    VoiceConfiguration,
    VoiceModel,
    VoiceOption,
    VoiceTool,
} from '@/lib/types';

export const voiceApi = {
    startCall: async (payload: VoiceStartCallRequest): Promise<VoiceStartCallResponse> => {
        const { data } = await api.post<VoiceStartCallResponse>('/voice/start-call', payload);
        return data;
    },
    testAgent: async (): Promise<VoiceTestResponse> => {
        const { data } = await api.get<VoiceTestResponse>('/voice/test-agent');
        return data;
    },
    callHistory: async (limit = 20): Promise<VoiceCallHistoryResponse> => {
        const { data } = await api.get<VoiceCallHistoryResponse>('/voice/call-history', { params: { limit } });
        return data;
    },
    webrtcTest: async (): Promise<VoiceWebRTCResponse> => {
        const { data } = await api.get<VoiceWebRTCResponse>('/voice/test');
        return data;
    },
    getConfig: async (): Promise<VoiceConfiguration> => {
        const { data } = await api.get<VoiceConfiguration>('/voice/config');
        return data;
    },
    updateConfig: async (config: VoiceConfiguration): Promise<{ status: string; message: string }> => {
        const { data } = await api.put('/voice/config', config);
        return data;
    },
    getModels: async (): Promise<{ groq: VoiceModel[]; openai: VoiceModel[] }> => {
        const { data } = await api.get('/voice/models');
        return data;
    },
    getVoices: async (forceRefresh = false): Promise<{ voices: VoiceOption[]; count: number; elevenlabs_configured: boolean }> => {
        const { data } = await api.get('/voice/voices', { params: { force_refresh: forceRefresh } });
        return data;
    },
    getTools: async (): Promise<{ tools: VoiceTool[] }> => {
        const { data } = await api.get('/voice/tools');
        return data;
    },
    getVapiConfig: async (): Promise<{ publicKey: string; assistantId: string }> => {
        const { data } = await api.get('/voice/vapi-config');
        return data;
    },
};
