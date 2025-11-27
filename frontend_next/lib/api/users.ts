import api from '@/lib/api';
import type { UserResponse, UserCreate, UserUpdate } from '@/lib/types';

export const usersApi = {
    /**
     * List all users (admin only)
     */
    list: async (): Promise<UserResponse[]> => {
        const response = await api.get<UserResponse[]>('/users');
        return response.data;
    },

    /**
     * Get user by ID
     */
    get: async (userId: string): Promise<UserResponse> => {
        const response = await api.get<UserResponse>(`/users/${userId}`);
        return response.data;
    },

    /**
     * Create new user (uses register endpoint)
     */
    create: async (data: UserCreate): Promise<UserResponse> => {
        const response = await api.post<UserResponse>('/users/register', data);
        return response.data;
    },

    /**
     * Update user
     */
    update: async (userId: string, data: UserUpdate): Promise<UserResponse> => {
        const response = await api.put<UserResponse>(`/users/${userId}`, data);
        return response.data;
    },

    /**
     * Delete user
     */
    delete: async (userId: string): Promise<void> => {
        await api.delete(`/users/${userId}`);
    },
};
