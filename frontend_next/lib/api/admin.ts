import api from '@/lib/api';
import {
    UserResponse,
    AppointmentResponse,
    ServiceResponse,
    ConversationResponse,
    TenantResponse,
    BusinessConfig,
    Token,
} from '@/lib/types';

export type User = UserResponse;
export type Appointment = AppointmentResponse;
export type Service = ServiceResponse;
export type Conversation = ConversationResponse;
export type Tenant = TenantResponse;
export type { BusinessConfig };

export interface CrewJob {
    id: string;
    status: 'queued' | 'running' | 'completed' | 'failed';
    task?: string;
    created_at?: string;
    updated_at?: string;
    metadata?: Record<string, unknown>;
}

type Paginated<T> = {
    items: T[];
    total: number;
    page?: number;
    limit?: number;
};

type PaginatedOrList<T> = Paginated<T> | T[];

export interface TenantBillingSummary {
    tenant_id: string;
    name: string;
    email: string;
    billing_plan: string;
    subscription_status: string;
    minutes_balance: number;
    billing_period_end: string | null;
    calls_paused: boolean;
    billing_exempt: boolean;
    fallback_number: string | null;
    has_phone_number: boolean;
    calls_30d: number;
    minutes_30d: number;
    vapi_cost_30d_usd: number;
    revenue_30d_usd: number;
    margin_30d_usd: number;
}

export interface BillingOverview {
    tenants: TenantBillingSummary[];
    platform_summary: {
        total_tenants: number;
        paying_tenants: number;
        paused_tenants: number;
        revenue_30d_usd: number;
        vapi_cost_30d_usd: number;
        margin_30d_usd: number;
        minutes_owed: number;
        enforcement_enabled: boolean;
    };
    topup_price_per_minute_usd: number;
}

export interface AddMinutesPayload {
    /** "monthly" (with calls + avg_minutes) or "custom"; leave out for extra minutes. */
    plan?: string;
    calls?: number;
    avg_minutes?: number;
    minutes?: number;
    amount_paid?: number;
    currency?: string;
    reference?: string;
    note?: string;
}

export interface IndustryTemplate {
    id: string;
    label: string;
    description: string;
    services: string[];
}

export interface BillingSettingsPayload {
    billing_exempt?: boolean;
    fallback_number?: string;
}

interface GlobalAnalytics {
    tenants: {
        total: number;
        active: number;
    };
    users: number;
    appointments: number;
    conversations: number;
}

interface JobTriggerResponse {
    message: string;
    job_id?: string;
}

interface JobStatusResponse {
    job_id: string;
    status: CrewJob['status'];
    progress?: number;
    result?: Record<string, unknown>;
    error?: string;
}

