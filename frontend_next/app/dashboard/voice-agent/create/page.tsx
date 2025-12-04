"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * DEPRECATED: This page has been replaced by the AI settings page.
 * Redirects to the settings/ai page where users manage their single agent.
 */
export default function CreateAgentPage() {
    const router = useRouter();

    useEffect(() => {
        router.replace("/dashboard/settings/ai");
    }, [router]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
                <p className="text-muted-foreground">Redirecting to AI Configuration...</p>
            </div>
        </div>
    );
}
