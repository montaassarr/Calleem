"use client";

import React, { useEffect, useState } from 'react';
import { adminApi } from '@/lib/api/admin';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Calendar, MessageSquare, Building2, DollarSign, Activity, Server, Globe, Database, Zap } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export default function AdminDashboard() {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await adminApi.getGlobalAnalytics();
                setStats(data);
            } catch (error) {
                toast({
                    title: "Error",
                    description: "Failed to fetch analytics",
                    variant: "destructive"
                });
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    const statCards = [
        {
            title: "Total Revenue (MRR)",
            value: "$12,450",
            icon: DollarSign,
            description: "+15% from last month",
            color: "text-green-600"
        },
        {
            title: "Active Tenants",
            value: stats?.tenants?.active || 0,
            icon: Building2,
            description: `out of ${stats?.tenants?.total || 0} total accounts`,
            color: "text-blue-600"
        },
        {
            title: "AI Conversations",
            value: stats?.conversations || 0,
            icon: MessageSquare,
            description: "handled today across all agents",
            color: "text-purple-600"
        },
        {
            title: "System Health",
            value: "99.9%",
            icon: Activity,
            description: "All systems operational",
            color: "text-green-500"
        }
    ];

    if (loading) {
        return <div className="p-8 text-center">Loading dashboard...</div>;
    }

    return (
        <div className="p-6 space-y-8">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold">SaaS Control Center</h1>
                <div className="flex gap-2">
                    <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        Operational
                    </div>
                </div>
            </div>

            {/* Top Stats Row */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {statCards.map((stat, i) => (
                    <Card key={i}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                {stat.title}
                            </CardTitle>
                            <stat.icon className={`h-4 w-4 ${stat.color}`} />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stat.value}</div>
                            <p className="text-xs text-muted-foreground">
                                {stat.description}
                            </p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                {/* Main Chart Area (Placeholder) */}
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>Revenue Overview</CardTitle>
                    </CardHeader>
                    <CardContent className="pl-2">
                        <div className="h-[200px] flex items-center justify-center text-muted-foreground bg-slate-50 rounded-md border border-dashed">
                            Revenue Chart Placeholder
                        </div>
                    </CardContent>
                </Card>

                {/* System Status */}
                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>System Status</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Server className="w-4 h-4 text-slate-500" />
                                    <span className="text-sm font-medium">Backend API</span>
                                </div>
                                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Online</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Globe className="w-4 h-4 text-slate-500" />
                                    <span className="text-sm font-medium">Frontend App</span>
                                </div>
                                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Online</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Database className="w-4 h-4 text-slate-500" />
                                    <span className="text-sm font-medium">MongoDB Cluster</span>
                                </div>
                                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Healthy</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Zap className="w-4 h-4 text-slate-500" />
                                    <span className="text-sm font-medium">AI Inference (Groq)</span>
                                </div>
                                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Operational</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Recent Activity / Logs */}
            <Card>
                <CardHeader>
                    <CardTitle>Recent System Activity</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {[1, 2, 3].map((_, i) => (
                            <div key={i} className="flex items-center justify-between border-b pb-2 last:border-0">
                                <div className="flex items-center gap-3">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full" />
                                    <div>
                                        <p className="text-sm font-medium">New tenant registration</p>
                                        <p className="text-xs text-muted-foreground">Barber Shop #{100 + i} joined the platform</p>
                                    </div>
                                </div>
                                <span className="text-xs text-muted-foreground">{i * 15} mins ago</span>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
