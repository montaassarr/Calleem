"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useConfig } from "@/contexts/ConfigContext";
import { Loader2 } from "lucide-react";

export function OnboardingGuard({ children }: { children: React.ReactNode }) {
    const { config, isLoading } = useConfig();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (isLoading) return;

        // If config is loaded and tenant is NOT configured
        if (config && config.is_configured === false) {
            // Allow access to onboarding page
            if (!pathname.startsWith("/dashboard/onboarding")) {
                router.push("/dashboard/onboarding");
            }
        }
        // If tenant IS configured, prevent access to onboarding page
        else if (config && config.is_configured === true) {
            if (pathname.startsWith("/dashboard/onboarding")) {
                router.push("/dashboard");
            }
        }
    }, [config, isLoading, pathname, router]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    return <>{children}</>;
}
