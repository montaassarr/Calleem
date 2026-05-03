"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Sidebar } from "@/components/dashboard/Sidebar"
import { DashboardHeader } from "@/components/dashboard/DashboardHeader"
import { MobileFootbar } from "@/components/dashboard/MobileFootbar"
import { Loader2 } from "lucide-react"
import { ConfigProvider } from "@/contexts/ConfigContext"
import { TooltipProvider } from "@/components/ui/tooltip"
import { Toaster } from "@/components/ui/toaster"
import { Toaster as Sonner } from "@/components/ui/sonner"
import ErrorBoundary from "@/components/ErrorBoundary"

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const router = useRouter()
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const token = localStorage.getItem("token") || localStorage.getItem("access_token")
        if (!token) {
            router.push("/login")
        } else {
            setIsLoading(false)
        }
    }, [router])

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-white">
                <Loader2 className="h-8 w-8 animate-spin text-[#0a4c2f]" />
            </div>
        )
    }

    return (
        <ErrorBoundary>
            <ConfigProvider>
                <TooltipProvider>
                    <div className="flex bg-white text-gray-800 font-sans h-screen w-screen overflow-hidden md:p-2.5 gap-0 md:gap-2.5 relative">
                        {/* Sidebar panel */}
                        <div className="hidden lg:flex bg-[#f3f5f4] rounded-[32px] flex-shrink-0 relative overflow-hidden shadow-sm">
                            <Sidebar />
                        </div>

                        {/* Main content area */}
                        <div className="flex-1 flex flex-col gap-0 md:gap-2.5 overflow-hidden relative bg-[#f3f5f4] md:bg-transparent">
                            {/* Header panel */}
                            <div className="hidden md:block bg-transparent md:bg-[#f3f5f4] rounded-none md:rounded-[32px] flex-shrink-0 md:overflow-hidden md:shadow-sm z-20">
                                <DashboardHeader />
                            </div>

                            {/* Content panel */}
                            <div className="bg-[#f3f5f4] rounded-none md:rounded-[32px] flex-1 overflow-hidden relative md:shadow-sm">
                                <main className="h-full overflow-y-auto p-4 md:p-8 pt-4 md:pt-6 pb-36 md:pb-8 scroll-smooth relative z-10 scrollbar-hide">
                                    <div className="max-w-[1400px] mx-auto">
                                        {children}
                                    </div>
                                </main>
                            </div>
                        </div>
                    </div>
                    <MobileFootbar />
                    <Toaster />
                    <Sonner />
                </TooltipProvider>
            </ConfigProvider>
        </ErrorBoundary>
    )
}
