import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
            },
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
                // Only redirect to login on 401 if it's not a config fetch
                // Config fetch failures should be handled gracefully by the component
                const isConfigEndpoint = error.config?.url?.includes('/admin/config');

                if (error.response?.status === 401 && !isConfigEndpoint) {
                    // Redirect to login on unauthorized (but not for config fetches)
                    if (typeof window !== 'undefined') {
                        localStorage.removeItem('token');
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('user');
                        window.location.href = '/login';
                    }
                }
                return Promise.reject(error);
            }
        );
    }

    async get<T = any>(url: string, config?: AxiosRequestConfig) {
        const response = await this.client.get<T>(url, config);
        return response.data;
    }

    async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
        const response = await this.client.post<T>(url, data, config);
        return response.data;
    }

    async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
        const response = await this.client.put<T>(url, data, config);
        return response.data;
    }

    async delete<T = any>(url: string, config?: AxiosRequestConfig) {
        const response = await this.client.delete<T>(url, config);
        return response.data;
    }

    async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
        const response = await this.client.patch<T>(url, data, config);
        return response.data;
    }
}

export const apiClient = new ApiClient();
export default apiClient;
