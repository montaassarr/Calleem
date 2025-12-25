"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Loader2, Wrench, Calendar, Phone, MessageSquare, Settings } from "lucide-react";
import { assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

interface Tool {
    id: string;
    name: string;
    description: string;
    category: string;
    config: any;
}

const categoryIcons: Record<string, any> = {
    scheduling: Calendar,
    call_control: Phone,
    communication: MessageSquare,
    default: Wrench
};

export default function ToolsPage() {
    const { toast } = useToast();
    const [loading, setLoading] = useState(true);
    const [builtInTools, setBuiltInTools] = useState<Tool[]>([]);
    const [enabledTools, setEnabledTools] = useState<string[]>([]);
    const [togglingTool, setTogglingTool] = useState<string | null>(null);

    useEffect(() => {
        loadTools();
    }, []);

    const loadTools = async () => {
        try {
            setLoading(true);
            const [builtIn, enabled] = await Promise.all([
                assistantApi.getBuiltInTools(),
                assistantApi.getEnabledTools()
            ]);

            setBuiltInTools(builtIn.tools || []);

            // Extract enabled tool function names
            const enabledNames = (enabled.tools || []).map((t: any) =>
                t.function?.name || t.name || ""
            );
            setEnabledTools(enabledNames);
        } catch (error) {
            console.error("Failed to load tools:", error);
            toast({
                title: "Error",
                description: "Failed to load tools",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    const toggleTool = async (toolId: string, toolName: string) => {
        const isEnabled = enabledTools.includes(toolName);

        try {
            setTogglingTool(toolId);

            if (isEnabled) {
                await assistantApi.disableTool(toolId);
                setEnabledTools(enabledTools.filter(n => n !== toolName));
                toast({
                    title: "Disabled",
                    description: `${builtInTools.find(t => t.id === toolId)?.name} has been disabled`
                });
            } else {
                await assistantApi.enableTool(toolId);
                setEnabledTools([...enabledTools, toolName]);
                toast({
                    title: "Enabled",
                    description: `${builtInTools.find(t => t.id === toolId)?.name} has been enabled`
                });
            }
        } catch (error) {
            console.error("Toggle failed:", error);
            toast({
                title: "Error",
                description: "Failed to update tool",
                variant: "destructive"
            });
        } finally {
            setTogglingTool(null);
        }
    };

    const getToolFunctionName = (tool: Tool) => {
        return tool.config?.function?.name || tool.id;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    // Group tools by category
    const groupedTools = builtInTools.reduce((acc, tool) => {
        const category = tool.category || "other";
        if (!acc[category]) acc[category] = [];
        acc[category].push(tool);
        return acc;
    }, {} as Record<string, Tool[]>);

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Tools & Functions</h1>
                    <p className="text-muted-foreground mt-1">
                        Enable capabilities for your AI assistant
                    </p>
                </div>
                <Button variant="outline" asChild>
                    <Link href="/dashboard/voice-agent/control-center">Back to Control Center</Link>
                </Button>
            </div>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card className="bg-white border-slate-200 shadow-sm">
                    <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Tools</p>
                                <p className="text-2xl font-bold">{builtInTools.length}</p>
                            </div>
                            <Wrench className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-white border-slate-200 shadow-sm">
                    <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Enabled</p>
                                <p className="text-2xl font-bold text-green-600">{enabledTools.length}</p>
                            </div>
                            <Badge variant="default" className="bg-green-600">Active</Badge>
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-white border-slate-200 shadow-sm">
                    <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Categories</p>
                                <p className="text-2xl font-bold">{Object.keys(groupedTools).length}</p>
                            </div>
                            <Settings className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Tools by Category */}
            {Object.entries(groupedTools).map(([category, tools]) => {
                const Icon = categoryIcons[category] || categoryIcons.default;
                return (
                    <Card key={category}>
                        <CardHeader>
                            <CardTitle className="bg-white border-slate-200 shadow-sm flex items-center gap-2 capitalize">
                                <Icon className="h-5 w-5" />
                                {category.replace("_", " ")}
                            </CardTitle>
                            <CardDescription>
                                {category === "scheduling" && "Appointment booking and availability checking"}
                                {category === "call_control" && "Call management functions"}
                                {category === "communication" && "Messaging and notifications"}
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid gap-4 md:grid-cols-2">
                                {tools.map((tool) => {
                                    const functionName = getToolFunctionName(tool);
                                    const isEnabled = enabledTools.includes(functionName);
                                    const isToggling = togglingTool === tool.id;

                                    return (
                                        <div
                                            key={tool.id}
                                            className={`p-4 border rounded-lg transition-all ${isEnabled ? "border-primary bg-primary/5" : "border-border"
                                                }`}
                                        >
                                            <div className="flex items-start justify-between gap-4">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2">
                                                        <h3 className="font-semibold">{tool.name}</h3>
                                                        {isEnabled && (
                                                            <Badge variant="default" className="bg-green-600 text-xs">
                                                                Active
                                                            </Badge>
                                                        )}
                                                    </div>
                                                    <p className="text-sm text-muted-foreground mt-1">
                                                        {tool.description}
                                                    </p>
                                                    <code className="text-xs text-muted-foreground mt-2 block">
                                                        {functionName}()
                                                    </code>
                                                </div>
                                                <div className="flex items-center">
                                                    {isToggling ? (
                                                        <Loader2 className="h-4 w-4 animate-spin" />
                                                    ) : (
                                                        <Switch
                                                            checked={isEnabled}
                                                            onCheckedChange={() => toggleTool(tool.id, functionName)}
                                                        />
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>
                );
            })}
        </div>
    );
}
