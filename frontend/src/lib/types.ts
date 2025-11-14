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
  role?: 'admin' | 'staff';
  active?: boolean;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  role?: 'admin' | 'staff';
  active?: boolean;
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'staff';
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

export type AppointmentStatus = 'confirmed' | 'cancelled' | 'completed' | 'no_show';

export interface AppointmentCreate {
  client_name: string;
  client_phone: string;
  service: string;
  datetime: string; // ISO 8601 datetime string
  duration_minutes: number;
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
  client_name: string;
  client_phone: string;
  service: string;
  datetime: string;
  duration_minutes: number;
  status: AppointmentStatus;
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
    datetime?: string;
    client_name?: string;
    phone_number?: string;
    [key: string]: any;
  };
  awaiting_field?: string;
}

export interface ConversationResponse {
  id: string;
  conversation_id: string;
  phone_number: string;
  messages: Message[];
  state: ConversationState;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationFilters {
  search?: string;
  limit?: number;
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

export interface BusinessSettings {
  business_name: string;
  business_phone: string;
  business_email: string;
  business_address: string;
  business_hours: string;
  timezone: string;
  available_services: string;
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
