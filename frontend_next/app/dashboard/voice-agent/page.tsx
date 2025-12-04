"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Redirect to Control Center
 * This page is kept for backward compatibility
 * All voice agent features are now in the Control Center
 */
export default function VoiceAgentPage() {
    const router = useRouter();

    useEffect(() => {
        router.replace("/dashboard/voice-agent/control-center");
    }, [router]);

    return (
        <div className="flex items-center justify-center h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
        </div>
    );
}
