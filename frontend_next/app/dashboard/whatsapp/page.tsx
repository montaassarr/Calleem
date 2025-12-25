"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Smartphone, CheckCircle2, XCircle, Copy, ExternalLink } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { webhookApi } from "@/lib/api-endpoints";
import { toast } from "sonner";

export default function WhatsAppPage() {
    const { data: webhookStatus, isLoading } = useQuery({
        queryKey: ["webhook-status"],
        queryFn: () => webhookApi.getStatus(),
    });

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        toast.success("Copied!", {
            description: "Webhook URL copied to clipboard",
        });
    };

    const getWebhookUrl = (endpoint: string) =>{
        // In Next.js, we use NEXT_PUBLIC_ prefix for client-side env vars
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 
          (typeof window !== 'undefined' && window.location.hostname === 'localhost' 
            ? 'http://localhost:8000' 
            : '');
        
        // Check for placeholder URLs
        if (baseUrl && baseUrl.includes('your-railway-url')) {
            console.error('❌ NEXT_PUBLIC_API_URL contains placeholder value! Please update it in Vercel environment variables.');
        }
        
        return baseUrl ? `${baseUrl}/api/v1${endpoint}` : `/api/v1${endpoint}`;
    };

    return (
        <div className="p-6">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold mb-2">WhatsApp & SMS Integration</h1>
                <p className="text-muted-foreground">Configure your Twilio webhooks and test messaging</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Status Card */}
                <div className="bg-white border border-slate-200 shadow-sm rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                            <Smartphone className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-lg">Webhook Status</h3>
                            <p className="text-sm text-muted-foreground">Real-time connection status</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 bg-white border border-slate-200 shadow-sm rounded-lg">
                            <span className="font-medium">Overall Status</span>
                            {isLoading ? (
                                <span className="text-sm text-muted-foreground">Checking...</span>
                            ) : webhookStatus?.status === 'active' ? (
                                <div className="flex items-center gap-2">
                                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                                    <span className="text-green-700 font-medium">Active</span>
                                </div>
                            ) : (
                                <div className="flex items-center gap-2">
                                    <XCircle className="w-5 h-5 text-red-500" />
                                    <span className="text-red-700 font-medium">Inactive</span>
                                </div>
                            )}
                        </div>

                        <div className="p-4 bg-white border border-slate-200 shadow-sm rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium">SMS Webhook</span>
                                <CheckCircle2 className="w-4 h-4 text-green-500" />
                            </div>
                            <p className="text-xs text-muted-foreground">Configured</p>
                        </div>

                        <div className="p-4 bg-white border border-slate-200 shadow-sm rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium">Voice Webhook</span>
                                <CheckCircle2 className="w-4 h-4 text-green-500" />
                            </div>
                            <p className="text-xs text-muted-foreground">Configured</p>
                        </div>
                    </div>
                </div>

                {/* Configuration */}
                <div className="bg-white border border-slate-200 shadow-sm rounded-2xl p-6">
                    <h3 className="font-semibold text-lg mb-4">Twilio Configuration</h3>

                    <div className="space-y-4">
                        <div>
                            <label className="text-sm font-medium mb-2 block">SMS Webhook URL</label>
                            <div className="flex gap-2">
                                <Input
                                    value={getWebhookUrl('/webhook/sms')}
                                    readOnly
                                    className="bg-white border border-slate-200 shadow-sm font-mono text-xs"
                                />
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => copyToClipboard(getWebhookUrl('/webhook/sms'))}
                                >
                                    <Copy className="w-4 h-4" />
                                </Button>
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                                Use this URL in your Twilio SMS webhook configuration
                            </p>
                        </div>

                        <div>
                            <label className="text-sm font-medium mb-2 block">Voice Webhook URL</label>
                            <div className="flex gap-2">
                                <Input
                                    value={getWebhookUrl('/webhook/voice')}
                                    readOnly
                                    className="bg-white border border-slate-200 shadow-sm font-mono text-xs"
                                />
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => copyToClipboard(getWebhookUrl('/webhook/voice'))}
                                >
                                    <Copy className="w-4 h-4" />
                                </Button>
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                                Use this URL in your Twilio voice webhook configuration
                            </p>
                        </div>

                        <div className="pt-4 border-t border-slate-200">
                            <Button className="w-full gap-2" variant="outline" asChild>
                                <a href="https://console.twilio.com" target="_blank" rel="noopener noreferrer">
                                    <ExternalLink className="w-4 h-4" />
                                    Open Twilio Console
                                </a>
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Setup Instructions */}
                <div className="lg:col-span-2 bg-white border border-slate-200 shadow-sm rounded-2xl p-6">
                    <h3 className="font-semibold text-lg mb-4">Setup Instructions</h3>

                    <div className="space-y-4">
                        <div className="flex gap-4">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold flex-shrink-0">
                                1
                            </div>
                            <div>
                                <h4 className="font-medium mb-1">Configure Ngrok (for development)</h4>
                                <p className="text-sm text-muted-foreground">
                                    Run <code className="bg-white/10 px-2 py-1 rounded">ngrok http 8000</code> to expose your local server. Copy the HTTPS URL.
                                </p>
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold flex-shrink-0">
                                2
                            </div>
                            <div>
                                <h4 className="font-medium mb-1">Update Twilio Webhook URLs</h4>
                                <p className="text-sm text-muted-foreground">
                                    Go to your Twilio phone number settings and paste the webhook URLs above (replace localhost with your ngrok URL).
                                </p>
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold flex-shrink-0">
                                3
                            </div>
                            <div>
                                <h4 className="font-medium mb-1">Test the Integration</h4>
                                <p className="text-sm text-muted-foreground">
                                    Send an SMS to your Twilio number and check the Conversations page to see the AI response.
                                </p>
                            </div>
                        </div>

                        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg mt-4">
                            <p className="text-sm text-blue-800 dark:text-blue-200">
                                <strong>💡 Tip:</strong> For production deployment, replace ngrok with your actual domain name or server IP.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
