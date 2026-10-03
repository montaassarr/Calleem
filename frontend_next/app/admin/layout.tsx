"use client";

import { AdminSidebar } from "@/components/admin/AdminSidebar";
import { AdminTopbar } from "@/components/admin/AdminTopbar";
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

    // Dark console theme for the admin area, on <body> so dialogs and menus get it too.
    useEffect(() => {
        document.body.classList.add("admin-theme");
        return () => document.body.classList.remove("admin-theme");
    }, []);

    useEffect(() => {
        if (!isLoading) {
            if (!isAuthenticated) {
                if (pathname !== "/admin/login") {
                    router.push("/admin/login");
                }
            } else if (user?.role !== "super_admin") {
                router.push("/dashboard");
            }
        }
    }, [isLoading, isAuthenticated, user, router, pathname]);

    // Show simplified layout for login page
    if (pathname === "/admin/login") {
        return (
            <div className="min-h-screen bg-background">
                {children}
                <Toaster />
                <Sonner />
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background">
                <div className="flex flex-col items-center gap-4">
                    <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#8cff2e] border-t-transparent" />
                    <p className="text-sm text-muted-foreground">Verifying access...</p>
                </div>
            </div>
        );
    }

    // Access denied state (handled by redirect usually, but prevent flash)
    if (!isAuthenticated || user?.role !== "super_admin") {
        return null;
    }

    return (
        <div className="min-h-screen bg-background">
            <AdminSidebar />
            <div className="ml-[264px] flex min-h-screen flex-col">
                <AdminTopbar />
                <main className="mx-auto w-full max-w-[1320px] flex-1 space-y-8 px-8 py-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
                    {children}
                </main>
            </div>
            <Toaster />
            <Sonner />
        </div>
    );
}
