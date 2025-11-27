import api from '@/lib/api';
import {
    UserResponse,
    AppointmentResponse,
    ServiceResponse,
    ConversationResponse,
    TenantResponse,
    BusinessConfig,
    CrewJobResponse
} from '@/lib/types';

export type User = UserResponse;
export type Appointment = AppointmentResponse;
export type Service = ServiceResponse;
export type Conversation = ConversationResponse;
export type Tenant = TenantResponse;
export type CrewJob = CrewJobResponse;
export type { BusinessConfig };

// Admin API Functions
export const adminApi = {
    // Users
    getUsers: async (skip = 0, limit = 100) => {
        const response = await api.get(`/admin/users?skip=${skip}&limit=${limit}`);
        return response.data;
    },
    createUser: async (data: any) => {
        const response = await api.post('/admin/users', data);
        return response.data;
    },
    updateUser: async (id: string, data: any) => {
        const response = await api.put(`/admin/users/${id}`, data);
        return response.data;
    },
    deleteUser: async (id: string) => {
        await api.delete(`/admin/users/${id}`);
    },
    impersonateUser: async (id: string) => {
        const response = await api.post(`/admin/users/${id}/impersonate`);
        return response.data;
    },

    // Appointments
    getAppointments: async (skip = 0, limit = 100, status?: string) => {
        let url = `/admin/appointments?skip=${skip}&limit=${limit}`;
        if (status) url += `&status=${status}`;
        const response = await api.get(url);
        return response.data;
    },
    createAppointment: async (data: any) => {
        const response = await api.post('/admin/appointments', data);
        return response.data;
    },
    updateAppointment: async (id: string, data: any) => {
        const response = await api.put(`/admin/appointments/${id}`, data);
        return response.data;
    },
    deleteAppointment: async (id: string) => {
        await api.delete(`/admin/appointments/${id}`);
    },

    // Services
    getServices: async (skip = 0, limit = 100) => {
        const response = await api.get(`/admin/services?skip=${skip}&limit=${limit}`);
        return response.data;
    },
    createService: async (data: any) => {
        const response = await api.post('/admin/services', data);
        return response.data;
    },
    updateService: async (id: string, data: any) => {
        const response = await api.put(`/admin/services/${id}`, data);
        return response.data;
    },
    deleteService: async (id: string) => {
        await api.delete(`/admin/services/${id}`);
    },

    // Conversations
    getConversations: async (skip = 0, limit = 100, phone?: string) => {
        let url = `/admin/conversations?skip=${skip}&limit=${limit}`;
        if (phone) url += `&phone=${phone}`;
        const response = await api.get(url);
        return response.data;
    },
    deleteConversation: async (id: string) => {
        await api.delete(`/admin/conversations/${id}`);
    },

    // Business Config
    getConfig: async () => {
        const response = await api.get('/admin/config');
        return response.data;
    },
    updateConfig: async (data: any) => {
        const response = await api.put('/admin/config', data);
        return response.data;
    },

    // Tenants
    getTenants: async (skip = 0, limit = 100, search?: string) => {
        let url = `/admin/tenants?skip=${skip}&limit=${limit}`;
        if (search) url += `&search=${search}`;
        const response = await api.get(url);
        return response.data;
    },
    createTenant: async (data: any) => {
        const response = await api.post('/admin/tenants', data);
        return response.data;
    },
    updateTenant: async (id: string, data: any) => {
        const response = await api.put(`/admin/tenants/${id}`, data);
        return response.data;
    },

    // Analytics
    getGlobalAnalytics: async () => {
        const response = await api.get('/admin/analytics/global');
        return response.data;
    },

    // CrewAI
    triggerDataCleaning: async () => {
        const response = await api.post('/crew/clean-data');
        return response.data;
    },
    triggerAnalytics: async () => {
        const response = await api.post('/crew/analyze');
        return response.data;
    },
    getJobStatus: async (jobId: string) => {
        const response = await api.get(`/crew/status/${jobId}`);
        return response.data;
    },
    getJobs: async (limit = 10) => {
        const response = await api.get(`/crew/jobs?limit=${limit}`);
        return response.data;
    }
};
