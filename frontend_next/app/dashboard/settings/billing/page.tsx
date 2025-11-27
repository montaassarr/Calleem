"use client";

import { Button } from "@/components/ui/button";
import { Check, ArrowLeft, CreditCard, Zap, Shield, Star } from "lucide-react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";

export default function BillingPage() {
    const router = useRouter();

    const plans = [
        {
            name: "Basic",
            price: "$149",
            period: "/month",
            description: "Essential AI receptionist for small businesses",
            features: [
                "AI Voice Receptionist",
                "Basic Appointment Booking",
                "Email Notifications",
                "Standard Support",
                "1 Phone Number"
            ],
            current: false,
            popular: false,
            color: "border-white/10",
            buttonVariant: "outline" as const
        },
        {
            name: "Pro",
            price: "$499",
            period: "/month",
            description: "Advanced automation for growing teams",
            features: [
                "Everything in Basic",
                "Smart Automations (n8n)",
                "Team Management",
                "CRM Integrations",
                "Priority Support",
                "3 Phone Numbers"
            ],
            current: true,
            popular: true,
            color: "border-primary/50 bg-primary/5",
            buttonVariant: "default" as const
        },
        {
            name: "Enterprise",
            price: "$999",
            period: "/month",
            description: "Custom solutions for large organizations",
            features: [
                "Everything in Pro",
                "Custom Workflows",
                "Dedicated Account Manager",
                "SLA Guarantees",
                "White-label Options",
                "Unlimited Phone Numbers"
            ],
            current: false,
            popular: false,
            color: "border-purple-500/50 bg-purple-500/5",
            buttonVariant: "outline" as const
        }
    ];

    return (
        <div className="p-6 max-w-6xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-4 mb-8">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => router.push('/dashboard/settings')}
                >
                    <ArrowLeft className="w-5 h-5" />
                </Button>
                <div>
                    <h1 className="text-3xl font-bold mb-2">Billing & Plans</h1>
                    <p className="text-muted-foreground">
                        Manage your subscription and payment methods
                    </p>
                </div>
            </div>

            {/* Current Plan Status */}
            <div className="glass rounded-2xl p-6 mb-10 flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                        <CreditCard className="w-6 h-6 text-green-500" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-lg">Active Subscription: Pro Plan</h3>
                        <p className="text-sm text-muted-foreground">Next billing date: December 27, 2025</p>
                    </div>
                </div>
                <div className="flex gap-3">
                    <Button variant="outline">Update Payment Method</Button>
                    <Button variant="destructive">Cancel Subscription</Button>
                </div>
            </div>

            {/* Plans Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {plans.map((plan) => (
                    <div
                        key={plan.name}
                        className={`relative glass rounded-2xl p-8 border-2 flex flex-col ${plan.color} ${plan.popular ? 'shadow-lg shadow-primary/10' : ''}`}
                    >
                        {plan.popular && (
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                                <Badge className="bg-gradient-to-r from-primary to-accent border-0 px-4 py-1">
                                    Most Popular
                                </Badge>
                            </div>
                        )}

                        <div className="mb-6">
                            <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                            <div className="flex items-baseline gap-1">
                                <span className="text-4xl font-bold">{plan.price}</span>
                                <span className="text-muted-foreground">{plan.period}</span>
                            </div>
                            <p className="text-sm text-muted-foreground mt-3 leading-relaxed">
                                {plan.description}
                            </p>
                        </div>

                        <div className="space-y-4 mb-8 flex-1">
                            {plan.features.map((feature) => (
                                <div key={feature} className="flex items-start gap-3">
                                    <div className="mt-1 w-5 h-5 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                                        <Check className="w-3 h-3 text-primary" />
                                    </div>
                                    <span className="text-sm">{feature}</span>
                                </div>
                            ))}
                        </div>

                        <Button
                            variant={plan.buttonVariant}
                            className={`w-full ${plan.popular ? 'bg-gradient-to-r from-primary to-accent hover:opacity-90' : ''}`}
                            disabled={plan.current}
                        >
                            {plan.current ? "Current Plan" : "Upgrade"}
                        </Button>
                    </div>
                ))}
            </div>

            {/* Enterprise Banner */}
            <div className="mt-10 glass-strong rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 border border-white/10">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                        <Shield className="w-6 h-6 text-blue-500" />
                    </div>
                    <div>
                        <h3 className="font-bold text-lg">Need a custom enterprise solution?</h3>
                        <p className="text-muted-foreground">
                            Get a tailored plan with dedicated infrastructure and custom AI model training.
                        </p>
                    </div>
                </div>
                <Button variant="secondary">Contact Sales</Button>
            </div>
        </div>
    );
}
