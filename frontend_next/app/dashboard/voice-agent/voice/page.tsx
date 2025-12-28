"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Loader2, Volume2, Play, Save, Check } from "lucide-react";
import { assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

interface Voice {
    id: string;
    name: string;
    gender: string;
    accent: string;
}

interface VoiceProvider {
    id: string;
    name: string;
    description: string;
    voices: Voice[];
}

export default function VoiceConfigPage() {
    const { toast } = useToast();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [providers, setProviders] = useState<VoiceProvider[]>([]);
    const [currentVoice, setCurrentVoice] = useState<any>(null);

    // Form state
    const [selectedProvider, setSelectedProvider] = useState("11labs");
    const [selectedVoice, setSelectedVoice] = useState("");
    const [voiceSpeed, setVoiceSpeed] = useState([1.0]);
    const [previewText, setPreviewText] = useState("Hello! Thank you for calling. How can I help you today?");

    const loadData = useCallback(async () => {
        try {
            setLoading(true);
            const [providersData, voiceData] = await Promise.all([
                assistantApi.getVoiceProviders(),
                assistantApi.getVoice()
            ]);

            setProviders(providersData.providers || []);
            setCurrentVoice(voiceData.voice || {});

            if (voiceData.voice) {
                setSelectedProvider(voiceData.voice.provider || "11labs");
                setSelectedVoice(voiceData.voice.voiceId || "");
                setVoiceSpeed([voiceData.voice.speed || 1.0]);
            }
        } catch (error) {
            console.error("Failed to load voice config:", error);
            toast({
                title: "Error",
                description: "Failed to load voice configuration",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    }, [toast]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handleSave = async () => {
        try {
            setSaving(true);
            await assistantApi.updateVoice({
                provider: selectedProvider,
                voice_id: selectedVoice,
                speed: voiceSpeed[0]
            });

            toast({
                title: "Saved",
                description: "Voice configuration updated successfully"
            });
        } catch (error) {
            console.error("Failed to save:", error);
            toast({
                title: "Error",
                description: "Failed to save voice configuration",
                variant: "destructive"
            });
        } finally {
            setSaving(false);
        }
    };

    const currentProviderVoices = providers.find(p => p.id === selectedProvider)?.voices || [];

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Voice Configuration</h1>
                    <p className="text-muted-foreground mt-1">
                        Configure how your AI assistant sounds
                    </p>
                </div>
                <div className="flex gap-3">
                    <Button variant="outline" asChild>
                        <Link href="/dashboard/voice-agent/control-center">Back to Control Center</Link>
                    </Button>
                    <Button onClick={handleSave} disabled={saving}>
                        {saving ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                            <Save className="w-4 h-4 mr-2" />
                        )}
                        Save Changes
                    </Button>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
                {/* Voice Provider Selection */}
                <Card className="bg-white border-slate-200 shadow-sm">
                    <CardHeader>
                        <CardTitle>Voice Provider</CardTitle>
                        <CardDescription>Choose your text-to-speech provider</CardDescription>
                    </CardHeader>
                    <CardContent className="bg-white border-slate-200 shadow-sm space-y-4">
                        <div className="grid grid-cols-1 gap-3">
                            {providers.map((provider) => (
                                <div
                                    key={provider.id}
                                    onClick={() => {
                                        setSelectedProvider(provider.id);
                                        setSelectedVoice("");
                                    }}
                                    className={`p-4 border rounded-lg cursor-pointer transition-all ${selectedProvider === provider.id
                                        ? "border-primary bg-primary/5 ring-2 ring-primary"
                                        : "hover:border-primary/50"
                                        }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h3 className="font-semibold">{provider.name}</h3>
                                            <p className="text-sm text-muted-foreground">{provider.description}</p>
                                        </div>
                                        {selectedProvider === provider.id && (
                                            <Check className="h-5 w-5 text-primary" />
                                        )}
                                    </div>
                                    <div className="mt-2">
                                        <Badge variant="secondary">{provider.voices.length} voices</Badge>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Voice Selection */}
                <Card className="bg-white border-slate-200 shadow-sm">
                    <CardHeader>
                        <CardTitle>Select Voice</CardTitle>
                        <CardDescription>Choose a voice for your assistant</CardDescription>
                    </CardHeader>
                    <CardContent className="bg-white border-slate-200 shadow-sm space-y-4">
                        <div className="grid grid-cols-2 gap-3 max-h-80 overflow-y-auto">
                            {currentProviderVoices.map((voice) => (
                                <div
                                    key={voice.id}
                                    onClick={() => setSelectedVoice(voice.id)}
                                    className={`p-3 border rounded-lg cursor-pointer transition-all ${selectedVoice === voice.id
                                        ? "border-primary bg-primary/5 ring-2 ring-primary"
                                        : "hover:border-primary/50"
                                        }`}
                                >
                                    <div className="flex items-center gap-2">
                                        <Volume2 className="h-4 w-4 text-muted-foreground" />
                                        <span className="font-medium">{voice.name}</span>
                                    </div>
                                    <div className="flex gap-1 mt-1">
                                        <Badge variant="outline" className="text-xs">{voice.gender}</Badge>
                                        <Badge variant="outline" className="text-xs">{voice.accent}</Badge>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {selectedVoice && (
                            <div className="pt-4 border-t">
                                <p className="text-sm text-muted-foreground mb-2">
                                    Selected: <span className="font-medium text-foreground">
                                        {currentProviderVoices.find(v => v.id === selectedVoice)?.name}
                                    </span>
                                </p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Voice Settings */}
                <Card className="bg-white border-slate-200 shadow-sm lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Voice Settings</CardTitle>
                        <CardDescription>Fine-tune voice parameters</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid gap-6 md:grid-cols-2">
                            <div className="space-y-4">
                                <Label>Speaking Speed</Label>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm w-12">Slow</span>
                                    <Slider
                                        value={voiceSpeed}
                                        onValueChange={setVoiceSpeed}
                                        min={0.5}
                                        max={2.0}
                                        step={0.1}
                                        className="flex-1"
                                    />
                                    <span className="text-sm w-12">Fast</span>
                                </div>
                                <p className="text-sm text-muted-foreground">
                                    Current: {voiceSpeed[0].toFixed(1)}x
                                </p>
                            </div>

                            <div className="space-y-4">
                                <Label>Voice Preview</Label>
                                <textarea
                                    value={previewText}
                                    onChange={(e) => setPreviewText(e.target.value)}
                                    className="w-full p-3 border rounded-lg resize-none h-20"
                                    placeholder="Enter text to preview..."
                                />
                                <Button variant="outline" className="w-full">
                                    <Play className="w-4 h-4 mr-2" />
                                    Preview Voice (Coming Soon)
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
