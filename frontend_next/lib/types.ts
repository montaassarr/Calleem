/**
 * TypeScript Type Definitions
 * Complete type system matching backend models
 */

// ============================================
// AUTHENTICATION & USERS
// ============================================

export interface UserCreate {
    username: string;
    email: string;
    password: string;
    full_name: string;
    role?: 'owner' | 'admin' | 'staff' | 'viewer' | 'barber' | 'manager' | 'super_admin';
    business_id?: string;
    tenant_id?: string;
    permissions?: string[];
    active?: boolean;
}

export interface UserUpdate {
    email?: string;
    full_name?: string;
    role?: 'owner' | 'admin' | 'staff' | 'viewer';
    active?: boolean;
}

export interface UserResponse {
    id: string;
    username: string;
    email: string;
    full_name: string;
    role: 'owner' | 'admin' | 'staff' | 'viewer' | 'barber' | 'manager' | 'super_admin';
    business_id?: string;
    tenant_id?: string;
    permissions: string[];
    active: boolean;
    created_at: string;
    updated_at?: string;
    last_login?: string;
}

export interface Token {
    access_token: string;
    token_type: string;
}

export interface LoginCredentials {
    username: string;
    password: string;
}

// ============================================
// APPOINTMENTS
// ============================================

export type AppointmentStatus = 'confirmed' | 'pending' | 'cancelled' | 'completed' | 'no_show';

export interface AppointmentCreate {
    business_id: string;
    location_id: string;
    client_id?: string;
    service_id?: string;
    staff_id?: string;
    client_name: string;
    client_phone: string;
    service: string;
    datetime: string; // ISO 8601 datetime string
    duration_minutes: number;
    source?: string;
    notes?: string;
}

export interface AppointmentUpdate {
    client_name?: string;
    service?: string;
    datetime?: string;
    duration_minutes?: number;
    status?: AppointmentStatus;
    notes?: string;
}

export interface AppointmentResponse {
    id: string;
    business_id: string;
    location_id: string;
    client_id?: string;
    service_id?: string;
    staff_id?: string;
    client_name: string;
    client_phone: string;
    service: string;
    datetime: string;
    start_time: string;
    end_time: string;
    duration_minutes: number;
    status: AppointmentStatus;
    source: string;
    notes?: string;
    created_at: string;
    updated_at: string;
}

export interface AppointmentFilters {
    status?: AppointmentStatus;
    date_from?: string;
    date_to?: string;
    client_phone?: string;
    skip?: number;
    limit?: number;
}

// ============================================
// CONVERSATIONS
// ============================================

export type MessageRole = 'client' | 'ai';

export interface Message {
    role: MessageRole;
    text: string;
    timestamp: string;
    metadata?: Record<string, any>;
}

export interface ConversationState {
    intent: string;
    collected_info: {
        service?: string;
        date?: string;
        time?: string;
        client_name?: string;
        client_phone?: string;
        [key: string]: any;
    };
    next_question?: string;
    completed: boolean;
}

export interface ConversationResponse {
    id: string;
    conversation_id: string;
    business_id: string;
    phone_number: string;
    client_phone: string;
    source: string;
    messages: Message[];
    state: ConversationState;
    appointment_id?: string;
    created_at: string;
    updated_at: string;
    last_updated: string;
}

export interface ConversationFilters {
    search?: string;
    limit?: number;
}

// ============================================
// BUSINESS CONFIG
// ============================================

export interface BusinessConfig {
    business_name: string;
    timezone: string;
    currency: string;
    phone_number?: string;
    email?: string;
    address?: string;
    vapi_api_key?: string;
    twilio_account_sid?: string;
    twilio_auth_token?: string;
    twilio_phone_number?: string;
    system_prompt?: string;
    is_configured?: boolean;
}

// ============================================
// SERVICES
// ============================================

export interface ServiceCreate {
    name: string;
    description: string;
    duration_minutes: number;
    price: number;
    active?: boolean;
}

