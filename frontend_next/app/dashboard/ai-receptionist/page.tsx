"use client";

import { useState } from "react";
import { Bot, Loader2, Play, Settings } from "lucide-react";
import dynamic from 'next/dynamic';
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

// Dynamically import LiveKit components
const VoiceApp = dynamic(
  () => import('@/components/voice-agent/voice-app').then((mod) => mod.VoiceApp),
  { ssr: false, loading: () => <div className="flex items-center justify-center p-8"><Loader2 className="w-6 h-6 animate-spin" /></div> }
);

export default function AIReceptionistPage() {
    const [isActive, setIsActive] = useState(false);
    const [liveKitToken, setLiveKitToken] = useState<string>("");
    const [roomUrl, setRoomUrl] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);

    const handleStart = async () => {
        setIsLoading(true);
        try {
            const response = await fetch("/api/v1/voice-agent/webrtc/test", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                },
                body: JSON.stringify({}),
            });

            if (!response.ok) {
                throw new Error("Failed to start receptionist");
            }

            const data = await response.json();
            setLiveKitToken(data.token);
            setRoomUrl(data.url);
            setIsActive(true);
            toast.success("AI Receptionist is ready!");
        } catch (error: any) {
            toast.error("Failed to start", {
                description: error.message || "Please check your configuration",
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleStop = () => {
        setIsActive(false);
        setLiveKitToken("");
        setRoomUrl("");
        toast.success("AI Receptionist stopped");
    };

    return (
        <div className="container mx-auto p-6 max-w-7xl">
            <div className="mb-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                            <Bot className="w-10 h-10 text-primary" />
                            AI Receptionist
                        </h1>
                        <p className="text-lg text-muted-foreground">
                            Your 24/7 intelligent virtual assistant for customer interactions
                        </p>
                    </div>
                    <Link href="/dashboard/settings/ai">
                        <Button variant="outline" size="sm">
                            <Settings className="w-4 h-4 mr-2" />
                            Configure
                        </Button>
                    </Link>
                </div>
            </div>

            {!isActive ? (
                <div className="grid lg:grid-cols-2 gap-6">
                    {/* Launch Card */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Play className="w-5 h-5" />
                                Quick Start
                            </CardTitle>
                            <CardDescription>
                                Launch your AI receptionist and start testing
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Alert>
                                <Bot className="w-4 h-4" />
                                <AlertTitle>Ready to go</AlertTitle>
                                <AlertDescription>
                                    Your AI receptionist is configured and ready to handle customer inquiries
                                </AlertDescription>
                            </Alert>

                            <Button 
                                onClick={handleStart} 
                                disabled={isLoading}
                                size="lg"
                                className="w-full"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Starting...
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-4 h-4 mr-2" />
                                        Start AI Receptionist
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>

                    {/* Features Card */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Capabilities</CardTitle>
                            <CardDescription>
                                What your AI receptionist can do
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <div className="flex items-start gap-3">
                                <Badge variant="outline" className="mt-1">1</Badge>
                                <div>
                                    <p className="font-medium">Answer Questions</p>
                                    <p className="text-sm text-muted-foreground">
                                        Provide information about services, pricing, and availability
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <Badge variant="outline" className="mt-1">2</Badge>
                                <div>
                                    <p className="font-medium">Book Appointments</p>
                                    <p className="text-sm text-muted-foreground">
                                        Check calendar and schedule appointments automatically
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <Badge variant="outline" className="mt-1">3</Badge>
                                <div>
                                    <p className="font-medium">Handle Inquiries</p>
                                    <p className="text-sm text-muted-foreground">
                                        Respond to customer questions with natural conversation
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <Badge variant="outline" className="mt-1">4</Badge>
                                <div>
                                    <p className="font-medium">Collect Information</p>
                                    <p className="text-sm text-muted-foreground">
                                        Gather customer details and save to your CRM
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            ) : (
                <div className="h-[calc(100vh-250px)] rounded-lg border overflow-hidden shadow-lg">
                    <VoiceApp
                        token={liveKitToken}
                        serverUrl={roomUrl}
                        onDisconnect={handleStop}
                        agentName="callflow-multi-tenant"
                    />
                </div>
            )}
        </div>
    );
}

import VoiceAgentPage from "../voice-agent/page";

export default function AIReceptionistPage() {
    return <VoiceAgentPage />;
}
