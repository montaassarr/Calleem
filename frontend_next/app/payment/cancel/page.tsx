"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { XCircle, ArrowLeft, HelpCircle } from "lucide-react";

export default function PaymentCancelPage() {
    const router = useRouter();

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            <div className="max-w-md w-full">
                {/* Cancel Card */}
                <div className="glass rounded-2xl p-8 space-y-6 text-center">
                    {/* Cancel Icon */}
                    <div className="flex justify-center">
                        <div className="w-24 h-24 rounded-full bg-amber-500/20 flex items-center justify-center">
                            <XCircle className="w-12 h-12 text-amber-400" />
                        </div>
                    </div>

                    {/* Message */}
                    <div className="space-y-2">
                        <h1 className="text-2xl font-bold text-white">
                            Payment Canceled
                        </h1>
                        <p className="text-slate-300">
                            No charges have been made to your account
                        </p>
                    </div>

                    {/* Help Section */}
                    <div className="text-left p-4 rounded-lg bg-slate-900/50 border border-white/10 space-y-2">
                        <div className="flex items-center gap-2 mb-3">
                            <HelpCircle className="w-4 h-4 text-cyan-400" />
                            <p className="text-white font-semibold text-sm">Have questions?</p>
                        </div>
                        <ul className="text-slate-300 text-sm space-y-1">
                            <li className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                                14-day free trial included
                            </li>
                            <li className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                                No credit card charges during trial
                            </li>
                            <li className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                                Cancel anytime, no commitment
                            </li>
                        </ul>
                    </div>

                    {/* Action Buttons */}
                    <div className="space-y-3">
                        <Button
                            onClick={() => router.push("/signup")}
                            className="w-full h-12 bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 text-white rounded-xl font-medium"
                        >
                            Try Again
                        </Button>

                        <Button
                            onClick={() => router.push("/")}
                            variant="outline"
                            className="w-full h-12 rounded-xl"
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back to Home
                        </Button>
                    </div>
                </div>

                {/* Support Info */}
                <div className="mt-6 p-4 rounded-lg bg-slate-900/50 border border-white/10">
                    <p className="text-slate-400 text-xs text-center">
                        Need help?{" "}
                        <a href="mailto:support@example.com" className="text-cyan-400 hover:text-cyan-300">
                            Contact Support
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );
}
