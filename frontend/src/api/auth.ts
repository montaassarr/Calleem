/**
 * Authentication API Service
 */

import api from '@/lib/api';
import type { LoginCredentials, Token, UserResponse, UserCreate, UserUpdate } from '@/lib/types';

export const authApi = {
  /**
   * Login user and get JWT token
   */
  login: async (credentials: LoginCredentials): Promise<Token> => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post<Token>('/users/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    return response.data;
  },

  /**
   * Register a new user
   */
  register: async (userData: UserCreate): Promise<UserResponse> => {
    const response = await api.post<UserResponse>('/users/register', userData);
    return response.data;
  },

  /**
   * Get current authenticated user
   */
  getCurrentUser: async (): Promise<UserResponse> => {
    const response = await api.get<UserResponse>('/users/me');
    return response.data;
  },

  /**
   * Logout user (client-side only)
   */
  logout: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
  },
};

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
