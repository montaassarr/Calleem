"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { businessConfigApi } from "@/lib/api-endpoints";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import {
    Zap,
    Calendar,
    MessageSquare,
    Sheet,
    Users,
    CheckCircle2,
    Loader2,
    Lock,
    Crown,
    Sparkles
} from "lucide-react";
import { useRouter } from "next/navigation";

interface Automation {
    id: string;
    title: string;
    description: string;
    icon: any;
    color: string;
    gradient: string;
}

const AUTOMATIONS: Automation[] = [
    {
        id: "google_calendar_sync",
        title: "Sync to Google Calendar",
        description: "Automatically add new appointments to your Google Calendar in real-time.",
        icon: Calendar,
        color: "text-blue-500",
        gradient: "from-blue-500/20 to-blue-600/10"
    },
    {
        id: "airtable_sync",
        title: "Save to Airtable",
        description: "Log all call data, transcripts, and customer info to your Airtable base.",
        icon: Sheet,
        color: "text-orange-500",
        gradient: "from-orange-500/20 to-orange-600/10"
    },
    {
        id: "whatsapp_confirmation",
        title: "WhatsApp/SMS Confirmation",
        description: "Send automatic booking confirmations via WhatsApp or SMS to customers.",
        icon: MessageSquare,
        color: "text-green-500",
        gradient: "from-green-500/20 to-green-600/10"
    },
    {
        id: "hubspot_contact",
        title: "Create HubSpot Contact",
        description: "Automatically create or update contacts in HubSpot CRM from call data.",
        icon: Users,
        color: "text-purple-500",
        gradient: "from-purple-500/20 to-purple-600/10"
    },
    {
        id: "slack_notification",
        title: "Post to Slack",
        description: "Get instant Slack notifications when new appointments are booked.",
        icon: MessageSquare,
        color: "text-pink-500",
        gradient: "from-pink-500/20 to-pink-600/10"
    },
];

