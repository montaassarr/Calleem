import api from "@/lib/api"
import type {
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentFilters,
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    ServiceFilters,
    ConversationResponse,
    UserResponse,
    VoiceAgentStatus,
    VoiceWebRTCResponse,
} from "@/lib/types"

// API Base URL for direct fetch calls
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

export const appointmentsApi = {
    list: async (filters?: AppointmentFilters): Promise<AppointmentResponse[]> => {
        const response = await api.get<AppointmentResponse[]>("/appointments/", {
            params: filters,
        })
        return response
    },

    get: async (appointmentId: string): Promise<AppointmentResponse> => {
        const response = await api.get<AppointmentResponse>(`/appointments/${appointmentId}`)
        return response
    },

    create: async (data: AppointmentCreate): Promise<AppointmentResponse> => {
        const response = await api.post<AppointmentResponse>("/appointments/", data)
        return response
    },

    update: async (appointmentId: string, data: AppointmentUpdate): Promise<AppointmentResponse> => {
        const response = await api.put<AppointmentResponse>(`/appointments/${appointmentId}`, data)
        return response
    },

    delete: async (appointmentId: string): Promise<void> => {
        await api.delete(`/appointments/${appointmentId}`)
    },

    cancel: async (appointmentId: string): Promise<AppointmentResponse> => {
        const response = await api.post<AppointmentResponse>(`/appointments/${appointmentId}/cancel`)
        return response
    },

    checkAvailability: async (
        date: string,
        time: string,
        durationMinutes: number = 30,
    ): Promise<{
        available: boolean
        requested_datetime: string
        duration_minutes: number
        reason: string
    }> => {
        const response = await api.get("/appointments/availability/check", {
            params: {
                date,
                time,
                duration_minutes: durationMinutes,
            },
        })
        return response
    },

    getStats: async (): Promise<{
        total: number
        upcoming: number
        by_status: Record<string, number>
    }> => {
        const response = await api.get("/appointments/stats/summary")
        return response
    },
}

export const servicesApi = {
    list: async (filters?: ServiceFilters): Promise<ServiceResponse[]> => {
        const response = await api.get<ServiceResponse[]>("/services/", {
            params: filters,
        })
        return response
    },

    get: async (serviceId: string): Promise<ServiceResponse> => {
        const response = await api.get<ServiceResponse>(`/services/${serviceId}`)
        return response
    },

    create: async (data: ServiceCreate): Promise<ServiceResponse> => {
        const response = await api.post<ServiceResponse>("/services/", data)
        return response
    },

    update: async (serviceId: string, data: ServiceUpdate): Promise<ServiceResponse> => {
        const response = await api.put<ServiceResponse>(`/services/${serviceId}`, data)
        return response
    },

    delete: async (serviceId: string): Promise<void> => {
        await api.delete(`/services/${serviceId}`)
    },

    getActive: async (): Promise<ServiceResponse[]> => {
        return servicesApi.list({ active_only: true })
    },

    toggleActive: async (serviceId: string, isActive: boolean): Promise<ServiceResponse> => {
        return servicesApi.update(serviceId, { active: isActive })
    },
}

export const conversationsApi = {
    list: async (params?: { search?: string; limit?: number }): Promise<ConversationResponse[]> => {
        const response = await api.get<ConversationResponse[]>("/conversations", {
            params,
        })
        return response
    },

    get: async (id: string): Promise<ConversationResponse> => {
        const response = await api.get<ConversationResponse>(`/conversations/${id}`)
        return response
    },

    delete: async (id: string): Promise<void> => {
        await api.delete(`/conversations/${id}`)
    },
}

export const webhookApi = {
    getStatus: async (): Promise<any> => {
        const response = await api.get("/whatsapp/status")
        return response
    },

    updateSettings: async (settings: any): Promise<any> => {
        const response = await api.post("/whatsapp/settings", settings)
        return response
    }
}

