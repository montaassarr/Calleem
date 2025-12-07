/**
 * LiveKit API Client
 * Handles room management API calls
 */

import api from '@/lib/api';

export interface LiveKitRoom {
  sid?: string;
  name: string;
  num_participants: number;
  max_participants: number;
  created_at?: number;
  empty_timeout: number;
  metadata?: string;
}

export interface LiveKitParticipant {
  sid?: string;
  identity: string;
  name?: string;
  state?: string;
  joined_at?: number;
  metadata?: string;
  is_publisher: boolean;
}

export interface LiveKitStatus {
  configured: boolean;
  server_url: string | null;
  agent_queue: string;
  agent_name: string;
}

export interface CreateRoomRequest {
  room_name: string;
  empty_timeout?: number;
  max_participants?: number;
  metadata?: Record<string, any>;
}

export interface TokenRequest {
  room_name: string;
  participant_identity: string;
  participant_name?: string;
  participant_metadata?: Record<string, any>;
  ttl?: number;
  grants?: Record<string, any>;
}

export interface TokenResponse {
  server_url: string;
  participant_token: string;
}

export const livekitApi = {
  /**
   * Get LiveKit configuration status
   */
  async getStatus(): Promise<LiveKitStatus> {
    return api.get('/livekit/status');
  },

  /**
   * Generate a LiveKit access token
   */
  async generateToken(request: TokenRequest): Promise<TokenResponse> {
    return api.post('/livekit/token', request);
  },

  /**
   * List all rooms for current tenant
   */
  async listRooms(): Promise<LiveKitRoom[]> {
    return api.get('/livekit/rooms');
  },

  /**
   * List all rooms across all tenants (admin only)
   */
  async listAllRooms(): Promise<LiveKitRoom[]> {
    return api.get('/livekit/rooms/all');
  },

  /**
   * Create a new room
   */
  async createRoom(request: CreateRoomRequest): Promise<LiveKitRoom> {
    return api.post('/livekit/rooms', request);
  },

  /**
   * Get room details
   */
  async getRoom(roomName: string): Promise<LiveKitRoom> {
    return api.get(`/livekit/rooms/${encodeURIComponent(roomName)}`);
  },

  /**
   * Delete a room
   */
  async deleteRoom(roomName: string): Promise<{ success: boolean; message: string }> {
    return api.delete(`/livekit/rooms/${encodeURIComponent(roomName)}`);
  },

  /**
   * List participants in a room
   */
  async listParticipants(roomName: string): Promise<LiveKitParticipant[]> {
    return api.get(`/livekit/rooms/${encodeURIComponent(roomName)}/participants`);
  },

  /**
   * Remove a participant from a room
   */
  async removeParticipant(roomName: string, identity: string): Promise<{ success: boolean; message: string }> {
    return api.delete(
      `/livekit/rooms/${encodeURIComponent(roomName)}/participants/${encodeURIComponent(identity)}`
    );
  },
};
