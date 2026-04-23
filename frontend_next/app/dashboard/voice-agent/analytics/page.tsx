"use client";

import { useState, useEffect, useCallback } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Phone, Clock, TrendingUp, DollarSign, BarChart3, MessageSquare, ArrowUpRight } from "lucide-react";
import { assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";
import { WebCallsModal } from "@/components/dashboard/WebCallsModal";

interface CallAnalytics {
    total_calls: number;
    total_duration_minutes: number;
    avg_duration_seconds: number;
    total_cost_cents: number;
    calls_by_status: Record<string, number>;
    calls_by_day: Array<{ date: string; count: number; duration: number }>;
}

interface Conversation {
    id: string;
    vapi_call_id?: string;
    customer_phone?: string;
    status?: string;
    duration?: number;
    summary?: string;
    created_at?: string;
}

interface WebCall {
    id: string;
    phoneNumber: string;
    duration?: number;
    createdAt?: string;
    endedAt?: string;
    transcript?: string;
    status?: string;
    cost?: number;
}

export default function AnalyticsPage() {
    const { toast } = useToast();
    const [loading, setLoading] = useState(true);
    const [period, setPeriod] = useState("30");
    const [analytics, setAnalytics] = useState<CallAnalytics | null>(null);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [loadingConversations, setLoadingConversations] = useState(false);
    const [showWebCallsModal, setShowWebCallsModal] = useState(false);
    const [webCalls, setWebCalls] = useState<WebCall[]>([]);
    const [loadingWebCalls, setLoadingWebCalls] = useState(false);

    const loadAnalytics = useCallback(async () => {
        try {
            setLoading(true);
            const data = await assistantApi.getCallAnalytics(parseInt(period));
            setAnalytics(data);
        } catch (error) {
            console.error("Failed to load analytics:", error);
        } finally {
            setLoading(false);
        }
    }, [period]);

    const loadConversations = useCallback(async () => {
        try {
            setLoadingConversations(true);
            const data = await assistantApi.getConversations(10);
            setConversations(data.conversations || []);
        } catch (error) {
            console.error("Failed to load conversations:", error);
        } finally {
            setLoadingConversations(false);
        }
    }, []);

    const loadWebCalls = useCallback(async () => {
        try {
            setLoadingWebCalls(true);
            const data = await assistantApi.getConversations(100, 0);
            const formattedCalls: WebCall[] = (data.conversations || []).map((conv: any) => ({
                id: conv.id || conv.vapi_call_id,
                phoneNumber: conv.customer_phone || conv.phone_number || "Web Call",
                duration: conv.duration,
                createdAt: conv.created_at || conv.datetime,
                endedAt: conv.ended_at,
                transcript: conv.transcript || conv.summary,
                status: conv.status || "unknown",
                cost: conv.cost,
            }));
            setWebCalls(formattedCalls);
        } catch (error) {
            console.error("Failed to load web calls:", error);
            toast({ title: "Error", description: "Failed to load web calls", variant: "destructive" });
        } finally {
            setLoadingWebCalls(false);
        }
    }, [toast]);

    useEffect(() => { loadAnalytics(); }, [loadAnalytics]);
    useEffect(() => { loadConversations(); }, [loadConversations]);

    const handleOpenWebCalls = () => {
        setShowWebCallsModal(true);
        loadWebCalls();
    };

    const formatDuration = (seconds?: number) => {
        if (!seconds) return "0:00";
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    const formatDate = (dateStr?: string) => {
        if (!dateStr) return "—";
        return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    };

    const getStatusStyle = (status?: string) => {
        switch (status) {
            case "ended": return "bg-green-100 text-green-700";
            case "in-progress": return "bg-amber-100 text-amber-700";
            default: return "bg-gray-100 text-gray-600";
        }
    };

    const statCards = [
        { label: "Total Calls", value: analytics?.total_calls || 0, icon: Phone, color: "from-blue-500 to-blue-600" },
        { label: "Total Duration", value: `${analytics?.total_duration_minutes?.toFixed(1) || 0} min`, icon: Clock, color: "from-[#187848] to-[#0a4c2f]" },
        { label: "Avg Duration", value: `${analytics?.avg_duration_seconds?.toFixed(0) || 0} sec`, icon: TrendingUp, color: "from-purple-500 to-purple-600" },
        { label: "Total Cost", value: `$${((analytics?.total_cost_cents || 0) / 100).toFixed(2)}`, icon: DollarSign, color: "from-amber-500 to-amber-600" },
    ];

    return (
        <div>
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Analytics</h1>
                    <p className="text-[14px] text-gray-500 font-medium">Call metrics and conversation history.</p>
                </div>
                <div className="flex items-center gap-2">
                    <Select value={period} onValueChange={setPeriod}>
                        <SelectTrigger className="w-32 rounded-xl border-gray-200">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="7">Last 7 days</SelectItem>
                            <SelectItem value="30">Last 30 days</SelectItem>
                            <SelectItem value="90">Last 90 days</SelectItem>
                        </SelectContent>
                    </Select>
                    <Link href="/dashboard/voice-agent/control-center" className="px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm">
                        Back
                    </Link>
                </div>
            </div>

            {/* Stats Cards */}
            {loading ? (
                <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-[#0a4c2f]" /></div>
            ) : (
                <div className="grid gap-4 grid-cols-2 xl:grid-cols-4 mb-8">
                    {statCards.map((card, i) => (
                        <div key={i} className="bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-5">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500 font-medium">{card.label}</p>
                                    <p className="text-[28px] font-bold text-gray-900 mt-1">{card.value}</p>
                                </div>
                                <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color} text-white`}>
                                    <card.icon className="h-5 w-5" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Calls by Status */}
            {analytics && Object.keys(analytics.calls_by_status || {}).length > 0 && (
                <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6 mb-8">
                    <h3 className="font-bold text-lg text-gray-900 mb-4 flex items-center gap-2"><BarChart3 className="h-5 w-5" />Calls by Status</h3>
                    <div className="flex flex-wrap gap-3">
                        {Object.entries(analytics.calls_by_status).map(([status, count]) => (
                            <div key={status} className="flex items-center gap-2 p-3 bg-gray-50 rounded-xl">
                                <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${getStatusStyle(status)}`}>{status}</span>
                                <span className="font-bold text-gray-900">{count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Recent Conversations */}
            <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6 mb-8">
                <h3 className="font-bold text-lg text-gray-900 mb-1 flex items-center gap-2"><MessageSquare className="h-5 w-5" />Recent Conversations</h3>
                <p className="text-sm text-gray-500 mb-6">View call history and transcripts</p>

                {loadingConversations ? (
                    <div className="flex justify-center py-4"><Loader2 className="h-6 w-6 animate-spin text-[#0a4c2f]" /></div>
                ) : conversations.length === 0 ? (
                    <div className="text-center py-8">
                        <MessageSquare className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                        <p className="font-medium text-gray-900">No conversations yet</p>
                        <p className="text-sm text-gray-500">Make a test call to see call history here</p>
                    </div>
                ) : (
                    <div className="flex flex-col gap-3">
                        {conversations.map((conv) => (
                            <div key={conv.id} className="flex items-center justify-between p-4 rounded-xl hover:bg-gray-50 transition-colors border border-gray-100">
                                <div className="flex items-center gap-3 min-w-0">
                                    <div className="w-10 h-10 rounded-full bg-[#f3f5f4] flex items-center justify-center shrink-0">
                                        <Phone className="h-4 w-4 text-gray-500" />
                                    </div>
                                    <div className="min-w-0">
                                        <p className="font-bold text-gray-900 text-sm">{conv.customer_phone || "Web Call"}</p>
                                        <p className="text-xs text-gray-500">{formatDate(conv.created_at)}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-sm font-medium text-gray-700">{formatDuration(conv.duration)}</span>
                                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${getStatusStyle(conv.status)}`}>{conv.status || "unknown"}</span>
                                    <Link href={`/dashboard/voice-agent/analytics/${conv.id}`} className="text-sm text-[#0a4c2f] hover:underline font-medium">View</Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* View All Web Calls */}
            <div className="flex justify-center py-4">
                <button onClick={handleOpenWebCalls} className="px-6 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-[20px] font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] flex items-center gap-2 relative overflow-hidden">
                    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                    <Phone className="h-4 w-4 relative z-10" />
                    <span className="relative z-10">View All Web Calls</span>
                </button>
            </div>

            <WebCallsModal isOpen={showWebCallsModal} onClose={() => setShowWebCallsModal(false)} calls={webCalls} isLoading={loadingWebCalls} />
        </div>
    );
}