export const usersApi = {
    list: async (tenantId?: string): Promise<UserResponse[]> => {
        const response = await api.get<UserResponse[]>("/admin/users", {
            params: { tenant_id: tenantId },
        })
        return response
    },

    create: async (data: Partial<UserResponse>): Promise<UserResponse> => {
        const response = await api.post<UserResponse>("/admin/users", data)
        return response
    },

    delete: async (id: string): Promise<void> => {
        await api.delete(`/admin/users/${id}`)
    },
}

export const voiceApi = {
    testAgent: async (): Promise<VoiceAgentStatus> => {
        const response = await api.get<VoiceAgentStatus>("/voice-agent/status")
        return response
    },

    callHistory: async (limit: number = 25): Promise<any> => {
        const response = await api.get("/voice-agent/history", {
            params: { limit }
        })
        return response
    },

    startCall: async (data: any): Promise<any> => {
        const response = await api.post("/voice-agent/call", data)
        return response
    },

    webrtcTest: async (): Promise<VoiceWebRTCResponse> => {
        const response = await api.post<VoiceWebRTCResponse>("/voice-agent/webrtc/test")
        return response
    },

    enableVoiceAgent: async (enabled: boolean = true): Promise<any> => {
        const response = await api.post("/voice-agent/enable", { enabled })
        return response
    },

    listCountries: async (): Promise<any[]> => {
        const response = await api.get("/voice-agent/numbers/countries")
        return response
    },

    searchNumbers: async (params: { country: string; area_code?: string }): Promise<any> => {
        const response = await api.get("/voice-agent/numbers/available", { params })
        return response
    },

    listNumbers: async (): Promise<any[]> => {
        const response = await api.get("/voice-agent/numbers")
        return response
    },

    purchaseNumber: async (payload: { country: string; phone_number: string }): Promise<any> => {
        const response = await api.post("/voice-agent/numbers/purchase", payload)
        return response
    }
}

export const businessConfigApi = {
    getConfig: async (): Promise<any> => {
        const response = await api.get("/admin/config")
        return response
    },

    updateFeatureFlags: async (features: any): Promise<any> => {
        const response = await api.put("/admin/config", features)
        return response
    }
}

// ============================================================================
// NEW: Onboarding API
// ============================================================================
export const onboardingApi = {
    getStatus: (): string => `${API_BASE_URL}/onboarding/status`,

    getVoiceProviders: async (): Promise<{
        providers: Array<{
            id: string
            name: string
            description: string
            get_key_url: string
            setup_steps: string[]
        }>
        recommendation: string
    }> => {
        const response = await api.get("/onboarding/voice-providers")
        return response
    },

    setupVoiceKey: async (data: {
        provider: string
        api_key: string
        name?: string
    }): Promise<any> => {
        const response = await api.post("/onboarding/setup-voice-key", data)
        return response
    },

    getAgentOptions: async (): Promise<{
        voice_providers: string[]
        ai_models: string[]
        voice_options: any[]
    }> => {
        const response = await api.get("/onboarding/agent-options")
        return response
    },

    configureAgent: async (data: {
        name: string
        voice_provider: string
        voice_id: string
        llm_model: string
        system_prompt?: string
    }): Promise<any> => {
        const response = await api.post("/onboarding/configure-agent", data)
        return response
    },

    skip: async (): Promise<any> => {
        const response = await api.post("/onboarding/skip")
        return response
    }
}

// ============================================================================
// NEW: API Keys Management (BYOK)
// ============================================================================
export const apiKeysApi = {
    list: async (): Promise<Array<{
        id: string
        provider: string
        name: string
        masked_key: string
        created_at: string
        last_used_at: string | null
    }>> => {
        const response = await api.get("/keys")
        return response
    },

    create: async (data: {
        provider: string
        api_key: string
        name: string
    }): Promise<any> => {
        const response = await api.post("/keys", data)
        return response
    },

    delete: async (keyId: string): Promise<void> => {
        await api.delete(`/keys/${keyId}`)
    },

    // Simple setup endpoints
    setupKey: async (data: {
        provider: string
        api_key: string
        key_name: string
    }): Promise<any> => {
        const response = await api.post("/setup/api-key", data)
        return response
    },

    getMyKeys: async (): Promise<any> => {
        const response = await api.get("/setup/my-keys")
        return response
    },

    getProviders: async (): Promise<any> => {
        const response = await api.get("/setup/providers")
        return response
    },

    deleteByProvider: async (provider: string): Promise<void> => {
        await api.delete(`/setup/api-key/${provider}`)
    }
}

