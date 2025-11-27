"use client";

import React, { useEffect, useState } from 'react';
import { adminApi, CrewJob } from '@/lib/api/admin';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { Loader2, Play, RefreshCw, FileText, BarChart, Users, DollarSign, ShieldCheck } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { DataTable } from '@/components/admin/DataTable';

export default function AiMonitorPage() {
    const [jobs, setJobs] = useState<CrewJob[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [selectedJob, setSelectedJob] = useState<CrewJob | null>(null);
    const [isResultOpen, setIsResultOpen] = useState(false);
    const [triggering, setTriggering] = useState<string | null>(null);

    const { toast } = useToast();

    const fetchJobs = async () => {
        try {
            setLoading(true);
            const data = await adminApi.getJobs(20); // Get last 20 jobs
            setJobs(data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch AI jobs",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchJobs();
        // Poll every 10 seconds
        const interval = setInterval(fetchJobs, 10000);
        return () => clearInterval(interval);
    }, []);

    const handleTrigger = async (type: string, apiCall: () => Promise<any>) => {
        try {
            setTriggering(type);
            await apiCall();
            toast({
                title: "Success",
                description: `${type} job started successfully`
            });
            fetchJobs();
        } catch (error) {
            toast({
                title: "Error",
                description: `Failed to start ${type} job`,
                variant: "destructive"
            });
        } finally {
            setTriggering(null);
        }
    };

    const handleViewResult = (job: CrewJob) => {
        setSelectedJob(job);
        setIsResultOpen(true);
    };

    const getStatusBadge = (status: string) => {
        const styles: Record<string, string> = {
            completed: "bg-green-100 text-green-800",
            running: "bg-blue-100 text-blue-800 animate-pulse",
            pending: "bg-yellow-100 text-yellow-800",
            failed: "bg-red-100 text-red-800"
        };
        return (
            <Badge className={styles[status] || "bg-gray-100 text-gray-800"}>
                {status.toUpperCase()}
            </Badge>
        );
    };

    const columns = [
        {
            key: 'type',
            label: 'Job Type',
            render: (type: string) => (
                <span className="font-medium capitalize">{type.replace(/_/g, ' ')}</span>
            )
        },
        {
            key: 'status',
            label: 'Status',
            render: (status: string) => getStatusBadge(status)
        },
        {
            key: 'created_at',
            label: 'Started At',
            render: (date: string) => new Date(date).toLocaleString()
        },
        {
            key: 'actions',
            label: 'Result',
            render: (_, job: CrewJob) => (
                job.status === 'completed' ? (
                    <Button variant="ghost" size="sm" onClick={() => handleViewResult(job)}>
                        <FileText className="h-4 w-4 mr-2" /> View Report
                    </Button>
                ) : (
                    <span className="text-muted-foreground text-sm">-</span>
                )
            )
        }
    ];

    return (
        <div className="p-6 space-y-6">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">AI Operations Center</h1>
                <p className="text-muted-foreground">
                    Monitor and trigger autonomous AI agents for your business.
                </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Customer Insights</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-xs text-muted-foreground mb-4">
                            Segments customers and analyzes behavior patterns.
                        </div>
                        <Button
                            className="w-full"
                            onClick={() => handleTrigger('Insights', adminApi.triggerInsights)}
                            disabled={!!triggering}
                        >
                            {triggering === 'Insights' ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                            Run Analysis
                        </Button>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Revenue Optimization</CardTitle>
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-xs text-muted-foreground mb-4">
                            Identifies upsell opportunities and pricing strategies.
                        </div>
                        <Button
                            className="w-full"
                            onClick={() => handleTrigger('Revenue', adminApi.triggerRevenue)}
                            disabled={!!triggering}
                        >
                            {triggering === 'Revenue' ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                            Optimize Revenue
                        </Button>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Data Cleaning</CardTitle>
                        <RefreshCw className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-xs text-muted-foreground mb-4">
                            Standardizes and deduplicates client records.
                        </div>
                        <Button
                            className="w-full"
                            onClick={() => handleTrigger('Cleaning', adminApi.triggerDataCleaning)}
                            disabled={!!triggering}
                        >
                            {triggering === 'Cleaning' ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                            Clean Data
                        </Button>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Analytics Report</CardTitle>
                        <BarChart className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-xs text-muted-foreground mb-4">
                            Generates comprehensive business performance reports.
                        </div>
                        <Button
                            className="w-full"
                            onClick={() => handleTrigger('Analytics', adminApi.triggerAnalytics)}
                            disabled={!!triggering}
                        >
                            {triggering === 'Analytics' ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                            Generate Report
                        </Button>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Recent Job History</CardTitle>
                    <CardDescription>
                        View the status and results of recent AI agent operations.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <DataTable
                        title=""
                        columns={columns}
                        data={jobs}
                        total={jobs.length}
                        page={page}
                        pageSize={20}
                        onPageChange={setPage}
                        isLoading={loading}
                        hideSearch
                        hidePagination={jobs.length < 20}
                    />
                </CardContent>
            </Card>

            <Dialog open={isResultOpen} onOpenChange={setIsResultOpen}>
                <DialogContent className="max-w-3xl max-h-[80vh]">
                    <DialogHeader>
                        <DialogTitle>Job Result: {selectedJob?.type.replace(/_/g, ' ')}</DialogTitle>
                        <DialogDescription>
                            Completed on {selectedJob?.completed_at && new Date(selectedJob.completed_at).toLocaleString()}
                        </DialogDescription>
                    </DialogHeader>
                    <ScrollArea className="h-[60vh] w-full rounded-md border p-4 bg-muted/50">
                        <pre className="text-sm whitespace-pre-wrap font-mono">
                            {selectedJob?.result || "No result data available."}
                        </pre>
                    </ScrollArea>
                </DialogContent>
            </Dialog>
        </div>
    );
}
