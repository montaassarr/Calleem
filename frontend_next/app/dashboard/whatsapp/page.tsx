"use client";

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
        toast.success("Copied!", { description: "Webhook URL copied to clipboard" });
    };

    const getWebhookUrl = (endpoint: string) => {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL ||
            (typeof window !== 'undefined' && window.location.hostname === 'localhost'
                ? 'http://localhost:8000'
                : '');
        if (baseUrl && baseUrl.includes('your-railway-url')) {
            console.error('❌ NEXT_PUBLIC_API_URL contains placeholder value!');
        }
        return baseUrl ? `${baseUrl}/api/v1${endpoint}` : `/api/v1${endpoint}`;
    };

    return (
        <div>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">WhatsApp & SMS Integration</h1>
                <p className="text-[14px] text-gray-500 font-medium">Configure your Twilio webhooks and test messaging.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Status Card */}
                <div className="bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#187848] to-[#0a4c2f] flex items-center justify-center">
                            <Smartphone className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h3 className="font-bold text-gray-900">Webhook Status</h3>
                            <p className="text-sm text-gray-500">Real-time connection status</p>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <div className="flex items-center justify-between p-3.5 bg-gray-50 rounded-xl">
                            <span className="font-medium text-gray-700">Overall Status</span>
                            {isLoading ? (
                                <span className="text-sm text-gray-400">Checking...</span>
                            ) : webhookStatus?.status === 'active' ? (
                                <div className="flex items-center gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                                    <span className="text-green-700 font-bold text-sm">Active</span>
                                </div>
                            ) : (
                                <div className="flex items-center gap-2">
                                    <XCircle className="w-4 h-4 text-red-500" />
                                    <span className="text-red-700 font-bold text-sm">Inactive</span>
                                </div>
                            )}
                        </div>
                        {["SMS Webhook", "Voice Webhook"].map((name) => (
                            <div key={name} className="flex items-center justify-between p-3.5 bg-gray-50 rounded-xl">
                                <span className="text-sm font-medium text-gray-700">{name}</span>
                                <div className="flex items-center gap-1">
                                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                                    <span className="text-xs text-gray-500">Configured</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Configuration */}
                <div className="bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                    <h3 className="font-bold text-gray-900 mb-4">Twilio Configuration</h3>
                    <div className="space-y-4">
                        {[
                            { label: "SMS Webhook URL", endpoint: "/webhook/sms" },
                            { label: "Voice Webhook URL", endpoint: "/webhook/voice" },
                        ].map((webhook) => (
                            <div key={webhook.endpoint}>
                                <label className="text-sm font-semibold text-gray-700 mb-2 block">{webhook.label}</label>
                                <div className="flex gap-2">
                                    <input
                                        value={getWebhookUrl(webhook.endpoint)}
                                        readOnly
                                        className="flex-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-mono text-gray-700 focus:outline-none"
                                    />
                                    <button
                                        onClick={() => copyToClipboard(getWebhookUrl(webhook.endpoint))}
                                        className="px-3 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
                                    >
                                        <Copy className="w-4 h-4" />
                                    </button>
                                </div>
                                <p className="text-xs text-gray-400 mt-1">Use this URL in your Twilio {webhook.label.split(' ')[0].toLowerCase()} webhook configuration</p>
                            </div>
                        ))}

                        <div className="pt-4 border-t border-gray-100">
                            <a
                                href="https://console.twilio.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="w-full px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center justify-center gap-2"
                            >
                                <ExternalLink className="w-4 h-4" />
                                Open Twilio Console
                            </a>
                        </div>
                    </div>
                </div>

                {/* Setup Instructions */}
                <div className="lg:col-span-2 bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                    <h3 className="font-bold text-gray-900 mb-6">Setup Instructions</h3>
                    <div className="space-y-5">
                        {[
                            { step: 1, title: "Configure Ngrok (for development)", desc: <>Run <code className="bg-gray-100 px-2 py-1 rounded-lg text-xs font-mono">ngrok http 8000</code> to expose your local server. Copy the HTTPS URL.</> },
                            { step: 2, title: "Update Twilio Webhook URLs", desc: "Go to your Twilio phone number settings and paste the webhook URLs above (replace localhost with your ngrok URL)." },
                            { step: 3, title: "Test the Integration", desc: "Send an SMS to your Twilio number and check the Conversations page to see the AI response." },
                        ].map((item) => (
                            <div key={item.step} className="flex gap-4">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#187848] to-[#0a4c2f] flex items-center justify-center text-white font-bold text-sm shrink-0">
                                    {item.step}
                                </div>
                                <div>
                                    <h4 className="font-bold text-gray-900 mb-1">{item.title}</h4>
                                    <p className="text-sm text-gray-500">{item.desc}</p>
                                </div>
                            </div>
                        ))}

                        <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl mt-4">
                            <p className="text-sm text-blue-700">
                                <strong>💡 Tip:</strong> For production deployment, replace ngrok with your actual domain name or server IP.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
