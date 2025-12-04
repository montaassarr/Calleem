"use client";

import React, { useEffect, useState } from 'react';
import { adminApi } from '@/lib/api/admin';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Calendar, MessageSquare, Building2, DollarSign, Activity, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';

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

export default function AdminDashboard() {
    const [stats, setStats] = useState<GlobalAnalytics | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await adminApi.getGlobalAnalytics();
                setStats(data);
            } catch (error: any) {
                console.error("Failed to fetch analytics:", error);
                toast.error("Failed to fetch analytics");
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    const statCards = [
        {
            title: "Active Tenants",
            value: stats?.tenants?.active || 0,
            icon: Building2,
            description: `out of ${stats?.tenants?.total || 0} total`,
            color: "text-blue-600"
        },
        {
            title: "Total Users",
            value: stats?.users || 0,
            icon: Users,
            description: "across all tenants",
            color: "text-purple-600"
        },
        {
            title: "Total Appointments",
            value: stats?.appointments || 0,
            icon: Calendar,
            description: "scheduled appointments",
            color: "text-green-600"
        },
        {
            title: "AI Conversations",
            value: stats?.conversations || 0,
            icon: MessageSquare,
            description: "total conversations",
            color: "text-cyan-600"
        }
    ];

    if (loading) {
        return (
            <div className="p-8 flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                        SaaS Admin Dashboard
                    </h1>
                    <p className="text-muted-foreground mt-2">
                        Manage tenants, users, and system configuration
                    </p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-full text-sm font-medium">
                    <CheckCircle2 className="w-4 h-4" />
                    All Systems Operational
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {statCards.map((stat, i) => (
                    <Card key={i} className="hover:shadow-lg transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">
                                {stat.title}
                            </CardTitle>
                            <stat.icon className={`h-5 w-5 ${stat.color}`} />
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold">{stat.value.toLocaleString()}</div>
                            <p className="text-xs text-muted-foreground mt-1">
                                {stat.description}
                            </p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Quick Actions */}
            <Card>
                <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <a
                            href="/admin/tenants"
                            className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-accent transition-colors cursor-pointer"
                        >
                            <Building2 className="w-8 h-8 text-blue-600" />
                            <span className="text-sm font-medium">Manage Tenants</span>
                        </a>
                        <a
                            href="/admin/users"
                            className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-accent transition-colors cursor-pointer"
                        >
                            <Users className="w-8 h-8 text-purple-600" />
                            <span className="text-sm font-medium">Manage Users</span>
                        </a>
                        <a
                            href="/admin/appointments"
                            className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-accent transition-colors cursor-pointer"
                        >
                            <Calendar className="w-8 h-8 text-green-600" />
                            <span className="text-sm font-medium">View Appointments</span>
                        </a>
                        <a
                            href="/admin/conversations"
                            className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-accent transition-colors cursor-pointer"
                        >
                            <MessageSquare className="w-8 h-8 text-cyan-600" />
                            <span className="text-sm font-medium">View Conversations</span>
                        </a>
                    </div>
                </CardContent>
            </Card>

            {/* System Info */}
            <Card>
                <CardHeader>
                    <CardTitle>System Information</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Last Updated</p>
                            <p className="font-semibold">
                                {stats?.timestamp ? new Date(stats.timestamp).toLocaleString() : 'N/A'}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Environment</p>
                            <p className="font-semibold">Development</p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground mb-1">Access Level</p>
                            <p className="font-semibold text-blue-600">Public (Demo Mode)</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
