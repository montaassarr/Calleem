"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Phone, Clock, TrendingUp, DollarSign, BarChart3, MessageSquare } from "lucide-react";
import { assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

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

export default function AnalyticsPage() {
    const { toast } = useToast();
    const [loading, setLoading] = useState(true);
    const [period, setPeriod] = useState("30");
    const [analytics, setAnalytics] = useState<CallAnalytics | null>(null);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [loadingConversations, setLoadingConversations] = useState(false);

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

    useEffect(() => {
        loadAnalytics();
    }, [loadAnalytics]);

    useEffect(() => {
        loadConversations();
    }, [loadConversations]);

    const formatDuration = (seconds?: number) => {
        if (!seconds) return "0:00";
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    const formatDate = (dateStr?: string) => {
        if (!dateStr) return "—";
        return new Date(dateStr).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Analytics</h1>
                    <p className="text-muted-foreground mt-1">
                        Call metrics and conversation history
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <Select value={period} onValueChange={setPeriod}>
                        <SelectTrigger className="w-32">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="7">Last 7 days</SelectItem>
                            <SelectItem value="30">Last 30 days</SelectItem>
                            <SelectItem value="90">Last 90 days</SelectItem>
                        </SelectContent>
                    </Select>
                    <Button variant="outline" asChild>
                        <Link href="/dashboard/voice-agent/control-center">Back</Link>
                    </Button>
                </div>
            </div>

            {/* Stats Cards */}
            {loading ? (
                <div className="flex justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-4">
                    <Card className="bg-white border-slate-200 shadow-sm">
                        <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Total Calls</p>
                                    <p className="text-3xl font-bold">{analytics?.total_calls || 0}</p>
                                </div>
                                <div className="p-3 bg-blue-100 rounded-full">
                                    <Phone className="h-6 w-6 text-blue-600" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-white border-slate-200 shadow-sm">
                        <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Total Duration</p>
                                    <p className="text-3xl font-bold">
                                        {analytics?.total_duration_minutes?.toFixed(1) || 0}
                                        <span className="text-lg font-normal text-muted-foreground"> min</span>
                                    </p>
                                </div>
                                <div className="p-3 bg-green-100 rounded-full">
                                    <Clock className="h-6 w-6 text-green-600" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-white border-slate-200 shadow-sm">
                        <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Avg Duration</p>
                                    <p className="text-3xl font-bold">
                                        {analytics?.avg_duration_seconds?.toFixed(0) || 0}
                                        <span className="text-lg font-normal text-muted-foreground"> sec</span>
                                    </p>
                                </div>
                                <div className="p-3 bg-purple-100 rounded-full">
                                    <TrendingUp className="h-6 w-6 text-purple-600" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-white border-slate-200 shadow-sm">
                        <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Total Cost</p>
                                    <p className="text-3xl font-bold">
                                        ${((analytics?.total_cost_cents || 0) / 100).toFixed(2)}
                                    </p>
                                </div>
                                <div className="p-3 bg-yellow-100 rounded-full">
                                    <DollarSign className="h-6 w-6 text-yellow-600" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Calls by Status */}
            {analytics && Object.keys(analytics.calls_by_status || {}).length > 0 && (
                <Card className="bg-white border-slate-200 shadow-sm">
                    <CardHeader>
                        <CardTitle className="bg-white border-slate-200 shadow-sm flex items-center gap-2">
                            <BarChart3 className="h-5 w-5" />
                            Calls by Status
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-wrap gap-3">
                            {Object.entries(analytics.calls_by_status).map(([status, count]) => (
                                <div key={status} className="flex items-center gap-2 p-3 bg-slate-100 rounded-lg">
                                    <Badge variant={status === "ended" ? "default" : "secondary"}>
                                        {status}
                                    </Badge>
                                    <span className="font-semibold">{count}</span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Recent Conversations */}
            <Card className="bg-white border-slate-200 shadow-sm">
                <CardHeader>
                    <CardTitle className="bg-white border-slate-200 shadow-sm flex items-center gap-2">
                        <MessageSquare className="h-5 w-5" />
                        Recent Conversations
                    </CardTitle>
                    <CardDescription>
                        View call history and transcripts
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loadingConversations ? (
                        <div className="flex justify-center py-4">
                            <Loader2 className="h-6 w-6 animate-spin" />
                        </div>
                    ) : conversations.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
                            <p>No conversations yet</p>
                            <p className="text-sm">Make a test call to see call history here</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {conversations.map((conv) => (
                                <div
                                    key={conv.id}
                                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-100/50 transition-colors"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="p-2 bg-slate-100 rounded-full">
                                            <Phone className="h-4 w-4" />
                                        </div>
                                        <div>
                                            <p className="font-medium">
                                                {conv.customer_phone || "Web Call"}
                                            </p>
                                            <p className="text-sm text-muted-foreground">
                                                {formatDate(conv.created_at)}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="text-right">
                                            <p className="text-sm font-medium">
                                                {formatDuration(conv.duration)}
                                            </p>
                                            <Badge variant={conv.status === "ended" ? "default" : "secondary"}>
                                                {conv.status || "unknown"}
                                            </Badge>
                                        </div>
                                        <Button variant="ghost" size="sm" asChild>
                                            <Link href={`/dashboard/voice-agent/analytics/${conv.id}`}>
                                                View
                                            </Link>
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
