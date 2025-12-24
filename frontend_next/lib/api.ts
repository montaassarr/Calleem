import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

// Get API URL from environment variable
// In production (Vercel), this MUST be set to the Railway backend URL
// Example: https://your-app-name.up.railway.app
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ||
    (typeof window !== 'undefined' && window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : '');

// Validate API URL in production
if (typeof window !== 'undefined' && !BASE_URL && window.location.hostname !== 'localhost') {
    console.error(
        '❌ NEXT_PUBLIC_API_URL is not set! ' +
        'Please set it in Vercel environment variables to your Railway backend URL.'
    );
}

// Check for placeholder URLs
if (BASE_URL && BASE_URL.includes('your-railway-url')) {
    console.error(
        '❌ NEXT_PUBLIC_API_URL contains placeholder value! ' +
        'Please update it in Vercel environment variables to your actual Railway backend URL.'
    );
}

const API_BASE_URL = BASE_URL ? `${BASE_URL}/api/v1` : '/api/v1';

class ApiClient {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
            },
            // Required for cross-origin requests with credentials (cookies, auth headers)
            withCredentials: true,
        });

        // Request interceptor to add auth token and tenant ID
        this.client.interceptors.request.use(
            (config) => {
                const token = localStorage.getItem('access_token');
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }

                // Add X-Tenant-ID header if available
                const tenantId = localStorage.getItem('tenant_id');
                if (tenantId) {
                    config.headers['X-Tenant-ID'] = tenantId;
                }

                // Fallback: try to get tenant_id from user object
                if (!tenantId) {
                    const userStr = localStorage.getItem('user');
                    if (userStr) {
                        try {
                            const user = JSON.parse(userStr);
                            if (user.tenant_id) {
                                config.headers['X-Tenant-ID'] = user.tenant_id;
                                // Cache it for next time
                                localStorage.setItem('tenant_id', user.tenant_id);
                            }
                        } catch (e) {
                            console.error('Error parsing user data:', e);
                        }
                    }
                }

                return config;
            },
            (error) => Promise.reject(error)
        );

        // Response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                // Log error details for debugging
                if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
                    console.error('API Error:', {
                        url: error.config?.url,
                        method: error.config?.method,
                        status: error.response?.status,
                        data: error.response?.data,
                    });
                }

                // Only redirect to login on 401 if it's not a config fetch
                // Config fetch failures should be handled gracefully by the component
                const isConfigEndpoint = error.config?.url?.includes('/admin/config');
                const isWhatsAppStatus = error.config?.url?.includes('/whatsapp/status');

                if (error.response?.status === 401 && !isConfigEndpoint && !isWhatsAppStatus) {
                    // Redirect to login on unauthorized (but not for config fetches)
                    if (typeof window !== 'undefined') {
                        localStorage.removeItem('token');
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('user');
                        localStorage.removeItem('tenant_id');
                        window.location.href = '/login';
                    }
                }

                // Enhance error object with more details
                if (error.response) {
                    error.message = error.response.data?.detail || error.response.data?.message || error.message;
                }

                return Promise.reject(error);
            }
        );
    }

    async get<T = any>(url: string, config?: AxiosRequestConfig) {
        try {
            const response = await this.client.get<T>(url, config);
            return response.data;
        } catch (error: any) {
            throw this.handleError(error);
        }
    }

    async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
        try {
            const response = await this.client.post<T>(url, data, config);
            return response.data;
        } catch (error: any) {
            throw this.handleError(error);
        }
    }

    async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
        try {
            const response = await this.client.put<T>(url, data, config);
            return response.data;
        } catch (error: any) {
            throw this.handleError(error);
        }
    }

    async delete<T = any>(url: string, config?: AxiosRequestConfig) {
        try {
            const response = await this.client.delete<T>(url, config);
            return response.data;
        } catch (error: any) {
            throw this.handleError(error);
        }
    }

    async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
        try {
            const response = await this.client.patch<T>(url, data, config);
            return response.data;
        } catch (error: any) {
            throw this.handleError(error);
        }
    }

    private handleError(error: any) {
        // Extract meaningful error message
        const message = error.response?.data?.detail
            || error.response?.data?.message
            || error.message
            || 'An unexpected error occurred';

        return {
            message,
            status: error.response?.status,
            data: error.response?.data,
        };
    }
}

export const apiClient = new ApiClient();
export default apiClient;
