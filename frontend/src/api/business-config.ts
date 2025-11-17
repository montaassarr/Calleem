/**
 * Business Configuration API Client
 * Handles all business config operations including AI settings, services, and WhatsApp config
 */

import api from '@/lib/api';

export interface OpeningHours {
  day_of_week: number; // 0=Monday, 6=Sunday
  open_time: string; // "HH:MM"
  close_time: string; // "HH:MM"
  is_open: boolean;
}

export interface ServiceDefinition {
  name: string;
  duration_minutes: number;
  price: number;
  description?: string;
  is_active?: boolean;
}

export interface AIConfiguration {
  model?: string;
  temperature?: number;
  max_tokens?: number;
  system_prompt?: string;
}

export interface WhatsAppConfiguration {
  phone_number_id?: string;
  access_token?: string;
  verify_token?: string;
  webhook_url?: string;
}

export interface BusinessConfig {
  business_id: string;
  business_name: string;
  business_email?: string;
  business_phone?: string;
  business_address?: string;
  timezone: string;
  opening_hours: OpeningHours[];
  services: ServiceDefinition[];
  ai_config: AIConfiguration;
  whatsapp_config: WhatsAppConfiguration;
  created_at?: string;
  updated_at?: string;
}

export interface BusinessConfigUpdate {
  business_name?: string;
  business_email?: string;
  business_phone?: string;
  business_address?: string;
  timezone?: string;
  opening_hours?: OpeningHours[];
  services?: ServiceDefinition[];
  ai_config?: AIConfiguration;
  whatsapp_config?: WhatsAppConfiguration;
}

export const businessConfigApi = {
  /**
   * Get current business configuration
   */
  getConfig: async (businessId: string = 'default'): Promise<BusinessConfig> => {
    const response = await api.get<BusinessConfig>('/business/config', {
      headers: { 'X-Business-ID': businessId }
    });
    return response.data;
  },

  /**
   * Update business configuration
   */
  updateConfig: async (
    data: BusinessConfigUpdate,
    businessId: string = 'default'
  ): Promise<BusinessConfig> => {
    const response = await api.put<BusinessConfig>('/business/config', data, {
      headers: { 'X-Business-ID': businessId }
    });
    return response.data;
  },

  /**
   * Reload configuration (invalidate cache)
   */
  reloadConfig: async (businessId: string = 'default'): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/business/config/reload', {}, {
      headers: { 'X-Business-ID': businessId }
    });
    return response.data;
  },

  /**
   * Get AI prompt configuration
   */
  getAIPrompt: async (businessId: string = 'default'): Promise<{ system_prompt: string }> => {
    const response = await api.get<{ system_prompt: string }>('/business/config/ai-prompt', {
      headers: { 'X-Business-ID': businessId }
    });
    return response.data;
  },

  /**
   * Update AI prompt
   */
  updateAIPrompt: async (
    systemPrompt: string,
    businessId: string = 'default'
  ): Promise<BusinessConfig> => {
    const response = await api.put<BusinessConfig>(
      '/business/config/ai-prompt',
      { system_prompt: systemPrompt },
      {
        headers: { 'X-Business-ID': businessId }
      }
    );
    return response.data;
  },

  /**
   * Update WhatsApp configuration
   */
  updateWhatsAppConfig: async (
    config: WhatsAppConfiguration,
    businessId: string = 'default'
  ): Promise<BusinessConfig> => {
    const response = await api.put<BusinessConfig>('/business/config/whatsapp', config, {
      headers: { 'X-Business-ID': businessId }
    });
    return response.data;
  },

  /**
   * Get services list
   */
  getServices: async (businessId: string = 'default'): Promise<ServiceDefinition[]> => {
    const response = await api.get<ServiceDefinition[]>('/business/config/services', {
      headers: { 'X-Business-ID': businessId }
    });
    return response.data;
  },
};
