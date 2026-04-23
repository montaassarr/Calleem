"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function VoiceAgentPage() {
    const router = useRouter();
    useEffect(() => { router.replace("/dashboard/voice-agent/control-center"); }, [router]);

    return (
        <div className="flex items-center justify-center h-screen">
            <Loader2 className="h-8 w-8 animate-spin text-[#0a4c2f]" />
        </div>
    );
}
