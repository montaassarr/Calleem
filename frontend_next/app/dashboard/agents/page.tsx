"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import {
    Plus,
    Bot,
    Phone,
    Pause,
    Play,
    Edit,
    Trash2,
    TestTube,
    Activity,
    Clock
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";

interface Agent {
    id: string;
    name: string;
    description?: string;
    status: "draft" | "active" | "paused";
    avatar_url?: string;
    total_calls: number;
    total_minutes: number;
    successful_calls: number;
    created_at: string;
    last_deployed_at?: string;
    vapi_assistant_id?: string;
}

export default function AgentsPage() {
    const router = useRouter();
    const [statusFilter, setStatusFilter] = useState<string>("all");

    const { data: agents = [], isLoading } = useQuery<Agent[]>({
        queryKey: ["agents", statusFilter],
        queryFn: async () => {
            const params = statusFilter !== "all" ? `?status_filter=${statusFilter}` : "";
            const response = await api.get(`/agents${params}`);
            return response;
        },
    });

    const getStatusColor = (status: string) => {
        switch (status) {
            case "active":
                return "bg-green-500/10 text-green-500 border-green-500/20";
            case "paused":
                return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
            case "draft":
                return "bg-gray-500/10 text-gray-500 border-gray-500/20";
            default:
                return "bg-gray-500/10 text-gray-500 border-gray-500/20";
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "active":
                return <Activity className="w-3 h-3" />;
            case "paused":
                return <Pause className="w-3 h-3" />;
            default:
                return <Clock className="w-3 h-3" />;
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                        <Bot className="w-8 h-8 text-primary" />
                        Voice Agents
                    </h1>
                    <p className="text-muted-foreground">
                        Manage your AI voice agents and their configurations
                    </p>
                </div>
                <Button
                    onClick={() => router.push("/dashboard/agents/new")}
                    className="gap-2 bg-gradient-to-r from-primary to-accent"
                >
                    <Plus className="w-4 h-4" />
                    Create Agent
                </Button>
            </div>

            {/* Filters */}
            <div className="flex gap-2">
                {["all", "active", "paused", "draft"].map((status) => (
                    <Button
                        key={status}
                        variant={statusFilter === status ? "default" : "outline"}
                        size="sm"
                        onClick={() => setStatusFilter(status)}
                        className="capitalize"
                    >
                        {status}
                    </Button>
                ))}
            </div>

            {/* Agents Grid */}
            {isLoading ? (
                <div className="text-center py-12 text-muted-foreground">
                    Loading agents...
                </div>
            ) : agents.length === 0 ? (
                <div className="glass rounded-2xl p-12 text-center">
                    <div className="text-6xl mb-4">🤖</div>
                    <h3 className="text-xl font-semibold mb-2">No Agents Yet</h3>
                    <p className="text-muted-foreground mb-6">
                        Create your first voice agent to start handling calls
                    </p>
                    <Button
                        onClick={() => router.push("/dashboard/agents/new")}
                        className="gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        Create Your First Agent
                    </Button>
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {agents.map((agent) => (
                        <div
                            key={agent.id}
                            className="glass rounded-2xl p-6 space-y-4 hover:scale-[1.02] transition-transform cursor-pointer"
                            onClick={() => router.push(`/dashboard/agents/${agent.id}`)}
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-2xl">
                                        {agent.avatar_url ? (
                                            <img
                                                src={agent.avatar_url}
                                                alt={agent.name}
                                                className="w-full h-full rounded-xl object-cover"
                                            />
                                        ) : (
                                            "🤖"
                                        )}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold">{agent.name}</h3>
                                        {agent.description && (
                                            <p className="text-xs text-muted-foreground line-clamp-1">
                                                {agent.description}
                                            </p>
                                        )}
                                    </div>
                                </div>
                                <Badge
                                    className={`gap-1 ${getStatusColor(agent.status)}`}
                                    variant="outline"
                                >
                                    {getStatusIcon(agent.status)}
                                    {agent.status}
                                </Badge>
                            </div>

                            {/* Stats */}
                            <div className="grid grid-cols-3 gap-2 text-center">
                                <div className="glass-strong rounded-lg p-2">
                                    <div className="text-lg font-bold">{agent.total_calls}</div>
                                    <div className="text-xs text-muted-foreground">Calls</div>
                                </div>
                                <div className="glass-strong rounded-lg p-2">
                                    <div className="text-lg font-bold">
                                        {Math.round(agent.total_minutes)}m
                                    </div>
                                    <div className="text-xs text-muted-foreground">Minutes</div>
                                </div>
                                <div className="glass-strong rounded-lg p-2">
                                    <div className="text-lg font-bold">
                                        {agent.total_calls > 0
                                            ? Math.round(
                                                (agent.successful_calls / agent.total_calls) * 100
                                            )
                                            : 0}
                                        %
                                    </div>
                                    <div className="text-xs text-muted-foreground">Success</div>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2 pt-2 border-t border-border/50">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="flex-1 gap-2"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        router.push(`/dashboard/agents/${agent.id}/test`);
                                    }}
                                >
                                    <TestTube className="w-4 h-4" />
                                    Test
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="flex-1 gap-2"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        router.push(`/dashboard/agents/${agent.id}`);
                                    }}
                                >
                                    <Edit className="w-4 h-4" />
                                    Edit
                                </Button>
                            </div>

                            {/* Deployed Status */}
                            {agent.vapi_assistant_id && (
                                <div className="text-xs text-muted-foreground flex items-center gap-1">
                                    <Phone className="w-3 h-3" />
                                    Deployed to VAPI
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
