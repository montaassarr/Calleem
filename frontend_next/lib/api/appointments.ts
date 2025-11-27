/**
 * Appointments API Service
 */

import api from '@/lib/api';
import type {
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentFilters,
} from '@/lib/types';

export const appointmentsApi = {
    /**
     * List appointments with optional filters
     */
    list: async (filters?: AppointmentFilters): Promise<AppointmentResponse[]> => {
        const response = await api.get<AppointmentResponse[]>('/appointments', {
            params: filters,
        });
        return response.data;
    },

    /**
     * Get a single appointment by ID
     */
    get: async (appointmentId: string): Promise<AppointmentResponse> => {
        const response = await api.get<AppointmentResponse>(`/appointments/${appointmentId}`);
        return response.data;
    },

    /**
     * Create a new appointment
     */
    create: async (data: AppointmentCreate): Promise<AppointmentResponse> => {
        const response = await api.post<AppointmentResponse>('/appointments', data);
        return response.data;
    },

    /**
     * Update an existing appointment
     */
    update: async (
        appointmentId: string,
        data: AppointmentUpdate
    ): Promise<AppointmentResponse> => {
        const response = await api.put<AppointmentResponse>(
            `/appointments/${appointmentId}`,
            data
        );
        return response.data;
    },

    /**
     * Delete/cancel an appointment
     */
    delete: async (appointmentId: string): Promise<void> => {
        await api.delete(`/appointments/${appointmentId}`);
    },

    /**
     * Cancel an appointment (sets status to cancelled)
     */
    cancel: async (appointmentId: string): Promise<AppointmentResponse> => {
        const response = await api.post<AppointmentResponse>(
            `/appointments/${appointmentId}/cancel`
        );
        return response.data;
    },

    /**
     * Check if a time slot is available
     */
    checkAvailability: async (
        date: string,
        time: string,
        durationMinutes: number = 30
    ): Promise<{
        available: boolean;
        requested_datetime: string;
        duration_minutes: number;
        reason: string;
    }> => {
        const response = await api.get('/appointments/availability/check', {
            params: {
                date,
                time,
                duration_minutes: durationMinutes,
            },
        });
        return response.data;
    },

    /**
     * Get appointment statistics
     */
    getStats: async (): Promise<{
        total: number;
        upcoming: number;
        by_status: Record<string, number>;
    }> => {
        const response = await api.get('/appointments/stats/summary');
        return response.data;
    },

    /**
     * Get appointments for a specific date range
     */
    getByDateRange: async (dateFrom: string, dateTo: string): Promise<AppointmentResponse[]> => {
        return appointmentsApi.list({ date_from: dateFrom, date_to: dateTo });
    },

    /**
     * Get upcoming appointments
     */
    getUpcoming: async (): Promise<AppointmentResponse[]> => {
        const now = new Date().toISOString();
        return appointmentsApi.list({ date_from: now, status: 'confirmed' });
    },

    /**
     * Get appointments for a specific client
     */
    getByPhone: async (clientPhone: string): Promise<AppointmentResponse[]> => {
        return appointmentsApi.list({ client_phone: clientPhone });
    },
};
