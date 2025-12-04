"use client";

import { useState, useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Phone, AlertCircle, CheckCircle2, Info, Settings, Loader2, PhoneOff, Mic } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import dynamic from 'next/dynamic';

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { voiceApi, businessConfigApi } from "@/lib/api-endpoints";

// Dynamically import LiveKit components to avoid SSR issues
const VoiceApp = dynamic(
  () => import('@/components/voice-agent/voice-app').then((mod) => mod.VoiceApp),
  { ssr: false, loading: () => <div className="flex items-center justify-center p-8"><Loader2 className="w-6 h-6 animate-spin" /></div> }
);

export default function VoiceTestPage() {
    const [testStatus, setTestStatus] = useState<"idle" | "testing" | "success" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState("");
    const [liveKitToken, setLiveKitToken] = useState<string>("");
    const [roomUrl, setRoomUrl] = useState<string>("");
    const [isInCall, setIsInCall] = useState(false);
    const queryClient = useQueryClient();

    // Get business config to check if voice is enabled
    const { data: businessConfig, isLoading: isConfigLoading } = useQuery({
        queryKey: ["business-config"],
        queryFn: () => businessConfigApi.getConfig(),
    });

    const voiceFeatureEnabled = businessConfig?.features_enabled?.voice_agent ?? false;
    const currentFeatures = useMemo(() => businessConfig?.features_enabled ?? {}, [businessConfig]);

    // Fetch voice agent status
    const { data: voiceStatus, isLoading, refetch: refetchStatus } = useQuery({
        queryKey: ["voice-agent", "status"],
        queryFn: () => voiceApi.testAgent(),
        enabled: voiceFeatureEnabled,
        retry: 1,
    });

    const enableVoiceAgent = useMutation({
        mutationFn: async () => voiceApi.enableVoiceAgent(true),
        onSuccess: () => {
            toast.success("Voice agent enabled. You're ready to test!");
            queryClient.invalidateQueries({ queryKey: ["business-config"] });
            queryClient.invalidateQueries({ queryKey: ["voice-agent", "status"] });
        },
        onError: (error: any) => {
            const detail = error?.response?.data?.detail ?? "Please try again in a moment.";
            toast.error("Unable to enable the voice agent", { description: detail });
        },
    });

    const handleTest = async () => {
        setTestStatus("testing");
        setErrorMessage("");

        try {
            // Call the WebRTC test endpoint to get token
            const response = await fetch("/api/v1/voice-agent/webrtc/test", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                },
                body: JSON.stringify({}),
            });

            if (!response.ok) {
                throw new Error("Failed to create test session");
            }

            const data = await response.json();
            setLiveKitToken(data.token);
            setRoomUrl(data.url);
            setIsInCall(true);
            setTestStatus("success");
            toast.success("Connected to LiveKit!");
        } catch (error: any) {
            setTestStatus("error");
            setErrorMessage(error?.message || "Test failed");
            toast.error("Failed to start call");
        }
    };

    const handleEndCall = () => {
        setIsInCall(false);
        setLiveKitToken("");
        setRoomUrl("");
        setTestStatus("idle");
    };

    return (
        <div className="p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-bold mb-2">Voice Agent Test</h1>
                <p className="text-muted-foreground">
                    Test your voice agent configuration and verify connectivity
                </p>
            </div>

            {!voiceFeatureEnabled && (
                <Alert className="mb-6" variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Activate your AI agent</AlertTitle>
                    <AlertDescription>
                        Turn on the voice agent to unlock web calls, phone routing, and transcripts. We’ll take care of the
                        backend wiring automatically.
                    </AlertDescription>
                    <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                        <Button
                            type="button"
                            className="w-full sm:w-auto"
                            disabled={enableVoiceAgent.isPending || isConfigLoading}
                            onClick={() => enableVoiceAgent.mutate()}
                        >
                            {enableVoiceAgent.isPending ? (
                                <span className="inline-flex items-center gap-2">
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                    Enabling...
                                </span>
                            ) : (
                                "Enable Voice Agent"
                            )}
                        </Button>
                        <Button
                            type="button"
                            variant="outline"
                            className="w-full sm:w-auto"
                            asChild
                        >
                            <Link href="/dashboard/voice-agent/control-center">Review setup steps</Link>
                        </Button>
                    </div>
                </Alert>
            )}

            {voiceFeatureEnabled && (
                <Alert className="mb-6">
                    <Info className="h-4 w-4" />
                    <AlertTitle>Live Testing Mode</AlertTitle>
                    <AlertDescription>
                        Test your voice agent with real-time interaction. The agent has demo functions 
                        you can try: weather lookup, discount calculator, reminder setting, and business 
                        status checking. Try asking: "What's the weather in London?" or "Calculate 25% off $80"
                    </AlertDescription>
                </Alert>
            )}

            {/* LiveKit Voice Room */}
            {isInCall && liveKitToken && roomUrl ? (
                <div className="mb-6 h-[600px] rounded-lg border overflow-hidden">
                    <VoiceApp
                        token={liveKitToken}
                        serverUrl={roomUrl}
                        onDisconnect={handleEndCall}
                        agentName="callflow-multi-tenant"
                    />
                </div>
            ) : null}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Mic className="w-5 h-5" />
                            Voice Agent Status
                        </CardTitle>
                        <CardDescription>
                            Current configuration and connectivity status
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm">Feature Status</span>
                            {voiceFeatureEnabled ? (
                                <Badge variant="default" className="gap-1">
                                    <CheckCircle2 className="w-3 h-3" />
                                    Enabled
                                </Badge>
                            ) : (
                                <Badge variant="secondary">Disabled</Badge>
                            )}
                        </div>

                        {voiceFeatureEnabled && voiceStatus && (
                            <>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm">Agent Status</span>
                                    <Badge variant={voiceStatus.configured ? "default" : "secondary"}>
                                        {voiceStatus.configured ? "Configured" : "Not Configured"}
                                    </Badge>
                                </div>

                                <div className="flex items-center justify-between">
                                    <span className="text-sm">Agent Name</span>
                                    <span className="text-sm font-mono">
                                        {voiceStatus.agent_name || "Not configured"}
                                    </span>
                                </div>

                                <div className="flex items-center justify-between">
                                    <span className="text-sm">Voice Agent</span>
                                    <span className="text-sm font-mono">
                                        {voiceStatus.voice_agent_enabled ? "Enabled" : "Disabled"}
                                    </span>
                                </div>

                                {voiceStatus.phone_number && (
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm">Phone Number</span>
                                        <span className="text-xs font-mono text-muted-foreground">
                                            {voiceStatus.phone_number}
                                        </span>
                                    </div>
                                )}
                            </>
                        )}

                        {voiceFeatureEnabled && (
                            <Button
                                onClick={handleTest}
                                disabled={testStatus === "testing" || isLoading}
                                className="w-full"
                            >
                                {testStatus === "testing" || isLoading ? "Testing..." : "Run Test"}
                            </Button>
                        )}

                        {testStatus === "success" && (
                            <Alert>
                                <CheckCircle2 className="h-4 w-4" />
                                <AlertTitle>Test Successful</AlertTitle>
                                <AlertDescription>
                                    Voice agent configuration is valid and connected
                                </AlertDescription>
                            </Alert>
                        )}

                        {testStatus === "error" && (
                            <Alert variant="destructive">
                                <AlertCircle className="h-4 w-4" />
                                <AlertTitle>Test Failed</AlertTitle>
                                <AlertDescription>{errorMessage}</AlertDescription>
                            </Alert>
                        )}

                        <div className="pt-4 border-t">
                            <Link href="/dashboard/voice-agent/control-center">
                                <Button variant="outline" className="w-full" size="sm">
                                    <Settings className="w-4 h-4 mr-2" />
                                    Open Control Center
                                </Button>
                            </Link>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Phone className="w-5 h-5" />
                            How It Works
                        </CardTitle>
                        <CardDescription>
                            Voice agent call flow
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-3">
                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    1
                                </div>
                                <div>
                                    <p className="text-sm font-medium">Customer calls your number</p>
                                    <p className="text-xs text-muted-foreground">Via phone or web interface</p>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    2
                                </div>
                                <div>
                                    <p className="text-sm font-medium">Vapi connects to Groq AI</p>
                                    <p className="text-xs text-muted-foreground">Using your configured model</p>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    3
                                </div>
                                <div>
                                    <p className="text-sm font-medium">AI processes conversation</p>
                                    <p className="text-xs text-muted-foreground">Natural language understanding</p>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    4
                                </div>
                                <div>
                                    <p className="text-sm font-medium">Executes actions via tools</p>
                                    <p className="text-xs text-muted-foreground">Check availability, book appointments</p>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    5
                                </div>
                                <div>
                                    <p className="text-sm font-medium">Saves to database</p>
                                    <p className="text-xs text-muted-foreground">Conversations and bookings stored</p>
                                </div>
                            </div>
                        </div>

                        <div className="pt-4 border-t">
                            <p className="text-xs text-muted-foreground">
                                💡 Configure your voice agent in the{" "}
                                <Link href="/dashboard/settings/ai" className="underline">
                                    AI Settings
                                </Link>
                                {" "}page to customize behavior
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
