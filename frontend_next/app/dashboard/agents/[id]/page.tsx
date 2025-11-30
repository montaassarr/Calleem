"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter, useParams } from "next/navigation";
import {
    ArrowLeft,
    Save,
    Rocket,
    Pause,
    Play,
    Trash2,
    Phone,
    Activity,
    Clock,
    CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import api from "@/lib/api";
import Vapi from "@vapi-ai/web";

interface Agent {
    id: string;
    name: string;
    description?: string;
    system_prompt: string;
    voice_settings: {
        provider: string;
        voice_id: string;
        stability?: number;
        similarity_boost?: number;
    };
    llm_model: string;
    llm_temperature: number;
    webhook_urls: {
        get_slots: string;
        book: string;
        update: string;
        cancel: string;
    };
    status: "draft" | "active" | "paused";
    vapi_assistant_id?: string;
    total_calls: number;
    total_minutes: number;
    successful_calls: number;
    created_at: string;
    last_deployed_at?: string;
}

export default function AgentDetailPage() {
    const router = useRouter();
    const params = useParams();
    const agentId = params.id as string;
    const queryClient = useQueryClient();
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState<Partial<Agent> | null>(null);
    const [callState, setCallState] = useState<"idle" | "connecting" | "live">("idle");
    const [vapiClient, setVapiClient] = useState<Vapi | null>(null);

    const { data: agent, isLoading } = useQuery<Agent>({
        queryKey: ["agent", agentId],
        queryFn: async () => {
            const response = await api.get(`/agents/${agentId}`);
            return response;
        },
    });

    const updateMutation = useMutation({
        mutationFn: async (data: Partial<Agent>) => {
            return await api.put(`/agents/${agentId}`, data);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["agent", agentId] });
            queryClient.invalidateQueries({ queryKey: ["agents"] });
            toast.success("Agent updated successfully!");
            setIsEditing(false);
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || "Failed to update agent");
        },
    });

    const deployMutation = useMutation({
        mutationFn: async () => {
            return await api.post(`/agents/${agentId}/deploy`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["agent", agentId] });
            toast.success("Agent deployed to VAPI!");
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || "Failed to deploy agent");
        },
    });

    const pauseMutation = useMutation({
        mutationFn: async () => {
            return await api.post(`/agents/${agentId}/pause`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["agent", agentId] });
            toast.success("Agent paused");
        },
    });

    const activateMutation = useMutation({
        mutationFn: async () => {
            return await api.post(`/agents/${agentId}/activate`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["agent", agentId] });
            toast.success("Agent activated");
        },
    });

    const deleteMutation = useMutation({
        mutationFn: async () => {
            return await api.delete(`/agents/${agentId}`);
        },
        onSuccess: () => {
            toast.success("Agent deleted");
            router.push("/dashboard/agents");
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || "Failed to delete agent");
        },
    });

    const handleSave = () => {
        if (formData) {
            updateMutation.mutate(formData);
        }
    };

    const handleTestCall = () => {
        if (!agent?.vapi_assistant_id) {
            toast.error("Please deploy the agent first");
            return;
        }

        const publicKey = process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY;
        if (!publicKey) {
            toast.error("VAPI public key not configured");
            return;
        }

        const client = new Vapi(publicKey);
        setVapiClient(client);

        client.on("call-start", () => {
            setCallState("live");
            toast.success("Call started!");
        });

        client.on("call-end", () => {
            setCallState("idle");
            toast.info("Call ended");
        });

        client.on("error", (error) => {
            setCallState("idle");
            toast.error("Call error: " + error.message);
        });

        setCallState("connecting");
        client.start(agent.vapi_assistant_id);
    };

    const handleEndCall = () => {
        if (vapiClient) {
            vapiClient.stop();
            setCallState("idle");
        }
    };

    if (isLoading) {
        return (
            <div className="p-6 max-w-4xl mx-auto">
                <div className="text-center py-12">Loading agent...</div>
            </div>
        );
    }

    if (!agent) {
        return (
            <div className="p-6 max-w-4xl mx-auto">
                <div className="text-center py-12">Agent not found</div>
            </div>
        );
    }

    const currentData = isEditing && formData ? formData : agent;

    return (
        <div className="p-6 max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="w-5 h-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold">{agent.name}</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <Badge
                                variant="outline"
                                className={
                                    agent.status === "active"
                                        ? "bg-green-500/10 text-green-500"
                                        : agent.status === "paused"
                                            ? "bg-yellow-500/10 text-yellow-500"
                                            : "bg-gray-500/10 text-gray-500"
                                }
                            >
                                {agent.status}
                            </Badge>
                            {agent.vapi_assistant_id && (
                                <Badge variant="outline" className="gap-1">
                                    <CheckCircle2 className="w-3 h-3" />
                                    Deployed
                                </Badge>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex gap-2">
                    {agent.status === "active" ? (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => pauseMutation.mutate()}
                            disabled={pauseMutation.isPending}
                        >
                            <Pause className="w-4 h-4 mr-2" />
                            Pause
                        </Button>
                    ) : (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => activateMutation.mutate()}
                            disabled={activateMutation.isPending}
                        >
                            <Play className="w-4 h-4 mr-2" />
                            Activate
                        </Button>
                    )}
                    <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => {
                            if (confirm("Are you sure you want to delete this agent?")) {
                                deleteMutation.mutate();
                            }
                        }}
                        disabled={deleteMutation.isPending}
                    >
                        <Trash2 className="w-4 h-4" />
                    </Button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold">{agent.total_calls}</div>
                    <div className="text-sm text-muted-foreground">Total Calls</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold">{Math.round(agent.total_minutes)}m</div>
                    <div className="text-sm text-muted-foreground">Minutes</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <div className="text-2xl font-bold">
                        {agent.total_calls > 0
                            ? Math.round((agent.successful_calls / agent.total_calls) * 100)
                            : 0}
                        %
                    </div>
                    <div className="text-sm text-muted-foreground">Success Rate</div>
                </div>
                <div className="glass rounded-xl p-4">
                    <Button
                        className="w-full gap-2"
                        onClick={callState === "idle" ? handleTestCall : handleEndCall}
                        variant={callState === "live" ? "destructive" : "default"}
                    >
                        <Phone className="w-4 h-4" />
                        {callState === "idle"
                            ? "Test Call"
                            : callState === "connecting"
                                ? "Connecting..."
                                : "End Call"}
                    </Button>
                </div>
            </div>

            {/* Configuration */}
            <div className="space-y-6">
                {isEditing ? (
                    <>
                        {/* Edit Mode */}
                        <div className="glass rounded-2xl p-6 space-y-4">
                            <h2 className="text-xl font-semibold">Basic Information</h2>
                            <div className="space-y-2">
                                <Label>Agent Name</Label>
                                <Input
                                    value={currentData.name || ""}
                                    onChange={(e) =>
                                        setFormData({ ...formData, name: e.target.value })
                                    }
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Description</Label>
                                <Input
                                    value={currentData.description || ""}
                                    onChange={(e) =>
                                        setFormData({ ...formData, description: e.target.value })
                                    }
                                />
                            </div>
                        </div>

                        <div className="glass rounded-2xl p-6 space-y-4">
                            <h2 className="text-xl font-semibold">System Prompt</h2>
                            <Textarea
                                rows={8}
                                value={currentData.system_prompt || ""}
                                onChange={(e) =>
                                    setFormData({ ...formData, system_prompt: e.target.value })
                                }
                                className="font-mono text-sm"
                            />
                        </div>

                        <div className="flex gap-4">
                            <Button variant="outline" onClick={() => setIsEditing(false)}>
                                Cancel
                            </Button>
                            <Button
                                onClick={handleSave}
                                disabled={updateMutation.isPending}
                                className="gap-2"
                            >
                                <Save className="w-4 h-4" />
                                Save Changes
                            </Button>
                            <Button
                                onClick={() => deployMutation.mutate()}
                                disabled={deployMutation.isPending}
                                className="gap-2"
                            >
                                <Rocket className="w-4 h-4" />
                                Deploy to VAPI
                            </Button>
                        </div>
                    </>
                ) : (
                    <>
                        {/* View Mode */}
                        <div className="glass rounded-2xl p-6 space-y-4">
                            <div className="flex items-center justify-between">
                                <h2 className="text-xl font-semibold">Configuration</h2>
                                <Button variant="outline" size="sm" onClick={() => {
                                    setFormData(agent);
                                    setIsEditing(true);
                                }}>
                                    Edit
                                </Button>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <Label className="text-muted-foreground">System Prompt</Label>
                                    <p className="mt-1 whitespace-pre-wrap">{agent.system_prompt}</p>
                                </div>

                                <div className="grid md:grid-cols-2 gap-4">
                                    <div>
                                        <Label className="text-muted-foreground">Voice Provider</Label>
                                        <p className="mt-1 capitalize">{agent.voice_settings.provider}</p>
                                    </div>
                                    <div>
                                        <Label className="text-muted-foreground">Voice ID</Label>
                                        <p className="mt-1 font-mono text-sm">{agent.voice_settings.voice_id}</p>
                                    </div>
                                    <div>
                                        <Label className="text-muted-foreground">LLM Model</Label>
                                        <p className="mt-1">{agent.llm_model}</p>
                                    </div>
                                    <div>
                                        <Label className="text-muted-foreground">Temperature</Label>
                                        <p className="mt-1">{agent.llm_temperature}</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="glass rounded-2xl p-6 space-y-4">
                            <h2 className="text-xl font-semibold">Webhook URLs</h2>
                            <div className="grid gap-2 text-sm">
                                <div>
                                    <Label className="text-muted-foreground">Get Slots</Label>
                                    <p className="font-mono text-xs">{agent.webhook_urls.get_slots}</p>
                                </div>
                                <div>
                                    <Label className="text-muted-foreground">Book</Label>
                                    <p className="font-mono text-xs">{agent.webhook_urls.book}</p>
                                </div>
                                <div>
                                    <Label className="text-muted-foreground">Update</Label>
                                    <p className="font-mono text-xs">{agent.webhook_urls.update}</p>
                                </div>
                                <div>
                                    <Label className="text-muted-foreground">Cancel</Label>
                                    <p className="font-mono text-xs">{agent.webhook_urls.cancel}</p>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
