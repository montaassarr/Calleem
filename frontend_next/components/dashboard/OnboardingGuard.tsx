"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useConfig } from "@/contexts/ConfigContext";
import { Loader2 } from "lucide-react";

export function OnboardingGuard({ children }: { children: React.ReactNode }) {
    const { config, isLoading, error } = useConfig();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (isLoading) return;

        // If there's an error fetching config (e.g., 401), don't block rendering
        // The dashboard layout will handle auth redirect
        if (error) {
            console.error('Config fetch error:', error);
            return;
        }

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
    }, [config, isLoading, error, pathname, router]);

    // If loading, show spinner
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    // If error, still render children (dashboard layout will handle auth)
    // This prevents blocking the UI on config fetch errors

    return <>{children}</>;
}
