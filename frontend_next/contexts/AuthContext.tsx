"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import { UserResponse, LoginCredentials, UserCreate } from '@/lib/types';

interface AuthContextType {
    user: UserResponse | null;
    isLoading: boolean;
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (data: UserCreate) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<UserResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();
    const pathname = usePathname();

    // Check for existing session on mount
    useEffect(() => {
        const initAuth = async () => {
            if (typeof window === 'undefined') return;

            const token = localStorage.getItem('access_token');
            if (!token) {
                setIsLoading(false);
                return;
            }

            try {
                const userData = await authApi.getCurrentUser();
                setUser(userData);

                // Store tenant_id for API interceptor
                if (userData.tenant_id) {
                    localStorage.setItem('tenant_id', userData.tenant_id);
                }
            } catch (error) {
                console.error('Failed to restore session:', error);
                localStorage.removeItem('access_token');
                localStorage.removeItem('tenant_id');
            } finally {
                setIsLoading(false);
            }
        };

        initAuth();
    }, []);

    const login = async (credentials: LoginCredentials) => {
        setIsLoading(true);
        try {
            const token = await authApi.login(credentials);
            localStorage.setItem('access_token', token.access_token);

            // Fetch user profile immediately
            const userData = await authApi.getCurrentUser();
            setUser(userData);

            if (userData.tenant_id) {
                localStorage.setItem('tenant_id', userData.tenant_id);
            }

            // Redirect based on role
            if (userData.role === 'super_admin') {
                router.push('/admin/dashboard');
            } else {
                router.push('/dashboard');
            }
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        } finally {
            setIsLoading(false);
        }
    };

    const register = async (data: UserCreate) => {
        setIsLoading(true);
        try {
            await authApi.register(data);
            // Auto login after registration
            await login({
                username: data.email, // Assuming email is username
                password: data.password
            });
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        authApi.logout();
        localStorage.removeItem('tenant_id');
        setUser(null);
        router.push('/login');
    };

    return (
        <AuthContext.Provider value={{
            user,
            isLoading,
            login,
            register,
            logout,
            isAuthenticated: !!user
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
