"use client";

import { AdminSidebar } from "@/components/admin/AdminSidebar";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { user, isLoading, isAuthenticated } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (!isLoading) {
            if (!isAuthenticated) {
                if (pathname !== "/admin/login") {
                    router.push("/admin/login");
                }
            } else if (!["super_admin", "owner", "admin"].includes(user?.role || "")) {
                router.push("/dashboard");
            }
        }
    }, [isLoading, isAuthenticated, user, router, pathname]);

    // Show simplified layout for login page
    if (pathname === "/admin/login") {
        return (
            <div className="min-h-screen bg-slate-950">
                {children}
                <Toaster />
                <Sonner />
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950">
                <div className="flex flex-col items-center gap-4">
                    <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                    <p className="text-sm text-muted-foreground">Verifying access...</p>
                </div>
            </div>
        );
    }

    // Access denied state (handled by redirect usually, but prevent flash)
    if (!isAuthenticated || !["super_admin", "owner", "admin"].includes(user?.role || "")) {
        return null;
    }

    return (
        <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
            <AdminSidebar />
            <main className="flex-1 ml-64 p-8 overflow-y-auto h-screen">
                <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {children}
                </div>
            </main>
            <Toaster />
            <Sonner />
        </div>
    );
}