export default function AutomationsPage() {
    const queryClient = useQueryClient();
    const router = useRouter();
    const [localAutomations, setLocalAutomations] = useState<Record<string, boolean>>({});
    const [hasChanges, setHasChanges] = useState(false);

    // Fetch current config
    const { data: config, isLoading } = useQuery({
        queryKey: ["business-config"],
        queryFn: () => businessConfigApi.getConfig(),
    });

    // Check if user is on Pro plan
    const isPro = config?.plan === "pro" || config?.plan === "enterprise";

    // Initialize local state from config
    useEffect(() => {
        if (config?.automations) {
            setLocalAutomations(config.automations);
        }
    }, [config]);

    // Mutation to save all automations
    const saveMutation = useMutation({
        mutationFn: async () => {
            const response = await fetch("/api/v1/automations/update", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                },
                body: JSON.stringify({ automations: localAutomations })
            });

            if (!response.ok) {
                throw new Error("Failed to update automations");
            }

            return response.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["business-config"] });
            toast.success("Automations saved successfully!");
            setHasChanges(false);
        },
        onError: () => {
            toast.error("Failed to save automations");
        },
    });

    const handleToggle = (id: string, checked: boolean) => {
        if (!isPro) {
            toast.error("Upgrade to Pro to unlock Smart Automations");
            router.push("/dashboard/settings/billing");
            return;
        }

        setLocalAutomations(prev => ({
            ...prev,
            [id]: checked
        }));
        setHasChanges(true);
    };

    const handleSave = () => {
        saveMutation.mutate();
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-[50vh]">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="p-6 space-y-8 max-w-6xl mx-auto">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Zap className="w-8 h-8 text-yellow-500 fill-yellow-500" />
                        Smart Automations
                        {isPro && (
                            <Badge className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white border-0">
                                <Crown className="w-3 h-3 mr-1" />
                                PRO
                            </Badge>
                        )}
                    </h1>
                    <p className="text-muted-foreground mt-2 text-lg">
                        Connect your AI receptionist to your favorite tools.
                        Powered by n8n automation engine.
                    </p>
                </div>
                <div className="glass px-4 py-2 rounded-full flex items-center gap-2 text-sm font-medium text-emerald-500 border border-emerald-500/20 bg-emerald-500/10">
                    <CheckCircle2 className="w-4 h-4" />
                    n8n Engine Active
                </div>
            </div>

            {/* Plan Gate Warning */}
            {!isPro && (
                <Card className="border-yellow-500/50 bg-gradient-to-r from-yellow-500/10 to-orange-500/10">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Lock className="w-5 h-5 text-yellow-500" />
                            Pro Feature
                        </CardTitle>
                        <CardDescription>
                            Smart Automations are available on the Pro plan ($499/month).
                            Upgrade now to unlock powerful workflow automation.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button
                            onClick={() => router.push("/dashboard/settings/billing")}
                            className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600"
                        >
                            <Crown className="w-4 h-4 mr-2" />
                            Upgrade to Pro
                        </Button>
                    </CardContent>
                </Card>
            )}

            {/* Automations Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {AUTOMATIONS.map((auto) => {
                    const isEnabled = localAutomations[auto.id] || false;

                    return (
                        <Card
                            key={auto.id}
                            className={`
                                relative group overflow-hidden transition-all duration-300
                                ${isEnabled && isPro
                                    ? `bg-gradient-to-br ${auto.gradient} border-primary/20 shadow-lg shadow-primary/5`
                                    : "glass border-white/10 hover:border-white/20"
                                }
                                ${!isPro ? "opacity-60" : ""}
                            `}
                        >
                            <CardHeader>
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex gap-4">
                                        <div className={`
                                            w-12 h-12 rounded-xl flex items-center justify-center shrink-0
                                            ${isEnabled && isPro ? "bg-primary/20" : "bg-white/5"}
                                        `}>
                                            <auto.icon className={`w-6 h-6 ${auto.color}`} />
                                        </div>
                                        <div className="space-y-1">
                                            <CardTitle className="text-lg flex items-center gap-2">
                                                {auto.title}
                                                {!isPro && <Lock className="w-4 h-4 text-yellow-500" />}
                                            </CardTitle>
                                            <CardDescription className="text-sm leading-relaxed">
                                                {auto.description}
                                            </CardDescription>
                                        </div>
                                    </div>
                                    <Switch
                                        checked={isEnabled}
                                        onCheckedChange={(checked) => handleToggle(auto.id, checked)}
                                        disabled={!isPro}
                                        className="data-[state=checked]:bg-primary"
                                    />
                                </div>
                            </CardHeader>

                            {/* Status Footer */}
                            {isEnabled && isPro && (
                                <CardContent className="pt-0">
                                    <div className="px-4 py-2 bg-white/5 rounded-lg flex items-center justify-between">
                                        <span className="text-xs text-muted-foreground font-medium">
                                            Status: <span className="text-emerald-500">Active</span>
                                        </span>
                                        <Sparkles className="w-4 h-4 text-primary" />
                                    </div>
                                </CardContent>
                            )}
                        </Card>
                    );
                })}
            </div>

            {/* Save Button */}
            {isPro && hasChanges && (
                <div className="fixed bottom-6 right-6 z-50">
                    <Button
                        onClick={handleSave}
                        disabled={saveMutation.isPending}
                        size="lg"
                        className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-2xl shadow-primary/50"
                    >
                        {saveMutation.isPending ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Saving...
                            </>
                        ) : (
                            <>
                                <CheckCircle2 className="w-4 h-4 mr-2" />
                                Save Automations
                            </>
                        )}
                    </Button>
                </div>
            )}

            {/* Enterprise Banner */}
            <Card className="glass-strong border border-primary/20 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-primary/10 opacity-50" />
                <CardContent className="relative z-10 p-8 text-center space-y-4">
                    <h3 className="text-xl font-bold">Need a custom workflow?</h3>
                    <p className="text-muted-foreground max-w-lg mx-auto">
                        Our Enterprise plan includes dedicated n8n workflow development.
                        We build custom integrations tailored to your business needs.
                    </p>
                    <Button variant="outline">
                        Contact Sales
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}
