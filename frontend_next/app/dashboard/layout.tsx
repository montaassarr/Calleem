"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Sidebar } from "@/components/dashboard/Sidebar"
import { DashboardHeader } from "@/components/dashboard/DashboardHeader"
import { Loader2 } from "lucide-react"
import { ConfigProvider } from "@/contexts/ConfigContext"
import { TooltipProvider } from "@/components/ui/tooltip"
import { Toaster } from "@/components/ui/toaster"
import { Toaster as Sonner } from "@/components/ui/sonner"
import { OnboardingGuard } from "@/components/dashboard/OnboardingGuard"

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const router = useRouter()
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        // Check for token (either 'token' or 'access_token' depending on login implementation)
        const token = localStorage.getItem("token") || localStorage.getItem("access_token")
        if (!token) {
            router.push("/login")
        } else {
            setIsLoading(false)
        }
    }, [router])

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    return (
        <ConfigProvider>
            <TooltipProvider>
                <OnboardingGuard>
                    <div className="min-h-screen bg-background text-foreground">
                        <div
                            className="absolute inset-0 z-0 pointer-events-none"
                            style={{
                                background: "radial-gradient(ellipse 50% 35% at 50% 0%, rgba(226, 232, 240, 0.05), transparent 60%), #000000",
                            }}
                        />
                        <Sidebar />
                        <main className="ml-64 min-h-screen relative z-10">
                            <DashboardHeader />
                            {children}
                        </main>
                        <Toaster />
                        <Sonner />
                    </div>
                </OnboardingGuard>
            </TooltipProvider>
        </ConfigProvider>
    )
}
