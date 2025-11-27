"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Phone, Mic, AlertCircle, CheckCircle2, Info } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { voiceApi } from "@/lib/api-endpoints";
import type { VoiceWebRTCResponse } from "@/lib/types";

export default function VoiceTestPage() {
    const [testStatus, setTestStatus] = useState<"idle" | "testing" | "success" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState("");

    // Fetch test status
    const { data: testData, refetch: refetchTest } = useQuery<VoiceWebRTCResponse>({
        queryKey: ["voice-test"],
        queryFn: () => voiceApi.webrtcTest(),
        enabled: false,
    });

    const handleTest = async () => {
        setTestStatus("testing");
        setErrorMessage("");

        try {
            await refetchTest();
            setTestStatus("success");
        } catch (error: any) {
            setTestStatus("error");
            setErrorMessage(error?.response?.data?.detail || "Test failed");
        }
    };

    return (
        <div className="p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-bold mb-2">Voice Agent Test</h1>
                <p className="text-muted-foreground">
                    Test your voice agent configuration in local demo mode
                </p>
            </div>

            <Alert className="mb-6">
                <Info className="h-4 w-4" />
                <AlertTitle>Local Demo Mode</AlertTitle>
                <AlertDescription>
                    This is a simplified demo version. In production, this would connect to a real voice service.
                    Currently, you can configure settings and see how the system would work.
                </AlertDescription>
            </Alert>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Mic className="w-5 h-5" />
                            Voice Agent Status
                        </CardTitle>
                        <CardDescription>
                            Test your voice configuration
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm">Configuration Status</span>
                            <Badge variant="outline" className="gap-1">
                                <CheckCircle2 className="w-3 h-3" />
                                Ready
                            </Badge>
                        </div>

                        <div className="flex items-center justify-between">
                            <span className="text-sm">Mode</span>
                            <Badge>Local Demo</Badge>
                        </div>

                        {testData && (
                            <>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm">Model</span>
                                    <span className="text-sm font-mono">{testData.config?.model || "Not set"}</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm">Voice</span>
                                    <span className="text-sm font-mono">{testData.config?.voice || "Not set"}</span>
                                </div>
                            </>
                        )}

                        <Button
                            onClick={handleTest}
                            disabled={testStatus === "testing"}
                            className="w-full"
                        >
                            {testStatus === "testing" ? "Testing..." : "Run Test"}
                        </Button>

                        {testStatus === "success" && (
                            <Alert>
                                <CheckCircle2 className="h-4 w-4" />
                                <AlertTitle>Test Successful</AlertTitle>
                                <AlertDescription>
                                    Voice agent configuration is valid
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
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Phone className="w-5 h-5" />
                            How It Works
                        </CardTitle>
                        <CardDescription>
                            Voice agent demo flow
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-3">
                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    1
                                </div>
                                <div>
                                    <p className="text-sm font-medium">Customer calls or initiates session</p>
                                    <p className="text-xs text-muted-foreground">Via phone or web interface</p>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    2
                                </div>
                                <div>
                                    <p className="text-sm font-medium">AI agent greets with configured message</p>
                                    <p className="text-xs text-muted-foreground">Uses your custom first message</p>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    3
                                </div>
                                <div>
                                    <p className="text-sm font-medium">Processes conversation with Groq AI</p>
                                    <p className="text-xs text-muted-foreground">Using configured model and temperature</p>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    4
                                </div>
                                <div>
                                    <p className="text-sm font-medium">Uses enabled tools</p>
                                    <p className="text-xs text-muted-foreground">Check availability, book appointments, etc.</p>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold">
                                    5
                                </div>
                                <div>
                                    <p className="text-sm font-medium">Saves to database</p>
                                    <p className="text-xs text-muted-foreground">All conversations and appointments stored</p>
                                </div>
                            </div>
                        </div>

                        <div className="pt-4 border-t">
                            <p className="text-xs text-muted-foreground">
                                💡 Configure your voice agent in the Settings page to customize behavior
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
