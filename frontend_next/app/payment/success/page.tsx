"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Sparkles, ArrowRight } from "lucide-react";
import confetti from "canvas-confetti";

export default function PaymentSuccessPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const sessionId = searchParams.get("session_id");
    const [countdown, setCountdown] = useState(5);

    useEffect(() => {
        // Trigger confetti animation
        const duration = 3000;
        const animationEnd = Date.now() + duration;

        const randomInRange = (min: number, max: number) => {
            return Math.random() * (max - min) + min;
        };

        const interval = setInterval(() => {
            const timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                clearInterval(interval);
                return;
            }

            confetti({
                particleCount: 3,
                angle: 60,
                spread: 55,
                origin: { x: 0 },
                colors: ["#06b6d4", "#0891b2", "#67e8f9"]
            });

            confetti({
                particleCount: 3,
                angle: 120,
                spread: 55,
                origin: { x: 1 },
                colors: ["#06b6d4", "#0891b2", "#67e8f9"]
            });
        }, 50);

        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        // Auto-redirect countdown
        if (countdown === 0) {
            router.push("/onboarding");
            return;
        }

        const timer = setTimeout(() => {
            setCountdown(countdown - 1);
        }, 1000);

        return () => clearTimeout(timer);
    }, [countdown, router]);

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            <div className="max-w-lg w-full">
                {/* Success Card */}
                <div className="glass rounded-2xl p-8 space-y-6 text-center">
                    {/* Success Icon */}
                    <div className="flex justify-center">
                        <div className="relative">
                            <div className="w-24 h-24 rounded-full bg-green-500/20 flex items-center justify-center">
                                <CheckCircle2 className="w-12 h-12 text-green-400" />
                            </div>
                            <div className="absolute -top-2 -right-2">
                                <Sparkles className="w-8 h-8 text-cyan-400 animate-pulse" />
                            </div>
                        </div>
                    </div>

                    {/* Success Message */}
                    <div className="space-y-2">
                        <h1 className="text-3xl font-bold text-white">
                            Welcome Aboard! 🎉
                        </h1>
                        <p className="text-slate-300 text-lg">
                            Your subscription is now active
                        </p>
                    </div>

                    {/* Plan Details */}
                    <div className="py-6 space-y-3">
                        <div className="p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
                            <p className="text-cyan-400 font-semibold">AI Receptionist Pro</p>
                            <p className="text-cyan-300/70 text-sm mt-1">$499/month</p>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-sm">
                            <div className="p-3 rounded-lg bg-slate-900/50 border border-white/5">
                                <p className="text-slate-400 mb-1">Trial Period</p>
                                <p className="text-white font-semibold">14 Days Free</p>
                            </div>
                            <div className="p-3 rounded-lg bg-slate-900/50 border border-white/5">
                                <p className="text-slate-400 mb-1">Trial Minutes</p>
                                <p className="text-white font-semibold">100 Minutes</p>
                            </div>
                        </div>
                    </div>

                    {/* What's Next */}
                    <div className="text-left p-4 rounded-lg bg-slate-900/50 border border-white/10 space-y-2">
                        <p className="text-white font-semibold text-sm">What's Next?</p>
                        <ul className="text-slate-300 text-sm space-y-1">
                            <li className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                                Set up your API keys
                            </li>
                            <li className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                                Configure your business profile
                            </li>
                            <li className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                                Create your first AI agent
                            </li>
                            <li className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                                Make a test call
                            </li>
                        </ul>
                    </div>

                    {/* CTA Button */}
                    <Button
                        onClick={() => router.push("/onboarding")}
                        className="w-full h-12 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 text-white rounded-xl font-medium text-lg gap-2"
                    >
                        Get Started
                        <ArrowRight className="w-5 h-5" />
                    </Button>

                    {/* Auto-redirect notice */}
                    <p className="text-slate-500 text-xs">
                        Redirecting to onboarding in {countdown} seconds...
                    </p>
                </div>

                {/* Session Info (for debugging) */}
                {sessionId && (
                    <div className="mt-4 p-3 rounded-lg bg-slate-900/50 border border-white/10">
                        <p className="text-slate-500 text-xs font-mono text-center">
                            Session: {sessionId}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
