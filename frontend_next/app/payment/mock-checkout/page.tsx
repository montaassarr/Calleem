"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Loader2 } from "lucide-react";
import api from "@/lib/api";
import { toast } from "sonner";

export default function MockCheckoutPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const sessionId = searchParams.get("session_id");
    const [isProcessing, setIsProcessing] = useState(false);
    const [isComplete, setIsComplete] = useState(false);

    const handleMockPayment = async () => {
        if (!sessionId) {
            toast.error("No session ID found");
            return;
        }

        setIsProcessing(true);

        try {
            // Simulate payment processing delay
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Complete mock checkout
            const response = await api.post(`/billing/mock-complete-checkout?session_id=${sessionId}`);

            setIsComplete(true);
            toast.success(response.message || "🧪 Mock payment successful!");

            // Redirect to success page after 1 second
            setTimeout(() => {
                router.push(`/payment/success?session_id=${sessionId}`);
            }, 1000);

        } catch (error: any) {
            console.error("Mock payment error:", error);
            toast.error(error.response?.data?.detail || "Payment failed");
            setIsProcessing(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            <div className="max-w-md w-full">
                {/* Mock Mode Banner */}
                <div className="mb-6 p-4 rounded-lg bg-amber-500/10 border border-amber-500/30 text-center">
                    <p className="text-amber-400 font-semibold text-sm">
                        🧪 TEST MODE - No Real Charges
                    </p>
                    <p className="text-amber-300/70 text-xs mt-1">
                        This is a simulated payment for testing
                    </p>
                </div>

                {/* Payment Card */}
                <div className="glass rounded-2xl p-8 space-y-6">
                    <div className="text-center space-y-2">
                        <h1 className="text-2xl font-bold text-white">
                            Checkout
                        </h1>
                        <p className="text-slate-300">
                            AI Receptionist Pro
                        </p>
                    </div>

                    {/* Plan Details */}
                    <div className="space-y-3 py-4 border-y border-white/10">
                        <div className="flex justify-between">
                            <span className="text-slate-400">Plan</span>
                            <span className="text-white font-semibold">Pro - Monthly</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-slate-400">Price</span>
                            <span className="text-white font-semibold">$499/month</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-slate-400">Trial Period</span>
                            <span className="text-green-400 font-semibold">14 days free</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-slate-400">Trial Minutes</span>
                            <span className="text-green-400 font-semibold">100 minutes included</span>
                        </div>
                    </div>

                    {/* Today's Charge */}
                    <div className="text-center py-4 bg-slate-900/50 rounded-lg border border-white/5">
                        <p className="text-slate-400 text-sm mb-1">Due Today</p>
                        <p className="text-3xl font-bold text-white">$0.00</p>
                        <p className="text-slate-500 text-xs mt-1">
                            You'll be charged $499 after your trial ends
                        </p>
                    </div>

                    {/* Mock Payment Button */}
                    {!isComplete ? (
                        <Button
                            onClick={handleMockPayment}
                            disabled={isProcessing}
                            className="w-full h-12 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-medium text-lg"
                        >
                            {isProcessing ? (
                                <>
                                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    🧪 Simulate Payment
                                </>
                            )}
                        </Button>
                    ) : (
                        <Button
                            disabled
                            className="w-full h-12 bg-green-600 text-white rounded-xl font-medium text-lg"
                        >
                            <CheckCircle2 className="w-5 h-5 mr-2" />
                            Payment Complete!
                        </Button>
                    )}

                    <div className="text-center">
                        <button
                            onClick={() => router.push("/dashboard")}
                            className="text-slate-400 hover:text-white text-sm transition-colors"
                        >
                            Cancel
                        </button>
                    </div>
                </div>

                {/* Test Instructions */}
                <div className="mt-6 p-4 rounded-lg bg-slate-900/50 border border-white/10">
                    <p className="text-slate-400 text-xs text-center">
                        💡 <span className="text-white font-semibold">Testing Instructions:</span>
                        <br />
                        Click "Simulate Payment" to complete checkout instantly.
                        <br />
                        No real payment processing or charges will occur.
                    </p>
                </div>
            </div>
        </div>
    );
}
