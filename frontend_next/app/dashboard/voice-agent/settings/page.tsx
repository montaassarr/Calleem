"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Save,
    ArrowLeft,
    Mic,
    MessageSquare,
    Clock,
    Phone
} from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { businessConfigApi } from "@/lib/api-endpoints";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export default function VoiceAgentSettingsPage() {
    const router = useRouter();
    const queryClient = useQueryClient();

    const [settings, setSettings] = useState({
        // Voice Settings
        voice_provider: "elevenlabs",
        elevenlabs_voice_id: "21m00Tcm4TlvDq8ikWAM", // Rachel voice

        // Call Settings
        max_call_duration: 300, // 5 minutes
        greeting_message: "Hello! I'm your AI receptionist. How can I help you today?",

        // System Prompt
        system_prompt: `You are a professional AI receptionist for a barber shop. Your role is to:
- Greet customers warmly
- Help them book appointments
- Answer questions about services and pricing
- Be friendly, professional, and efficient

Always confirm appointment details before booking.`,

        // VAPI Settings
        vapi_assistant_id: "",
        vapi_phone_number: "",
    });

    const { data: config, isLoading } = useQuery({
        queryKey: ["business-config"],
        queryFn: () => businessConfigApi.getConfig(),
    });

    useEffect(() => {
        if (config) {
            setSettings(prev => ({
                ...prev,
                system_prompt: config.system_prompt || prev.system_prompt,
                vapi_assistant_id: config.vapi_assistant_id || "",
                vapi_phone_number: config.vapi_phone_number || "",
            }));
        }
    }, [config]);

    const updateMutation = useMutation({
        mutationFn: (data: any) => businessConfigApi.updateFeatureFlags(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["business-config"] });
            toast.success("Voice agent settings saved successfully!");
        },
        onError: () => {
            toast.error("Failed to update voice agent settings");
        },
    });

    const handleSave = () => {
        updateMutation.mutate(settings);
    };

    if (isLoading) {
        return <div className="p-6 text-center text-muted-foreground">Loading...</div>;
    }

    return (
        <div className="p-6 max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => router.push('/dashboard/voice-agent')}
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold mb-2">Voice Agent Settings</h1>
                        <p className="text-muted-foreground">
                            Configure your AI voice agent's behavior and settings
                        </p>
                    </div>
                </div>
                <Button
                    className="gap-2 bg-gradient-to-r from-primary to-accent"
                    onClick={handleSave}
                    disabled={updateMutation.isPending}
                >
                    <Save className="w-4 h-4" />
                    {updateMutation.isPending ? "Saving..." : "Save Settings"}
                </Button>
            </div>

            {/* Voice Settings */}
            <div className="glass rounded-2xl p-6 space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Mic className="w-5 h-5 text-primary" />
                    Voice Settings
                </h2>

                <div className="space-y-4">
                    <div>
                        <Label htmlFor="voice_provider">Voice Provider</Label>
                        <select
                            id="voice_provider"
                            value={settings.voice_provider}
                            onChange={(e) => setSettings({ ...settings, voice_provider: e.target.value })}
                            className="w-full mt-2 glass-strong rounded-lg px-4 py-2 border border-white/10"
                        >
                            <option value="elevenlabs">ElevenLabs</option>
                            <option value="openai">OpenAI TTS</option>
                        </select>
                    </div>

                    <div>
                        <Label htmlFor="elevenlabs_voice_id">ElevenLabs Voice ID</Label>
                        <Input
                            id="elevenlabs_voice_id"
                            type="text"
                            value={settings.elevenlabs_voice_id}
                            onChange={(e) => setSettings({ ...settings, elevenlabs_voice_id: e.target.value })}
                            className="glass-strong font-mono text-sm mt-2"
                            placeholder="21m00Tcm4TlvDq8ikWAM"
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                            Get voice IDs from <a href="https://elevenlabs.io/voice-library" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">ElevenLabs Voice Library</a>
                        </p>
                    </div>
                </div>
            </div>

            {/* Call Settings */}
            <div className="glass rounded-2xl p-6 space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Phone className="w-5 h-5 text-primary" />
                    Call Settings
                </h2>

                <div className="space-y-4">
                    <div>
                        <Label htmlFor="max_call_duration">Max Call Duration (seconds)</Label>
                        <Input
                            id="max_call_duration"
                            type="number"
                            value={settings.max_call_duration}
                            onChange={(e) => setSettings({ ...settings, max_call_duration: parseInt(e.target.value) || 300 })}
                            className="glass-strong mt-2"
                            min="60"
                            max="1800"
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                            Maximum duration for a single call (60-1800 seconds)
                        </p>
                    </div>

                    <div>
                        <Label htmlFor="greeting_message">Greeting Message</Label>
                        <Input
                            id="greeting_message"
                            type="text"
                            value={settings.greeting_message}
                            onChange={(e) => setSettings({ ...settings, greeting_message: e.target.value })}
                            className="glass-strong mt-2"
                            placeholder="Hello! How can I help you today?"
                        />
                    </div>
                </div>
            </div>

            {/* System Prompt */}
            <div className="glass rounded-2xl p-6 space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-primary" />
                    AI Behavior (System Prompt)
                </h2>

                <div>
                    <Label htmlFor="system_prompt">System Prompt</Label>
                    <Textarea
                        id="system_prompt"
                        value={settings.system_prompt}
                        onChange={(e) => setSettings({ ...settings, system_prompt: e.target.value })}
                        className="glass-strong mt-2 min-h-[200px] font-mono text-sm"
                        placeholder="Define how your AI agent should behave..."
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                        This prompt defines your AI agent's personality, knowledge, and behavior
                    </p>
                </div>
            </div>

            {/* VAPI Integration */}
            <div className="glass rounded-2xl p-6 space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Clock className="w-5 h-5 text-primary" />
                    VAPI Integration
                </h2>

                <div className="space-y-4">
                    <div>
                        <Label htmlFor="vapi_assistant_id">VAPI Assistant ID</Label>
                        <Input
                            id="vapi_assistant_id"
                            type="text"
                            value={settings.vapi_assistant_id}
                            onChange={(e) => setSettings({ ...settings, vapi_assistant_id: e.target.value })}
                            className="glass-strong font-mono text-sm mt-2"
                            placeholder="assistant_..."
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                            Your VAPI assistant ID (optional - will auto-create if empty)
                        </p>
                    </div>

                    <div>
                        <Label htmlFor="vapi_phone_number">VAPI Phone Number</Label>
                        <Input
                            id="vapi_phone_number"
                            type="text"
                            value={settings.vapi_phone_number}
                            onChange={(e) => setSettings({ ...settings, vapi_phone_number: e.target.value })}
                            className="glass-strong font-mono text-sm mt-2"
                            placeholder="+1234567890"
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                            Phone number assigned by VAPI for incoming calls
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
