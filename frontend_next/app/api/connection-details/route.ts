import { NextRequest, NextResponse } from 'next/server';

type ConnectionDetails = {
  serverUrl: string;
  roomName: string;
  participantName: string;
  participantToken: string;
};

// Don't cache the results
export const revalidate = 0;

export async function POST(req: NextRequest) {
  try {
    // Get authentication token from Authorization header (client will pass from localStorage)
    const authHeader = req.headers.get('authorization');
    const token = authHeader?.replace('Bearer ', '') || 
                  req.cookies.get('access_token')?.value || 
                  req.cookies.get('token')?.value;

    if (!token) {
      console.error('No authentication token found');
      return new NextResponse('Unauthorized - Please log in', { status: 401 });
    }

    // Parse request body for agent configuration
    const body = await req.json();
    const agentName = body?.room_config?.agents?.[0]?.agent_name;

    console.log('Creating LiveKit session...');

    // Call your backend API to create LiveKit session
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/v1/voice-agent/webrtc/test`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        room_name: body.roomName,
        identity: body.identity,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error:', errorText);
      return new NextResponse(`Backend error: ${errorText}`, { status: response.status });
    }

    const sessionData = await response.json();
    console.log('Backend response:', sessionData);

    // Transform backend response to match LiveKit frontend expectations
    const connectionDetails: ConnectionDetails = {
      serverUrl: sessionData.url || sessionData.server_url || sessionData.serverUrl,
      roomName: sessionData.room_name || sessionData.roomName,
      participantToken: sessionData.token || sessionData.participantToken,
      participantName: sessionData.identity || body.identity || 'user',
    };

    console.log('Returning connection details:', {
      serverUrl: connectionDetails.serverUrl,
      roomName: connectionDetails.roomName,
      participantName: connectionDetails.participantName,
    });

    const headers = new Headers({
      'Cache-Control': 'no-store',
    });

    return NextResponse.json(connectionDetails, { headers });
  } catch (error) {
    console.error('Connection details error:', error);
    if (error instanceof Error) {
      return new NextResponse(error.message, { status: 500 });
    }
    return new NextResponse('Internal server error', { status: 500 });
  }
}
