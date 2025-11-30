"use client";

import { useState } from "react";
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, Rocket } from "lucide-react";
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
import { toast } from "sonner";
import api from "@/lib/api";

interface AgentFormData {
    name: string;
    description: string;
    system_prompt: string;
    voice_settings: {
        provider: string;
        voice_id: string;
        stability: number;
        similarity_boost: number;
    };
    llm_model: string;
    llm_temperature: number;
    webhook_urls: {
        get_slots: string;
        book: string;
        update: string;
        cancel: string;
    };
}

export default function NewAgentPage() {
    const router = useRouter();
    const queryClient = useQueryClient();

    const [formData, setFormData] = useState<AgentFormData>({
        name: "",
        description: "",
        system_prompt: `You are a friendly and professional AI receptionist. Your role is to:
- Greet callers warmly
- Help them check available appointment slots
- Book appointments with their preferred time
- Reschedule or cancel existing appointments
- Answer questions about services

Always be polite, clear, and efficient. Confirm all details before booking.`,
        voice_settings: {
            provider: "elevenlabs",
            voice_id: "21m00Tcm4TlvDq8ikWAM", // Rachel voice
            stability: 0.5,
            similarity_boost: 0.75,
        },
        llm_model: "gpt-4",
        llm_temperature: 0.7,
        webhook_urls: {
            get_slots: "http://localhost:5678/webhook/getslots",
            book: "http://localhost:5678/webhook/bookslots",
            update: "http://localhost:5678/webhook/updateslots",
            cancel: "http://localhost:5678/webhook/cancelslots",
        },
    });

    // Get current user's tenant_id
    const { data: user } = useQuery({
        queryKey: ["current-user"],
        queryFn: async () => {
            // Assuming you have a /me endpoint or get it from localStorage
            const userStr = localStorage.getItem("user");
            return userStr ? JSON.parse(userStr) : null;
        },
    });

    const createMutation = useMutation({
        mutationFn: async (data: any) => {
            return await api.post("/agents", data);
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["agents"] });
            toast.success("Agent created successfully!");
            router.push(`/dashboard/agents/${data.id}`);
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || "Failed to create agent");
        },
    });

    const deployMutation = useMutation({
        mutationFn: async (agentId: string) => {
            return await api.post(`/agents/${agentId}/deploy`);
        },
        onSuccess: () => {
            toast.success("Agent deployed to VAPI!");
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || "Failed to deploy agent");
        },
    });

    const handleSave = async (deploy: boolean = false) => {
        if (!formData.name) {
            toast.error("Please enter an agent name");
            return;
        }

        if (!user?.tenant_id) {
            toast.error("User tenant not found");
            return;
        }

        const payload = {
            ...formData,
            tenant_id: user.tenant_id,
            status: deploy ? "active" : "draft",
        };

        const agent = await createMutation.mutateAsync(payload);

        if (deploy && agent?.id) {
            await deployMutation.mutateAsync(agent.id);
        }
    };

    return (
        <div className="p-6 max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => router.back()}
                >
                    <ArrowLeft className="w-5 h-5" />
                </Button>
                <div>
                    <h1 className="text-3xl font-bold">Create Voice Agent</h1>
                    <p className="text-muted-foreground">
                        Configure your AI receptionist
                    </p>
                </div>
            </div>

            {/* Form */}
            <div className="space-y-6">
                {/* Basic Info */}
                <div className="glass rounded-2xl p-6 space-y-4">
                    <h2 className="text-xl font-semibold">Basic Information</h2>

                    <div className="space-y-2">
                        <Label htmlFor="name">Agent Name *</Label>
                        <Input
                            id="name"
                            placeholder="e.g., Sarah - Hair Salon Receptionist"
                            value={formData.name}
                            onChange={(e) =>
                                setFormData({ ...formData, name: e.target.value })
                            }
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Input
                            id="description"
                            placeholder="Brief description of this agent"
                            value={formData.description}
                            onChange={(e) =>
                                setFormData({ ...formData, description: e.target.value })
                            }
                        />
                    </div>
                </div>

                {/* System Prompt */}
                <div className="glass rounded-2xl p-6 space-y-4">
                    <h2 className="text-xl font-semibold">System Prompt</h2>
                    <div className="space-y-2">
                        <Label htmlFor="prompt">Instructions for the AI</Label>
                        <Textarea
                            id="prompt"
                            rows={8}
                            value={formData.system_prompt}
                            onChange={(e) =>
                                setFormData({ ...formData, system_prompt: e.target.value })
                            }
                            className="font-mono text-sm"
                        />
                    </div>
                </div>

                {/* Voice Settings */}
                <div className="glass rounded-2xl p-6 space-y-4">
                    <h2 className="text-xl font-semibold">Voice Settings</h2>

                    <div className="grid md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="voice_provider">Voice Provider</Label>
                            <Select
                                value={formData.voice_settings.provider}
                                onValueChange={(value) =>
                                    setFormData({
                                        ...formData,
                                        voice_settings: {
                                            ...formData.voice_settings,
                                            provider: value,
                                        },
                                    })
                                }
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="elevenlabs">ElevenLabs</SelectItem>
                                    <SelectItem value="openai">OpenAI TTS</SelectItem>
                                    <SelectItem value="deepgram">Deepgram</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="voice_id">Voice ID</Label>
                            <Input
                                id="voice_id"
                                placeholder="21m00Tcm4TlvDq8ikWAM"
                                value={formData.voice_settings.voice_id}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        voice_settings: {
                                            ...formData.voice_settings,
                                            voice_id: e.target.value,
                                        },
                                    })
                                }
                            />
                        </div>
                    </div>
                </div>

                {/* LLM Settings */}
                <div className="glass rounded-2xl p-6 space-y-4">
                    <h2 className="text-xl font-semibold">LLM Settings</h2>

                    <div className="grid md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="llm_model">Model</Label>
                            <Select
                                value={formData.llm_model}
                                onValueChange={(value) =>
                                    setFormData({ ...formData, llm_model: value })
                                }
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="gpt-4">GPT-4</SelectItem>
                                    <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                                    <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="temperature">Temperature: {formData.llm_temperature}</Label>
                            <input
                                type="range"
                                id="temperature"
                                min="0"
                                max="2"
                                step="0.1"
                                value={formData.llm_temperature}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        llm_temperature: parseFloat(e.target.value),
                                    })
                                }
                                className="w-full"
                            />
                        </div>
                    </div>
                </div>

                {/* Webhook URLs */}
                <div className="glass rounded-2xl p-6 space-y-4">
                    <h2 className="text-xl font-semibold">Webhook Configuration</h2>
                    <p className="text-sm text-muted-foreground">
                        These URLs connect to your N8N workflows
                    </p>

                    <div className="grid md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label>Get Slots</Label>
                            <Input
                                value={formData.webhook_urls.get_slots}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        webhook_urls: {
                                            ...formData.webhook_urls,
                                            get_slots: e.target.value,
                                        },
                                    })
                                }
                                className="font-mono text-xs"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label>Book Appointment</Label>
                            <Input
                                value={formData.webhook_urls.book}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        webhook_urls: {
                                            ...formData.webhook_urls,
                                            book: e.target.value,
                                        },
                                    })
                                }
                                className="font-mono text-xs"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label>Update Appointment</Label>
                            <Input
                                value={formData.webhook_urls.update}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        webhook_urls: {
                                            ...formData.webhook_urls,
                                            update: e.target.value,
                                        },
                                    })
                                }
                                className="font-mono text-xs"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label>Cancel Appointment</Label>
                            <Input
                                value={formData.webhook_urls.cancel}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        webhook_urls: {
                                            ...formData.webhook_urls,
                                            cancel: e.target.value,
                                        },
                                    })
                                }
                                className="font-mono text-xs"
                            />
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-4">
                    <Button
                        variant="outline"
                        onClick={() => handleSave(false)}
                        disabled={createMutation.isPending}
                        className="gap-2"
                    >
                        <Save className="w-4 h-4" />
                        Save as Draft
                    </Button>
                    <Button
                        onClick={() => handleSave(true)}
                        disabled={createMutation.isPending || deployMutation.isPending}
                        className="gap-2 flex-1"
                    >
                        <Rocket className="w-4 h-4" />
                        {createMutation.isPending || deployMutation.isPending
                            ? "Deploying..."
                            : "Deploy to VAPI"}
                    </Button>
                </div>
            </div>
        </div>
    );
}
