import api from '@/lib/api';
import { CrewJobResponse, CrewJobStatus } from '@/lib/types';

export interface CrewJobStartResponse {
    job_id: string;
    message: string;
}

export const crewApi = {
    triggerDataCleaning: async (): Promise<CrewJobStartResponse> => {
        const response = await api.post<CrewJobStartResponse>('/crew/clean-data');
        return response.data;
    },

    triggerAnalytics: async (): Promise<CrewJobStartResponse> => {
        const response = await api.post<CrewJobStartResponse>('/crew/analyze');
        return response.data;
    },

    triggerInsights: async (): Promise<CrewJobStartResponse> => {
        const response = await api.post<CrewJobStartResponse>('/crew/insights');
        return response.data;
    },

    triggerRevenue: async (): Promise<CrewJobStartResponse> => {
        const response = await api.post<CrewJobStartResponse>('/crew/revenue');
        return response.data;
    },

    getJobStatus: async (jobId: string): Promise<CrewJobResponse> => {
        const response = await api.get<CrewJobResponse>(`/crew/status/${jobId}`);
        return response.data;
    }
};
