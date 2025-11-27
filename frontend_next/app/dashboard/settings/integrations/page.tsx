"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Save,
    ArrowLeft,
    CheckCircle,
    XCircle,
    Eye,
    EyeOff,
    Bot,
    MessageSquare,
    Calendar,
    CreditCard,
    Slack,
    Database,
    ExternalLink
} from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { businessConfigApi } from "@/lib/api-endpoints";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Switch } from "@/components/ui/switch";

export default function IntegrationsSettingsPage() {
    const router = useRouter();
    const queryClient = useQueryClient();
    const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});

    const [settings, setSettings] = useState({
        openai_api_key: "",
        groq_api_key: "",
        elevenlabs_api_key: "",
        vapi_api_key: "",
        twilio_account_sid: "",
        twilio_auth_token: "",
        twilio_phone_number: "",
        twilio_verify_sid: "",
    });

    const { data: config, isLoading } = useQuery({
        queryKey: ["business-config"],
        queryFn: () => businessConfigApi.getConfig(),
    });

    useEffect(() => {
        if (config) {
            setSettings(prev => ({
                ...prev,
                ...config,
            }));
        }
    }, [config]);

    const updateMutation = useMutation({
        mutationFn: (data: any) => businessConfigApi.updateFeatureFlags(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["business-config"] });
            toast.success("Connections updated successfully");
        },
        onError: () => {
            toast.error("Failed to update connections");
        },
    });

    const handleSave = () => {
        updateMutation.mutate(settings);
    };

    const toggleKeyVisibility = (key: string) => {
        setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const renderApiKeyField = (id: string, label: string, placeholder: string, helpLink?: string) => (
        <div className="mb-4">
            <Label htmlFor={id}>{label}</Label>
            <div className="relative mt-2">
                <Input
                    id={id}
                    type={showKeys[id] ? "text" : "password"}
                    value={(settings as any)[id] || ""}
                    onChange={(e) => setSettings({ ...settings, [id]: e.target.value })}
                    className="glass-strong pr-10"
                    placeholder={placeholder}
                />
                <Button
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0"
                    onClick={() => toggleKeyVisibility(id)}
                >
                    {showKeys[id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
            </div>
            {helpLink && (
                <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                    Get your key from <a href={helpLink} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline flex items-center gap-0.5">{new URL(helpLink).hostname} <ExternalLink className="w-3 h-3" /></a>
                </p>
            )}
        </div>
    );

    const renderConnectionStatus = (isConnected: boolean) => (
        <div className="flex items-center gap-2">
            {isConnected ? (
                <>
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    <span className="text-xs font-medium text-emerald-500">Connected</span>
                </>
            ) : (
                <>
                    <XCircle className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs font-medium text-muted-foreground">Not Connected</span>
                </>
            )}
        </div>
    );

    if (isLoading) {
        return <div className="p-6 text-center text-muted-foreground">Loading connections...</div>;
    }

    return (
        <div className="p-6 max-w-5xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => router.push('/dashboard/settings')}
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold mb-2">Connections</h1>
                        <p className="text-muted-foreground">
                            Manage API keys and third-party integrations
                        </p>
                    </div>
                </div>
                <Button
                    className="gap-2 bg-gradient-to-r from-primary to-accent"
                    onClick={handleSave}
                    disabled={updateMutation.isPending}
                >
                    <Save className="w-4 h-4" />
                    {updateMutation.isPending ? "Saving..." : "Save Changes"}
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* AI Providers */}
                <div className="space-y-6">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                        <Bot className="w-5 h-5 text-primary" />
                        AI Providers
                    </h2>

                    <div className="glass rounded-2xl p-6 space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="font-medium">OpenAI</h3>
                            {renderConnectionStatus(!!settings.openai_api_key)}
                        </div>
                        {renderApiKeyField("openai_api_key", "API Key", "sk-...", "https://platform.openai.com/api-keys")}

                        <div className="border-t border-white/10 my-4" />

                        <div className="flex items-center justify-between">
                            <h3 className="font-medium">Groq</h3>
                            {renderConnectionStatus(!!settings.groq_api_key)}
                        </div>
                        {renderApiKeyField("groq_api_key", "API Key", "gsk_...", "https://console.groq.com/keys")}
                    </div>
                </div>

                {/* Voice Providers */}
                <div className="space-y-6">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                        <MessageSquare className="w-5 h-5 text-primary" />
                        Voice & Telephony
                    </h2>

                    <div className="glass rounded-2xl p-6 space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="font-medium">ElevenLabs</h3>
                            {renderConnectionStatus(!!settings.elevenlabs_api_key)}
                        </div>
                        {renderApiKeyField("elevenlabs_api_key", "API Key", "xi-...", "https://elevenlabs.io/app/settings/api-keys")}

                        <div className="border-t border-white/10 my-4" />

                        <div className="flex items-center justify-between">
                            <h3 className="font-medium">VAPI</h3>
                            {renderConnectionStatus(!!settings.vapi_api_key)}
                        </div>
                        {renderApiKeyField("vapi_api_key", "Private API Key", "...", "https://dashboard.vapi.ai")}

                        <div className="border-t border-white/10 my-4" />

                        <div className="flex items-center justify-between">
                            <h3 className="font-medium">Twilio</h3>
                            {renderConnectionStatus(!!settings.twilio_account_sid && !!settings.twilio_auth_token)}
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            {renderApiKeyField("twilio_account_sid", "Account SID", "AC...", "https://console.twilio.com")}
                            {renderApiKeyField("twilio_auth_token", "Auth Token", "...", "https://console.twilio.com")}
                        </div>
                        {renderApiKeyField("twilio_phone_number", "Phone Number", "+1234567890")}
                    </div>
                </div>

                {/* Workflow Connections */}
                <div className="space-y-6 lg:col-span-2">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                        <Database className="w-5 h-5 text-primary" />
                        Workflow Connections
                    </h2>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Airtable */}
                        <div className="glass rounded-2xl p-6 space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-yellow-500/10 flex items-center justify-center text-yellow-500">
                                        <Database className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h3 className="font-medium">Airtable</h3>
                                        <p className="text-xs text-muted-foreground">For storing call logs</p>
                                    </div>
                                </div>
                                {renderConnectionStatus(!!(settings as any).airtable_api_key)}
                            </div>
                            {renderApiKeyField("airtable_api_key", "Personal Access Token", "pat...", "https://airtable.com/create/tokens")}
                        </div>

                        {/* Google Calendar */}
                        <div className="glass rounded-2xl p-6 space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500">
                                        <Calendar className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h3 className="font-medium">Google Calendar</h3>
                                        <p className="text-xs text-muted-foreground">For syncing appointments</p>
                                    </div>
                                </div>
                                {renderConnectionStatus(!!(settings as any).google_calendar_connected)}
                            </div>

                            <div className="pt-2">
                                {(settings as any).google_calendar_connected ? (
                                    <div className="flex items-center justify-between p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                                        <span className="text-sm font-medium text-emerald-500">Account Connected</span>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="text-red-400 hover:text-red-500 hover:bg-red-500/10"
                                            onClick={() => setSettings({ ...settings, google_calendar_connected: false } as any)}
                                        >
                                            Disconnect
                                        </Button>
                                    </div>
                                ) : (
                                    <Button
                                        className="w-full gap-2 bg-white text-black hover:bg-gray-100"
                                        onClick={() => {
                                            // Simulate OAuth flow
                                            toast.success("Redirecting to Google...");
                                            setTimeout(() => {
                                                setSettings({ ...settings, google_calendar_connected: true } as any);
                                                toast.success("Google Calendar connected!");
                                            }, 1500);
                                        }}
                                    >
                                        <svg className="w-4 h-4" viewBox="0 0 24 24">
                                            <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                            <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                            <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                            <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                        </svg>
                                        Sign in with Google
                                    </Button>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
