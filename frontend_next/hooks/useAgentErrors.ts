import { useEffect } from 'react';
import { useRoomContext } from '@livekit/components-react';
import { toast } from 'sonner';

export function useAgentErrors() {
  const room = useRoomContext();

  useEffect(() => {
    if (!room) return;

    const handleConnectionQualityChanged = () => {
      // Monitor connection quality
      const connectionQuality = room.engine.connectionState;
      if (connectionQuality === 'disconnected' || connectionQuality === 'failed') {
        toast.error('Connection lost', {
          description: 'Trying to reconnect...',
        });
      }
    };

    const handleDisconnected = () => {
      console.log('Room disconnected');
    };

    const handleReconnecting = () => {
      toast.info('Reconnecting...', {
        description: 'Please wait while we restore the connection',
      });
    };

    const handleReconnected = () => {
      toast.success('Reconnected!', {
        description: 'Connection has been restored',
      });
    };

    room.on('connectionStateChanged', handleConnectionQualityChanged);
    room.on('disconnected', handleDisconnected);
    room.on('reconnecting', handleReconnecting);
    room.on('reconnected', handleReconnected);

    return () => {
      room.off('connectionStateChanged', handleConnectionQualityChanged);
      room.off('disconnected', handleDisconnected);
      room.off('reconnecting', handleReconnecting);
      room.off('reconnected', handleReconnected);
    };
  }, [room]);
}
