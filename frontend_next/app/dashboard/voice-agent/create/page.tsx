"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function CreateAgentPage() {
    const router = useRouter();
    useEffect(() => { router.replace("/dashboard/settings/ai"); }, [router]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin text-[#0a4c2f] mx-auto mb-4" />
                <p className="text-gray-500">Redirecting to AI Configuration...</p>
            </div>
        </div>
    );
}
