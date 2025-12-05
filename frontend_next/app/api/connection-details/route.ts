import { NextResponse } from 'next/server';
import { AccessToken, type AccessTokenOptions, type VideoGrant } from 'livekit-server-sdk';
import { RoomConfiguration } from '@livekit/protocol';

type ConnectionDetails = {
  serverUrl: string;
  roomName: string;
  participantName: string;
  participantToken: string;
};

const API_KEY = process.env.LIVEKIT_API_KEY;
const API_SECRET = process.env.LIVEKIT_API_SECRET;
const LIVEKIT_URL = process.env.LIVEKIT_URL;

export const revalidate = 0;

export async function POST(req: Request) {
  try {
    if (!LIVEKIT_URL || !API_KEY || !API_SECRET) {
      throw new Error('LiveKit configuration missing. Check LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET');
    }

    const body = await req.json();
    const tenantId: string = body?.tenant_id;
    const agentName: string = body?.room_config?.agents?.[0]?.agent_name;

    if (!tenantId) {
      throw new Error('tenant_id is required');
    }

    // Generate room name with tenant prefix for agent to extract
    const participantName = 'user';
    const participantIdentity = `user_${Math.floor(Math.random() * 10_000)}`;
    const roomName = `preview-${tenantId}-${Math.floor(Math.random() * 10_000)}`;

    // Room metadata for agent to identify tenant
    const roomMetadata = JSON.stringify({ tenant_id: tenantId });

    const participantToken = await createParticipantToken(
      { identity: participantIdentity, name: participantName },
      roomName,
      roomMetadata,
      agentName
    );

    const data: ConnectionDetails = {
      serverUrl: LIVEKIT_URL,
      roomName,
      participantToken,
      participantName,
    };

    return NextResponse.json(data, {
      headers: { 'Cache-Control': 'no-store' },
    });
  } catch (error) {
    console.error('Connection details error:', error);
    return new NextResponse(
      error instanceof Error ? error.message : 'Internal error',
      { status: 500 }
    );
  }
}

async function createParticipantToken(
  userInfo: AccessTokenOptions,
  roomName: string,
  roomMetadata: string,
  agentName?: string
): Promise<string> {
  const at = new AccessToken(API_KEY, API_SECRET, {
    ...userInfo,
    ttl: '15m',
  });

  const grant: VideoGrant = {
    room: roomName,
    roomJoin: true,
    roomCreate: true,
    canPublish: true,
    canPublishData: true,
    canSubscribe: true,
  };
  at.addGrant(grant);

  // Set room metadata with tenant info
  at.metadata = roomMetadata;

  if (agentName) {
    at.roomConfig = new RoomConfiguration({
      agents: [{ agentName }],
    });
  }

  return at.toJwt();
}