// Admin API Functions
export const adminApi = {
    // Users
    getUsers: async (skip = 0, limit = 100): Promise<UserResponse[]> => {
        const response = await api.get<UserResponse[]>(`/admin/users?skip=${skip}&limit=${limit}`);
        return response;
    },
    createUser: async (data: Partial<UserResponse>): Promise<UserResponse> => {
        const response = await api.post<UserResponse>('/admin/users', data);
        return response;
    },
    updateUser: async (id: string, data: Partial<UserResponse>): Promise<UserResponse> => {
        const response = await api.put<UserResponse>(`/admin/users/${id}`, data);
        return response;
    },
    deleteUser: async (id: string) => {
        await api.delete(`/admin/users/${id}`);
    },
    impersonateUser: async (id: string): Promise<Token> => {
        const response = await api.post<Token>(`/admin/users/${id}/impersonate`);
        return response;
    },
    approveUser: async (id: string): Promise<UserResponse> => {
        const response = await api.post<UserResponse>(`/admin/users/${id}/approve`);
        return response;
    },
    rejectUser: async (id: string): Promise<UserResponse> => {
        const response = await api.post<UserResponse>(`/admin/users/${id}/reject`);
        return response;
    },
    getPendingUsers: async (): Promise<UserResponse[]> => {
        const response = await api.get<UserResponse[]>('/admin/users/pending');
        return response;
    },

    // Appointments
    getAppointments: async (
        skip = 0,
        limit = 100,
        status?: string
    ): Promise<PaginatedOrList<AppointmentResponse>> => {
        let url = `/admin/appointments?skip=${skip}&limit=${limit}`;
        if (status) url += `&status=${status}`;
        const response = await api.get<PaginatedOrList<AppointmentResponse>>(url);
        return response;
    },
    createAppointment: async (data: AppointmentResponse | Partial<AppointmentResponse>): Promise<AppointmentResponse> => {
        const response = await api.post<AppointmentResponse>('/admin/appointments', data);
        return response;
    },
    updateAppointment: async (id: string, data: Partial<AppointmentResponse>): Promise<AppointmentResponse> => {
        const response = await api.put<AppointmentResponse>(`/admin/appointments/${id}`, data);
        return response;
    },
    deleteAppointment: async (id: string) => {
        await api.delete(`/admin/appointments/${id}`);
    },

    // Services
    getServices: async (skip = 0, limit = 100): Promise<PaginatedOrList<ServiceResponse>> => {
        const response = await api.get<PaginatedOrList<ServiceResponse>>(`/admin/services?skip=${skip}&limit=${limit}`);
        return response;
    },
    createService: async (data: ServiceResponse | Partial<ServiceResponse>): Promise<ServiceResponse> => {
        const response = await api.post<ServiceResponse>('/admin/services', data);
        return response;
    },
    updateService: async (id: string, data: Partial<ServiceResponse>): Promise<ServiceResponse> => {
        const response = await api.put<ServiceResponse>(`/admin/services/${id}`, data);
        return response;
    },
    deleteService: async (id: string) => {
        await api.delete(`/admin/services/${id}`);
    },

    // Conversations
    getConversations: async (
        skip = 0,
        limit = 100,
        phone?: string
    ): Promise<PaginatedOrList<ConversationResponse>> => {
        let url = `/admin/conversations?skip=${skip}&limit=${limit}`;
        if (phone) url += `&phone=${phone}`;
        const response = await api.get<PaginatedOrList<ConversationResponse>>(url);
        return response;
    },
    deleteConversation: async (id: string) => {
        await api.delete(`/admin/conversations/${id}`);
    },

    // Business Config
    getConfig: async (): Promise<BusinessConfig> => {
        const response = await api.get<BusinessConfig>('/admin/config');
        return response;
    },
    updateConfig: async (data: Partial<BusinessConfig>): Promise<BusinessConfig> => {
        const response = await api.put<BusinessConfig>('/admin/config', data);
        return response;
    },

    // Tenants
    getTenants: async (
        skip = 0,
        limit = 100,
        search?: string
    ): Promise<PaginatedOrList<TenantResponse>> => {
        let url = `/admin/tenants?skip=${skip}&limit=${limit}`;
        if (search) url += `&search=${search}`;
        const response = await api.get<PaginatedOrList<TenantResponse>>(url);
        return response;
    },
    createTenant: async (data: Partial<TenantResponse>): Promise<TenantResponse> => {
        const response = await api.post<TenantResponse>('/admin/tenants', data);
        return response;
    },
    updateTenant: async (id: string, data: Partial<TenantResponse>): Promise<TenantResponse> => {
        const response = await api.put<TenantResponse>(`/admin/tenants/${id}`, data);
        return response;
    },
    deleteTenant: async (id: string): Promise<void> => {
        await api.delete(`/admin/tenants/${id}`);
    },

    // Analytics
    getGlobalAnalytics: async (): Promise<GlobalAnalytics> => {
        const response = await api.get<GlobalAnalytics>('/admin/analytics/global');
        return response;
    },

    // Industry templates (plumber, law firm...)
    getTemplates: async (): Promise<IndustryTemplate[]> => {
        return api.get<IndustryTemplate[]>('/admin/templates');
    },
    applyTemplate: async (tenantId: string, template: string): Promise<{ success: boolean; services_added: number }> => {
        return api.post(`/admin/tenants/${tenantId}/template`, { template });
    },

    // Billing Overview
    getBillingOverview: async (): Promise<BillingOverview> => {
        return api.get<BillingOverview>('/admin/billing/overview');
    },
    addMinutes: async (tenantId: string, payload: AddMinutesPayload): Promise<{ success: boolean }> => {
        return api.post(`/admin/billing/tenants/${tenantId}/minutes`, payload);
    },
    updateBillingSettings: async (tenantId: string, payload: BillingSettingsPayload): Promise<{ success: boolean }> => {
        return api.patch(`/admin/billing/tenants/${tenantId}`, payload);
    },
    syncBilling: async (): Promise<{ tenants: number; paused: number; resumed: number; enforcement_enabled: boolean }> => {
        return api.post('/admin/billing/sync');
    },

    // CrewAI
    triggerDataCleaning: async (): Promise<JobTriggerResponse> => {
        const response = await api.post<JobTriggerResponse>('/crew/clean-data');
        return response;
    },
    triggerAnalytics: async (): Promise<JobTriggerResponse> => {
        const response = await api.post<JobTriggerResponse>('/crew/analyze');
        return response;
    },
    getJobStatus: async (jobId: string): Promise<JobStatusResponse> => {
        const response = await api.get<JobStatusResponse>(`/crew/status/${jobId}`);
        return response;
    },
    getJobs: async (limit = 10): Promise<CrewJob[]> => {
        const response = await api.get<CrewJob[]>(`/crew/jobs?limit=${limit}`);
        return response;
    }
};