export interface ServiceUpdate {
    name?: string;
    description?: string;
    duration_minutes?: number;
    price?: number;
    active?: boolean;
}

export interface ServiceResponse {
    id: string;
    name: string;
    description: string;
    duration_minutes: number;
    price: number;
    active: boolean;
    created_at: string;
    updated_at: string;
}

export interface ServiceFilters {
    active_only?: boolean;
    skip?: number;
    limit?: number;
}

// ============================================
// WEBHOOK & TWILIO
// ============================================

export interface WebhookStatus {
    status: 'active' | 'inactive';
    endpoints: {
        sms: string;
        voice: string;
        voice_menu: string;
    };
}

// ============================================
// BUSINESS SETTINGS
// ============================================

export interface OpeningHours {
    day_of_week: number;
    open_time: string;
    close_time: string;
    is_open: boolean;
}

export interface WhatsAppConfiguration {
    phone_number_id: string;
    access_token: string;
    verify_token: string;
    webhook_url: string;
    is_enabled: boolean;
}

export interface BusinessSettings {
    business_name: string;
    business_phone: string;
    business_email: string;
    business_address: string;
    timezone: string;
    opening_hours: OpeningHours[];
    services: ServiceResponse[];
    ai_config: AISettings;
    whatsapp_config: WhatsAppConfiguration;
    features_enabled: FeatureFlags;
}

export interface FeatureFlags {
    voice_agent?: boolean;
    email_notifications?: boolean;
    sms_reminders?: boolean;
    online_booking?: boolean;
    [key: string]: boolean | undefined;
}

// ============================================
// AI CONFIGURATION
// ============================================

