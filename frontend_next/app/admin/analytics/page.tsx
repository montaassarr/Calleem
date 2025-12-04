"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import type { LucideIcon } from "lucide-react";
import {
    Building2,
    Users,
    Calendar,
    MessageSquare,
    RefreshCw,
    Loader2,
    AlertCircle,
    CheckCircle2
} from "lucide-react";

import { adminApi } from "@/lib/api/admin";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface GlobalAnalytics {
    tenants: {
        total: number;
        active: number;
    };
    users: number;
    appointments: number;
    conversations: number;
    timestamp?: string;
}

interface MetricCardConfig {
    key: string;
    title: string;
    value: number;
    description: string;
    icon: LucideIcon;
    accent: string;
}

export default function AdminAnalyticsPage() {
    const [analytics, setAnalytics] = useState<GlobalAnalytics | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchAnalytics = useCallback(async (options: { background?: boolean } = {}) => {
        const { background = false } = options;
        if (background) {
            setRefreshing(true);
        } else {
            setLoading(true);
        }

        try {
            const data = await adminApi.getGlobalAnalytics();
            setAnalytics(data);
            setError(null);
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to fetch analytics";
            setError(message);
        } finally {
            if (background) {
                setRefreshing(false);
            } else {
                setLoading(false);
            }
        }
    }, []);

    useEffect(() => {
        fetchAnalytics();
    }, [fetchAnalytics]);

    const metrics: MetricCardConfig[] = useMemo(() => ([
        {
            key: "active-tenants",
            title: "Active Tenants",
            value: analytics?.tenants?.active ?? 0,
            description: `out of ${analytics?.tenants?.total ?? 0} total tenants`,
            icon: Building2,
            accent: "text-blue-600"
        },
        {
            key: "total-users",
            title: "Total Users",
            value: analytics?.users ?? 0,
            description: "across all tenants",
            icon: Users,
            accent: "text-purple-600"
        },
        {
            key: "appointments",
            title: "Appointments",
            value: analytics?.appointments ?? 0,
            description: "scheduled across the platform",
            icon: Calendar,
            accent: "text-green-600"
        },
        {
            key: "conversations",
            title: "AI Conversations",
            value: analytics?.conversations ?? 0,
            description: "handled by the assistant",
            icon: MessageSquare,
            accent: "text-cyan-600"
        }
    ]), [analytics]);

    const lastUpdated = useMemo(() => {
        if (!analytics?.timestamp) {
            return null;
        }
        try {
            return new Date(analytics.timestamp).toLocaleString();
        } catch (err) {
            console.warn("Failed to format analytics timestamp", err);
            return analytics.timestamp;
        }
    }, [analytics]);

    const renderStatusBadge = () => {
        if (error && !analytics) {
            return (
                <Badge variant="destructive" className="flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    Fetch Failed
                </Badge>
            );
        }

        if (analytics) {
            return (
                <Badge variant="outline" className="flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-green-600" />
                    Operational
                </Badge>
            );
        }

        return null;
    };

    if (loading && !analytics) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <div className="flex flex-col items-center gap-3 text-center">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-sm text-muted-foreground">Loading analytics…</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8 p-6">
            <header className="flex flex-wrap items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-semibold tracking-tight">Analytics Overview</h1>
                    <p className="text-sm text-muted-foreground">
                        Monitor tenant activity, usage, and AI engagement across the platform.
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    {renderStatusBadge()}
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => fetchAnalytics({ background: true })}
                        disabled={refreshing}
                        className="inline-flex items-center gap-2"
                    >
                        <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
                        Refresh
                    </Button>
                </div>
            </header>

            {error && (
                <Card className="border-destructive/40 bg-destructive/5">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-destructive">
                            <div className="flex items-center gap-2">
                                <AlertCircle className="h-4 w-4" />
                                Unable to refresh analytics
                            </div>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-destructive">{error}</p>
                    </CardContent>
                </Card>
            )}

            <section>
                <h2 className="mb-4 text-xl font-semibold">Key Metrics</h2>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    {metrics.map((metric) => (
                        <Card key={metric.key} className="hover:shadow-lg transition-shadow">
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground">
                                    {metric.title}
                                </CardTitle>
                                <metric.icon className={`h-5 w-5 ${metric.accent}`} />
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-semibold">
                                    {metric.value.toLocaleString()}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">{metric.description}</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </section>

            <section>
                <Card>
                    <CardHeader>
                        <CardTitle>Snapshot</CardTitle>
                    </CardHeader>
                    <CardContent className="grid gap-6 md:grid-cols-2">
                        <div className="space-y-2">
                            <p className="text-sm font-medium text-muted-foreground">Active Tenants</p>
                            <p className="text-lg font-semibold">
                                {(analytics?.tenants?.active ?? 0).toLocaleString()} / {(analytics?.tenants?.total ?? 0).toLocaleString()}
                            </p>
                            <p className="text-xs text-muted-foreground">
                                Number of businesses currently onboarded and actively using the platform.
                            </p>
                        </div>
                        <div className="space-y-2">
                            <p className="text-sm font-medium text-muted-foreground">Engagement</p>
                            <p className="text-lg font-semibold">
                                {(analytics?.conversations ?? 0).toLocaleString()} conversations powered by AI.
                            </p>
                            <p className="text-xs text-muted-foreground">
                                Conversations across all tenants in the current reporting period.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </section>

            {lastUpdated && (
                <p className="text-xs text-muted-foreground">
                    Last updated {lastUpdated}. Data refreshes automatically on demand.
                </p>
            )}
        </div>
    );
}
