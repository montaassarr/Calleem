"use client";

import { useState } from "react";
import { crewApi, CrewJobStatus } from "@/lib/api/crew";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Sparkles, BarChart3, CheckCircle2, XCircle } from "lucide-react";
import { useQuery, useMutation } from "@tanstack/react-query";

export default function CrewAdminPage() {
    const [activeJobId, setActiveJobId] = useState<string | null>(null);

    // Poll for job status if we have an active job
    const { data: jobStatus } = useQuery({
        queryKey: ['crewJob', activeJobId],
        queryFn: () => crewApi.getJobStatus(activeJobId!),
        enabled: !!activeJobId,
        refetchInterval: (query) => (query.state.data?.status === 'completed' || query.state.data?.status === 'failed' ? false : 2000),
    });

    const cleanDataMutation = useMutation({
        mutationFn: crewApi.triggerDataCleaning,
        onSuccess: (data) => setActiveJobId(data.job_id),
    });

    const analyticsMutation = useMutation({
        mutationFn: crewApi.triggerAnalytics,
        onSuccess: (data) => setActiveJobId(data.job_id),
    });

    return (
        <div className="space-y-8 p-8">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-white">AI Crews</h2>
                    <p className="text-slate-400">Manage and trigger your autonomous AI agents.</p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Data Cleaning Crew Card */}
                <Card className="bg-slate-950/50 border-white/10 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-white">
                            <Sparkles className="h-5 w-5 text-cyan-400" />
                            Data Cleaning Crew
                        </CardTitle>
                        <CardDescription className="text-slate-400">
                            Agents: Data Quality Specialist
                            <br />
                            Task: Scan for duplicates, inconsistencies, and clean database records.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button
                            onClick={() => cleanDataMutation.mutate()}
                            disabled={cleanDataMutation.isPending || (jobStatus?.status === 'running')}
                            className="bg-cyan-600 hover:bg-cyan-500 text-white w-full"
                        >
                            {cleanDataMutation.isPending ? (
                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Starting...</>
                            ) : (
                                "Start Cleaning Job"
                            )}
                        </Button>
                    </CardContent>
                </Card>

                {/* Analytics Crew Card */}
                <Card className="bg-slate-950/50 border-white/10 backdrop-blur-xl">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-white">
                            <BarChart3 className="h-5 w-5 text-purple-400" />
                            Analytics Crew
                        </CardTitle>
                        <CardDescription className="text-slate-400">
                            Agents: Business Analyst
                            <br />
                            Task: Analyze appointment trends and generate strategic insights.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button
                            onClick={() => analyticsMutation.mutate()}
                            disabled={analyticsMutation.isPending || (jobStatus?.status === 'running')}
                            className="bg-purple-600 hover:bg-purple-500 text-white w-full"
                        >
                            {analyticsMutation.isPending ? (
                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Starting...</>
                            ) : (
                                "Generate Insights"
                            )}
                        </Button>
                    </CardContent>
                </Card>
            </div>

            {/* Active Job Status */}
            {activeJobId && jobStatus && (
                <Card className="bg-slate-900/80 border-white/10 mt-8 animate-in fade-in slide-in-from-bottom-4">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            Job Status: {jobStatus.type === 'cleaning' ? 'Data Cleaning' : 'Analytics'}
                            {jobStatus.status === 'running' && <Loader2 className="h-4 w-4 animate-spin text-cyan-400" />}
                            {jobStatus.status === 'completed' && <CheckCircle2 className="h-4 w-4 text-green-400" />}
                            {jobStatus.status === 'failed' && <XCircle className="h-4 w-4 text-red-400" />}
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="bg-black/50 p-4 rounded-lg font-mono text-sm text-slate-300 whitespace-pre-wrap max-h-96 overflow-y-auto">
                            {jobStatus.result || jobStatus.error || "Processing..."}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
