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
} from "@/lib/types"

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
    list: async (params?: { search?: string; limit?: number }): Promise<any[]> => {
        const response = await api.get("/conversations", {
            params
        })
        return response
    },

    get: async (id: string): Promise<any> => {
        const response = await api.get(`/conversations/${id}`)
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
    list: async (tenantId?: string): Promise<any[]> => {
        const response = await api.get("/admin/users", {
            params: { tenant_id: tenantId }
        })
        return response
    },

    create: async (data: any): Promise<any> => {
        const response = await api.post("/admin/users", data)
        return response
    },

    delete: async (id: string): Promise<void> => {
        await api.delete(`/admin/users/${id}`)
    }
}

export const voiceApi = {
    testAgent: async (): Promise<any> => {
        const response = await api.get("/voice-agent/status")
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

    webrtcTest: async (): Promise<any> => {
        const response = await api.post("/voice-agent/webrtc/test")
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
