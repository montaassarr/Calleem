"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Save, ArrowLeft, CheckCircle, XCircle, Eye, EyeOff } from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { businessConfigApi } from "@/lib/api-endpoints";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export default function IntegrationsSettingsPage() {
    const router = useRouter();
    const queryClient = useQueryClient();
    const [showKeys, setShowKeys] = useState({
        groq: false,
        twilio_sid: false,
        twilio_token: false,
    });

    const [settings, setSettings] = useState({
        groq_api_key: "",
        twilio_account_sid: "",
        twilio_auth_token: "",
        twilio_phone_number: "",
        twilio_verify_sid: "",
    });

    const [status, setStatus] = useState({
        groq: false,
        twilio: false,
    });

    const { data: config, isLoading } = useQuery({
        queryKey: ["businessConfig"],
        queryFn: () => businessConfigApi.getConfig(),
    });

    useEffect(() => {
        if (config) {
            setSettings(prev => ({
                ...prev,
                ...config,
                groq_api_key: config.groq_api_key || prev.groq_api_key,
                twilio_account_sid: config.twilio_account_sid || prev.twilio_account_sid,
                twilio_auth_token: config.twilio_auth_token || prev.twilio_auth_token,
                twilio_phone_number: config.twilio_phone_number || prev.twilio_phone_number,
                twilio_verify_sid: config.twilio_verify_sid || prev.twilio_verify_sid,
            }));

            // Simple check for status based on presence of keys
            setStatus({
                groq: !!config.groq_api_key,
                twilio: !!config.twilio_account_sid && !!config.twilio_auth_token,
            });
        }
    }, [config]);

    const updateMutation = useMutation({
        mutationFn: (data: any) => businessConfigApi.updateFeatureFlags(data), // Using updateFeatureFlags as proxy again
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["businessConfig"] });
            toast.success("Integration settings updated successfully");
        },
        onError: () => {
            toast.error("Failed to update integration settings");
        },
    });

    const handleSave = () => {
        // updateMutation.mutate(settings);
        toast.info("Saving settings... (API update needed)");
    };

    const toggleKeyVisibility = (key: keyof typeof showKeys) => {
        setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
    };

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex items-center gap-4 mb-6">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => router.push('/dashboard/settings')}
                >
                    <ArrowLeft className="w-5 h-5" />
                </Button>
                <div>
                    <h1 className="text-3xl font-bold mb-2">Integrations</h1>
                    <p className="text-muted-foreground">
                        Manage API keys and third-party service connections
                    </p>
                </div>
            </div>

            {/* Groq AI */}
            <div className="glass rounded-2xl p-6 max-w-3xl mb-6">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h3 className="text-lg font-semibold">Groq AI</h3>
                        <p className="text-sm text-muted-foreground">Fast AI inference for conversation handling</p>
                    </div>
                    <div className="flex items-center gap-2">
                        {status.groq ? (
                            <>
                                <CheckCircle className="w-5 h-5 text-green-500" />
                                <span className="text-sm text-green-500">Connected</span>
                            </>
                        ) : (
                            <>
                                <XCircle className="w-5 h-5 text-red-500" />
                                <span className="text-sm text-red-500">Not Connected</span>
                            </>
                        )}
                    </div>
                </div>
                <div className="space-y-4">
                    <div>
                        <Label htmlFor="groq_api_key">API Key</Label>
                        <div className="relative mt-2">
                            <Input
                                id="groq_api_key"
                                type={showKeys.groq ? "text" : "password"}
                                value={settings.groq_api_key}
                                onChange={(e) => setSettings({ ...settings, groq_api_key: e.target.value })}
                                className="glass-strong pr-10"
                                placeholder="gsk_..."
                            />
                            <Button
                                variant="ghost"
                                size="icon"
                                className="absolute right-0 top-0"
                                onClick={() => toggleKeyVisibility('groq')}
                            >
                                {showKeys.groq ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </Button>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                            Get your API key from <a href="https://console.groq.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">console.groq.com</a>
                        </p>
                    </div>
                </div>
            </div>

            {/* Twilio */}
            <div className="glass rounded-2xl p-6 max-w-3xl mb-6">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h3 className="text-lg font-semibold">Twilio</h3>
                        <p className="text-sm text-muted-foreground">SMS and WhatsApp messaging platform</p>
                    </div>
                    <div className="flex items-center gap-2">
                        {status.twilio ? (
                            <>
                                <CheckCircle className="w-5 h-5 text-green-500" />
                                <span className="text-sm text-green-500">Connected</span>
                            </>
                        ) : (
                            <>
                                <XCircle className="w-5 h-5 text-red-500" />
                                <span className="text-sm text-red-500">Not Connected</span>
                            </>
                        )}
                    </div>
                </div>
                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="twilio_account_sid">Account SID</Label>
                            <div className="relative mt-2">
                                <Input
                                    id="twilio_account_sid"
                                    type={showKeys.twilio_sid ? "text" : "password"}
                                    value={settings.twilio_account_sid}
                                    onChange={(e) => setSettings({ ...settings, twilio_account_sid: e.target.value })}
                                    className="glass-strong pr-10"
                                    placeholder="AC..."
                                />
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="absolute right-0 top-0"
                                    onClick={() => toggleKeyVisibility('twilio_sid')}
                                >
                                    {showKeys.twilio_sid ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </Button>
                            </div>
                        </div>
                        <div>
                            <Label htmlFor="twilio_auth_token">Auth Token</Label>
                            <div className="relative mt-2">
                                <Input
                                    id="twilio_auth_token"
                                    type={showKeys.twilio_token ? "text" : "password"}
                                    value={settings.twilio_auth_token}
                                    onChange={(e) => setSettings({ ...settings, twilio_auth_token: e.target.value })}
                                    className="glass-strong pr-10"
                                />
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="absolute right-0 top-0"
                                    onClick={() => toggleKeyVisibility('twilio_token')}
                                >
                                    {showKeys.twilio_token ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </Button>
                            </div>
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="twilio_phone_number">Phone Number</Label>
                            <Input
                                id="twilio_phone_number"
                                value={settings.twilio_phone_number}
                                onChange={(e) => setSettings({ ...settings, twilio_phone_number: e.target.value })}
                                className="glass-strong mt-2"
                                placeholder="+1234567890"
                            />
                        </div>
                        <div>
                            <Label htmlFor="twilio_verify_sid">Verify SID (Optional)</Label>
                            <Input
                                id="twilio_verify_sid"
                                value={settings.twilio_verify_sid}
                                onChange={(e) => setSettings({ ...settings, twilio_verify_sid: e.target.value })}
                                className="glass-strong mt-2"
                                placeholder="VA..."
                            />
                        </div>
                    </div>
                    <p className="text-xs text-muted-foreground">
                        Get your credentials from <a href="https://console.twilio.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">console.twilio.com</a>
                    </p>
                </div>
            </div>

            {/* Save Button */}
            <div className="max-w-3xl">
                <div className="flex gap-3">
                    <Button
                        className="gap-2 bg-gradient-to-r from-primary to-accent"
                        onClick={handleSave}
                    >
                        <Save className="w-4 h-4" />
                        Save Integration Settings
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => router.push('/dashboard/settings')}
                    >
                        Cancel
                    </Button>
                </div>
            </div>

            {/* Warning */}
            <div className="glass rounded-lg p-4 max-w-3xl mt-6 border border-yellow-500/20">
                <p className="text-sm text-yellow-600 dark:text-yellow-400">
                    ⚠️ <strong>Security Note:</strong> API keys are sensitive. Never share them publicly. Changes will require a server restart to take effect.
                </p>
            </div>
        </div>
    );
}
