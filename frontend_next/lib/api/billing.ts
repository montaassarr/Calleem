import api from '@/lib/api';

export interface BillingSubscriptionStatus {
    status: string;
    plan_name: string;
    plan_price: string;
    trial_end: string | null;
    current_period_end: string;
    cancel_at_period_end: boolean;
    is_mock: boolean;
}

/** The business's prepaid minutes; every call takes its duration from here. */
export interface WalletSummary {
    minutes_balance: number;
    plan: string;
    plan_name: string;
    period_end: string | null;
    calls_paused: boolean;
    low_balance: boolean;
    enforcement_enabled: boolean;
    billing_exempt: boolean;
    fallback_number: string | null;
    /** The monthly plan's usage level, when the business has one. */
    plan_calls: number | null;
    plan_avg_minutes: number | null;
    plan_minutes: number | null;
    plan_price_usd: number | null;
    plan_next: { calls: number; avg_minutes: number; minutes: number; price_usd: number } | null;
}

export interface CheckoutTopup {
    minutes: number;
    price_usd: number;
}

export interface BillingWallet extends WalletSummary {
    tenant_id: string;
    has_subscription: boolean;
    this_month: { calls: number; minutes: number };
    checkout: {
        /** "stripe" once Stripe is live; until then clients request a plan through the contact form. */
        provider: 'stripe' | 'invoice';
        topups: CheckoutTopup[];
        topup_price_per_minute_usd: number;
    };
}

export type CheckoutRequest =
    | { kind: 'plan'; calls: number; avg_minutes: number }
    | { kind: 'minutes'; minutes: number };

export interface WalletHistoryEntry {
    type: 'credit' | 'call';
    minutes: number;
    source: string;
    plan: string | null;
    reference: string | null;
    note: string | null;
    duration_seconds: number | null;
    created_at: string;
}

export interface WalletHistory {
    entries: WalletHistoryEntry[];
    page: number;
    limit: number;
    total: number;
    has_more: boolean;
}

export interface DashboardBillingSummary {
    wallet?: WalletSummary;
    plan: string;
    plan_price: string;
    subscription_status: string;
    current_period_end: string | null;
    assistant_id: string | null;
    usage: {
        total_calls: number;
        total_minutes: number;
        total_cost: number;
        avg_cost_per_minute: number;
    };
    tenant_credit_balance: number | null;
    is_mock: boolean;
}

export const billingApi = {
    getSubscription: async (): Promise<BillingSubscriptionStatus> => {
        return api.get<BillingSubscriptionStatus>('/billing/subscription');
    },

    getDashboardSummary: async (): Promise<DashboardBillingSummary> => {
        return api.get<DashboardBillingSummary>('/billing/dashboard-summary');
    },

    getWallet: async (): Promise<BillingWallet> => {
        return api.get<BillingWallet>('/billing/wallet');
    },

    getHistory: async (page = 1, limit = 20): Promise<WalletHistory> => {
        return api.get<WalletHistory>(`/billing/history?page=${page}&limit=${limit}`);
    },

    setFallbackNumber: async (fallbackNumber: string): Promise<WalletSummary> => {
        return api.put<WalletSummary>('/billing/fallback-number', { fallback_number: fallbackNumber });
    },

    /** Stripe Checkout page for a usage-based monthly plan or a minutes pack. */
    createCheckout: async (request: CheckoutRequest): Promise<{ checkout_url: string }> => {
        return api.post<{ checkout_url: string }>('/billing/checkout', request);
    },

    /** New usage level for an active plan, starting at the next renewal. */
    changePlan: async (calls: number, avgMinutes: number): Promise<{ success: boolean }> => {
        return api.post<{ success: boolean }>('/billing/change-plan', { calls, avg_minutes: avgMinutes });
    },

    /** Stripe customer portal: change plan, update card, cancel, invoices. */
    openPortal: async (): Promise<{ portal_url: string }> => {
        return api.post<{ portal_url: string }>('/billing/portal');
    },
};
