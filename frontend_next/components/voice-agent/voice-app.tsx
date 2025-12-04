'use client';

import { useEffect } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  StartAudio,
  useVoiceAssistant,
  BarVisualizer,
  VoiceAssistantControlBar,
} from '@livekit/components-react';
import '@livekit/components-styles';

interface VoiceAppProps {
  token: string;
  serverUrl: string;
  onDisconnect?: () => void;
  agentName?: string;
}

export function VoiceApp({ token, serverUrl, onDisconnect, agentName }: VoiceAppProps) {
  return (
    <LiveKitRoom
      token={token}
      serverUrl={serverUrl}
      connect={true}
      audio={true}
      video={false}
      onDisconnected={onDisconnect}
      className="h-full w-full"
    >
      <SimpleVoiceAssistant agentName={agentName} />
      <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
        <StartAudio 
          label="🔊 Click HERE to Enable Audio & Hear AI Voice" 
          className="bg-green-500 hover:bg-green-600 text-white font-bold px-6 py-3 rounded-lg shadow-lg animate-pulse"
        />
      </div>
      <RoomAudioRenderer />
    </LiveKitRoom>
  );
}

function SimpleVoiceAssistant({ agentName }: { agentName?: string }) {
  const { state, audioTrack } = useVoiceAssistant();

  return (
    <div className="flex flex-col items-center justify-center h-full p-8 space-y-6">
      {/* Audio Enable Reminder */}
      {!audioTrack && (
        <div className="bg-yellow-100 dark:bg-yellow-900 border-2 border-yellow-500 rounded-lg p-4 max-w-md text-center">
          <p className="text-yellow-800 dark:text-yellow-200 font-semibold mb-2">
            🔊 Can't Hear the AI?
          </p>
          <p className="text-sm text-yellow-700 dark:text-yellow-300">
            Look for the green "Enable Audio" button at the top and click it!
          </p>
        </div>
      )}

      <div className="text-center space-y-2">
        <h3 className="text-lg font-semibold">
          {state === 'connecting' && '🔌 Connecting to agent...'}
          {state === 'initializing' && '⚙️ Initializing...'}
          {state === 'listening' && '👂 Listening...'}
          {state === 'thinking' && '🤔 Thinking...'}
          {state === 'speaking' && '🗣️ Speaking...'}
          {state === 'disconnected' && '❌ Disconnected'}
        </h3>
        <p className="text-sm text-muted-foreground">
          {agentName && `Agent: ${agentName}`}
        </p>
      </div>

      {audioTrack && (
        <div className="w-full max-w-md">
          <BarVisualizer
            state={state}
            barCount={7}
            trackRef={audioTrack}
            className="h-32"
            options={{ minHeight: 30 }}
          />
        </div>
      )}

      <VoiceAssistantControlBar />
      
      {/* Instructions */}
      <div className="mt-auto text-center space-y-2 text-sm text-muted-foreground max-w-lg">
        <p className="font-semibold">💡 Quick Tips:</p>
        <ul className="text-xs space-y-1">
          <li>• Click the green button above if you can't hear AI</li>
          <li>• Allow microphone access when prompted</li>
          <li>• Speak clearly: "I'd like to book an appointment"</li>
          <li>• AI will respond with voice and book for you</li>
        </ul>
      </div>
    </div>
  );
}
