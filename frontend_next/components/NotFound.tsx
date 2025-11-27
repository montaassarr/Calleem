"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { Home, ArrowLeft, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

export default function NotFound() {
    const router = useRouter();
    const [countdown, setCountdown] = useState(5);

    useEffect(() => {
        const timer = setInterval(() => {
            setCountdown((prev) => {
                if (prev <= 1) {
                    clearInterval(timer);
                    router.push("/dashboard");
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [router]);

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-background to-muted p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <GlassCard className="max-w-md w-full p-8 text-center space-y-6 border-white/10">
                    <div className="relative w-24 h-24 mx-auto mb-4">
                        <div className="absolute inset-0 bg-primary/20 rounded-full animate-pulse" />
                        <div className="absolute inset-0 flex items-center justify-center">
                            <AlertCircle className="w-12 h-12 text-primary" />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <h1 className="text-4xl font-bold tracking-tight">404</h1>
                        <h2 className="text-xl font-semibold text-foreground/80">Page Not Found</h2>
                        <p className="text-muted-foreground">
                            Oops! The page you're looking for doesn't exist or has been moved.
                        </p>
                    </div>

                    <div className="p-4 bg-muted/50 rounded-lg border border-border/50">
                        <p className="text-sm font-medium">
                            Redirecting to dashboard in <span className="text-primary font-bold">{countdown}</span> seconds...
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
                        <Button
                            variant="outline"
                            onClick={() => router.back()}
                            className="gap-2"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Go Back
                        </Button>
                        <Button
                            onClick={() => router.push("/dashboard")}
                            className="gap-2"
                        >
                            <Home className="w-4 h-4" />
                            Dashboard
                        </Button>
                    </div>
                </GlassCard>
            </motion.div>
        </div>
    );
}
