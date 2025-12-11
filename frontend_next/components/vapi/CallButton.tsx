"use client";

import React from 'react';
import { useVapi } from './VapiProvider';
import { Button } from '@/components/ui/button';
import { Mic, PhoneOff, Loader2 } from 'lucide-react';

interface CallButtonProps {
    assistantId: string;
    onCallStart?: () => void;
    onCallEnd?: () => void;
    className?: string;
}

export function CallButton({ assistantId, onCallStart, onCallEnd, className }: CallButtonProps) {
    const { startCall, stopCall, status } = useVapi();

    const handleToggleCall = async () => {
        if (status === 'connected' || status === 'connecting') {
            stopCall();
            if (onCallEnd) onCallEnd();
        } else {
            if (onCallStart) onCallStart();
            await startCall(assistantId);
        }
    };

    return (
        <Button
            onClick={handleToggleCall}
            variant={status === 'connected' ? "destructive" : "default"}
            size="lg"
            className={`gap-2 min-w-[150px] ${className}`}
            disabled={status === 'connecting'}
        >
            {status === 'connecting' ? (
                <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Connecting...
                </>
            ) : status === 'connected' ? (
                <>
                    <PhoneOff className="h-4 w-4" />
                    End Call
                </>
            ) : (
                <>
                    <Mic className="h-4 w-4" />
                    Start Call
                </>
            )}
        </Button>
    );
}
