/**
 * Webhook & Twilio API Service
 */

import api from '@/lib/api';
import type { WebhookStatus } from '@/lib/types';

export const webhookApi = {
  /**
   * Get webhook status
   */
  getStatus: async (): Promise<WebhookStatus> => {
    const response = await api.get<WebhookStatus>('/webhook/status');
    return response.data;
  },
};

// Note: SMS and Voice endpoints are for Twilio webhooks only
// They should not be called directly from the frontend