export interface AISettings {
    model: string;
    temperature: number;
    max_tokens: number;
    greeting_message: string;
    system_prompt: string;
    tone: 'professional' | 'friendly' | 'casual';
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export interface ChatTestRequest {
    message: string;
    phone_number?: string;
}

// ============================================
// DASHBOARD STATISTICS
// ============================================

export interface DashboardStats {
    total_appointments: number;
    upcoming_appointments: number;
    total_conversations: number;
    completed_conversations: number;
    active_services: number;
    total_users: number;
}

// ============================================
// API RESPONSE WRAPPERS
// ============================================

export interface ApiError {
    detail: string;
    status_code: number;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    skip: number;
    limit: number;
}

// ============================================
// FORM STATES
// ============================================

export interface FormState {
    isSubmitting: boolean;
    error: string | null;
    success: boolean;
}

// ============================================
// CALENDAR EVENT (for appointment display)
// ============================================

export interface CalendarEvent {
    id: string;
    title: string;
    start: Date;
    end: Date;
    backgroundColor?: string;
    borderColor?: string;
    extendedProps?: {
        client_phone: string;
        service: string;
        status: AppointmentStatus;
        notes?: string;
    };
}

// ============================================
// VOICE AGENT
// ============================================

export interface VoiceStartCallRequest {
    customer_number: string;
    customer_name?: string;
    metadata?: Record<string, any>;
}

export interface VoiceStartCallResponse {
    status: string;
    call_id: string;
    assistant_id: string;
}

export interface VoiceTestResponse {
    status: string;
    assistant_id: string | null;
    groq_model: string;
}

export interface VoiceCallHistoryItem {
    id: string;
    call_id?: string;
    status: string;
    customer?: {
        number?: string;
        name?: string;
    };
    cost?: number;
    created_at?: string;
    metadata?: Record<string, any>;
    business_id?: string;
    assistant_id?: string;
}

export interface VoiceCallHistoryResponse {
    items: VoiceCallHistoryItem[];
    count: number;
}

export interface VoiceWebRTCResponse {
    status: string;
    mode: string;
    config?: {
        model?: string;
        voice?: string;
        first_message?: string;
        system_prompt?: string;
    };
    assistant_id?: string;
    public_key?: string;
    session_token?: string;
    expires_at?: string;
    business_id?: string;
    session?: Record<string, any> | null;
}

// Voice Configuration Types
export interface VoiceConfiguration {
    model_provider: string;
    model_name: string;
    temperature: number;
    max_tokens: number;
    voice_provider: string;
    voice_id: string;
    first_message: string;
    system_prompt: string;
    enabled_tools: string[];
    end_call_on_goodbye: boolean;
    record_calls: boolean;
    silence_timeout_seconds: number;
}

export interface VoiceModel {
    id: string;
    name: string;
    provider: string;
}

export interface VoiceOption {
    voice_id: string;
    name: string;
    category: string;
    description?: string;
    provider?: string;
    accent?: string;
    gender?: string;
    age?: string;
    preview_url?: string;
    use_case?: string;
}

export interface VoiceTool {
    type: string;
    function: {
        name: string;
        description: string;
        parameters: {
            type: string;
            properties: Record<string, any>;
            required: string[];
        };
    };
}

// ============================================
// TENANTS (Multi-tenancy)
// ============================================

export type TenantStatus = 'active' | 'suspended' | 'pending';
export type TenantPlan = 'free' | 'premium' | 'enterprise';

export interface TenantCreate {
    owner_id: string;
    name: string;
    country?: string;
    timezone?: string;
    plan?: TenantPlan;
}

export interface TenantUpdate {
    name?: string;
    country?: string;
    timezone?: string;
    plan?: TenantPlan;
    status?: TenantStatus;
}

export interface TenantResponse {
    id: string;
    owner_id: string;
    name: string;
    country?: string;
    timezone: string;
    plan: TenantPlan;
    status: TenantStatus;
    total_calls: number;
    total_minutes: number;
    created_at: string;
    updated_at: string;
}

// ============================================
// LOCATIONS
// ============================================

export interface OpeningHours {
    day: string;
    open: string;
    close: string;
    closed: boolean;
}

export interface Location {
    id: string;
    business_id: string;
    name: string;
    timezone: string;
    opening_hours: OpeningHours[];
}

// ============================================
// STAFF
// ============================================

export interface StaffMember {
    id: string;
    business_id: string;
    name: string;
    services: string[];
    active: boolean;
}

// ============================================
// CRM (Customer Relationship Management)
// ============================================

export interface Client {
    id: string;
    business_id: string;
    name: string;
    phone: string;
    last_visit?: string;
    visit_count: number;
    preferences: Record<string, any>;
}

export interface ClientNote {
    id: string;
    client_id: string;
    author_id: string;
    content: string;
    created_at: string;
}

// ============================================
// CREWAI JOBS
// ============================================

export type CrewJobType = 'cleaning' | 'analytics' | 'insights' | 'revenue_optimization' | 'marketing' | 'quality_assurance';
export type CrewJobStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface CrewJobCreate {
    type: CrewJobType;
    tenant_id: string;
    parameters?: Record<string, any>;
}

export interface CrewJobResponse {
    id: string;
    type: CrewJobType;
    tenant_id: string;
    status: CrewJobStatus;
    result?: any;
    error?: string;
    created_at: string;
    started_at?: string;
    completed_at?: string;
    parameters?: Record<string, any>;
}

// ============================================
// AI INSIGHTS (CrewAI Results)
// ============================================

export interface CustomerInsight {
    segment: string;
    client_count: number;
    characteristics: string[];
    recommendations: string[];
}

export interface RevenueOpportunity {
    type: 'upsell' | 'cross_sell' | 'retention';
    client_id: string;
    client_name: string;
    estimated_value: number;
    confidence: number;
    recommendation: string;
}

export interface MarketingCampaign {
    name: string;
    target_segment: string;
    channel: string;
    message: string;
    expected_roi: number;
}

export interface QualityMetric {
    metric: string;
    score: number;
    trend: 'improving' | 'stable' | 'declining';
    issues: string[];
    recommendations: string[];
}
