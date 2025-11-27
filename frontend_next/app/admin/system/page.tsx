"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Server, Globe, Database, Activity, RefreshCw, Terminal, AlertTriangle } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export default function SystemHealthPage() {
    const { toast } = useToast();
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleAction = (action: string) => {
        setIsRefreshing(true);
        setTimeout(() => {
            setIsRefreshing(false);
            toast({
                title: "Action Triggered",
                description: `${action} has been initiated successfully.`,
            });
        }, 1500);
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">System Health</h1>
                    <p className="text-muted-foreground">Monitor infrastructure and perform DevOps tasks.</p>
                </div>
                <Button onClick={() => handleAction("System Refresh")}>
                    <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                    Refresh Status
                </Button>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
                {/* Infrastructure Status */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Server className="h-5 w-5" /> Infrastructure
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Backend Container</span>
                            <Badge className="bg-green-500">Running</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Frontend Container</span>
                            <Badge className="bg-green-500">Running</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Redis Cache</span>
                            <Badge className="bg-green-500">Running</Badge>
                        </div>
                        <div className="mt-4 pt-4 border-t">
                            <div className="text-xs text-muted-foreground mb-1">CPU Usage</div>
                            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                <div className="h-full bg-blue-500 w-[25%]" />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Database Status */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Database className="h-5 w-5" /> Database
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm">MongoDB Primary</span>
                            <Badge className="bg-green-500">Healthy</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Connections</span>
                            <span className="font-mono text-sm">42</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Storage Used</span>
                            <span className="font-mono text-sm">1.2 GB</span>
                        </div>
                        <Button variant="outline" size="sm" className="w-full mt-2" onClick={() => handleAction("DB Cleanup")}>
                            Run Cleanup Tool
                        </Button>
                    </CardContent>
                </Card>

                {/* API & Webhooks */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Globe className="h-5 w-5" /> API Gateways
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm">VAPI Webhook</span>
                            <Badge className="bg-green-500">Active</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">WhatsApp Webhook</span>
                            <Badge className="bg-yellow-500">Degraded</Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Error Rate (1h)</span>
                            <span className="text-red-500 font-bold">0.05%</span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* DevOps Tools */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Terminal className="h-5 w-5" /> DevOps Tools
                    </CardTitle>
                    <CardDescription>Administrative actions for system maintenance.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <Button variant="secondary" onClick={() => handleAction("Cache Flush")}>
                            Flush Redis Cache
                        </Button>
                        <Button variant="secondary" onClick={() => handleAction("Restart Agents")}>
                            Restart AI Agents
                        </Button>
                        <Button variant="secondary" onClick={() => handleAction("Log Rotate")}>
                            Rotate Logs
                        </Button>
                        <Button variant="destructive" onClick={() => handleAction("Emergency Stop")}>
                            <AlertTriangle className="mr-2 h-4 w-4" /> Emergency Stop
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