// ============================================================================
// NEW: Agents API (Voice Agents)
// ============================================================================
export const agentsApi = {
    list: async (params?: {
        status?: string
        skip?: number
        limit?: number
    }): Promise<Array<any>> => {
        const response = await api.get("/agents/", { params })
        return response
    },

    get: async (agentId: string): Promise<any> => {
        const response = await api.get(`/agents/${agentId}`)
        return response
    },

    create: async (data: {
        name: string
        description?: string
        llm_model: string
        llm_temperature: number
        system_prompt: string
        status: string
        voice_settings: any
        webhook_urls: any
    }): Promise<any> => {
        const response = await api.post("/agents/", data)
        return response
    },

    update: async (agentId: string, data: Partial<any>): Promise<any> => {
        const response = await api.put(`/agents/${agentId}`, data)
        return response
    },

    delete: async (agentId: string): Promise<void> => {
        await api.delete(`/agents/${agentId}`)
    },

    deploy: async (agentId: string): Promise<any> => {
        const response = await api.post(`/agents/${agentId}/deploy`)
        return response
    },

    pause: async (agentId: string): Promise<any> => {
        const response = await api.post(`/agents/${agentId}/pause`)
        return response
    },

    activate: async (agentId: string): Promise<any> => {
        const response = await api.post(`/agents/${agentId}/activate`)
        return response
    }
}

// Voice Agent API endpoints (comprehensive dashboard)
export const voiceAgentApi = {
    stats: (): string => `${API_BASE_URL}/voice-agent/stats`,
    phoneNumbers: (): string => `${API_BASE_URL}/voice-agent/numbers`,
    searchNumbers: (): string => `${API_BASE_URL}/voice-agent/search-numbers`,
    purchaseNumber: (): string => `${API_BASE_URL}/voice-agent/purchase-number`,
}

// Agents API with proper typing
export const apiEndpoints = {
    agents: {
        getMyAgent: (): string => `${API_BASE_URL}/agents/my-agent`,
        updateMyAgent: (): string => `${API_BASE_URL}/agents/my-agent`,
        // Deprecated: Old multi-agent endpoints kept for backward compatibility
        list: (): string => `${API_BASE_URL}/agents`,
        get: (id: string): string => `${API_BASE_URL}/agents/${id}`,
        create: (): string => `${API_BASE_URL}/agents`,
        update: (id: string): string => `${API_BASE_URL}/agents/${id}`,
        delete: (id: string): string => `${API_BASE_URL}/agents/${id}`,
    },
    voiceAgent: {
        stats: (): string => `${API_BASE_URL}/voice-agent/stats`,
        phoneNumbers: (): string => `${API_BASE_URL}/voice-agent/numbers`,
        searchNumbers: (): string => `${API_BASE_URL}/voice-agent/search-numbers`,
        purchaseNumber: (): string => `${API_BASE_URL}/voice-agent/purchase-number`,
    },
    phoneNumbers: {
        test: (): string => `${API_BASE_URL}/phone-numbers/test`,
        search: (): string => `${API_BASE_URL}/phone-numbers/search`,
        purchase: (): string => `${API_BASE_URL}/phone-numbers/purchase`,
        list: (): string => `${API_BASE_URL}/phone-numbers/list`,
        assign: (id: string): string => `${API_BASE_URL}/phone-numbers/${id}/assign`,
        delete: (id: string): string => `${API_BASE_URL}/phone-numbers/${id}`,
    },
    onboarding: {
        getStatus: (): string => `${API_BASE_URL}/onboarding/status`,
        skipOnboarding: (): string => `${API_BASE_URL}/onboarding/skip`,
    }
}
