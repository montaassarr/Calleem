"use client";

import { useState, useEffect, useCallback } from "react";
import { Switch } from "@/components/ui/switch";
import { Loader2, Wrench, Calendar, Phone, MessageSquare, Settings } from "lucide-react";
import { assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

interface Tool { id: string; name: string; description: string; category: string; config: any; }

const categoryIcons: Record<string, any> = { scheduling: Calendar, call_control: Phone, communication: MessageSquare, default: Wrench };
const categoryColors: Record<string, string> = { scheduling: "from-[#187848] to-[#0a4c2f]", call_control: "from-blue-500 to-blue-600", communication: "from-purple-500 to-purple-600", default: "from-gray-500 to-gray-600" };

export default function ToolsPage() {
    const { toast } = useToast();
    const [loading, setLoading] = useState(true);
    const [builtInTools, setBuiltInTools] = useState<Tool[]>([]);
    const [enabledTools, setEnabledTools] = useState<string[]>([]);
    const [togglingTool, setTogglingTool] = useState<string | null>(null);

    const loadTools = useCallback(async () => {
        try {
            setLoading(true);
            const [builtIn, enabled] = await Promise.all([assistantApi.getBuiltInTools(), assistantApi.getEnabledTools()]);
            setBuiltInTools(builtIn.tools || []);
            setEnabledTools((enabled.tools || []).map((t: any) => t.tool_id || t.id || "").filter(Boolean));
        } catch { toast({ title: "Error", description: "Failed to load tools", variant: "destructive" }); }
        finally { setLoading(false); }
    }, [toast]);

    useEffect(() => { loadTools(); }, [loadTools]);

    const toggleTool = async (toolId: string) => {
        const isEnabled = enabledTools.includes(toolId);
        try {
            setTogglingTool(toolId);
            if (isEnabled) { await assistantApi.disableTool(toolId); setEnabledTools(enabledTools.filter(n => n !== toolId)); toast({ title: "Disabled", description: `${builtInTools.find(t => t.id === toolId)?.name} disabled` }); }
            else { await assistantApi.enableTool(toolId); setEnabledTools([...enabledTools, toolId]); toast({ title: "Enabled", description: `${builtInTools.find(t => t.id === toolId)?.name} enabled` }); }
        } catch { toast({ title: "Error", description: "Failed to update tool", variant: "destructive" }); }
        finally { setTogglingTool(null); }
    };

    if (loading) return <div className="flex items-center justify-center h-96"><Loader2 className="h-8 w-8 animate-spin text-[#0a4c2f]" /></div>;

    const groupedTools = builtInTools.reduce((acc, tool) => { const cat = tool.category || "other"; if (!acc[cat]) acc[cat] = []; acc[cat].push(tool); return acc; }, {} as Record<string, Tool[]>);

    return (
        <div>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Tools & Functions</h1>
                    <p className="text-[14px] text-gray-500 font-medium">Enable capabilities for your AI assistant.</p>
                </div>
                <Link href="/dashboard/voice-agent/control-center" className="px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-[20px] font-semibold hover:bg-gray-50 transition-colors text-sm shadow-sm">
                    Back to Control Center
                </Link>
            </div>

            {/* Stats */}
            <div className="grid gap-4 grid-cols-3 mb-8">
                {[
                    { label: "Total Tools", value: builtInTools.length, icon: Wrench },
                    { label: "Enabled", value: enabledTools.length, extra: <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700">Active</span> },
                    { label: "Categories", value: Object.keys(groupedTools).length, icon: Settings },
                ].map((stat, i) => (
                    <div key={i} className="bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-5">
                        <p className="text-sm text-gray-500 font-medium">{stat.label}</p>
                        <div className="flex items-center justify-between mt-1">
                            <p className="text-[28px] font-bold text-gray-900">{stat.value}</p>
                            {stat.extra || (stat.icon && <stat.icon className="h-6 w-6 text-gray-400" />)}
                        </div>
                    </div>
                ))}
            </div>

            {/* Tools by Category */}
            {Object.entries(groupedTools).map(([category, tools]) => {
                const Icon = categoryIcons[category] || categoryIcons.default;
                const color = categoryColors[category] || categoryColors.default;
                return (
                    <div key={category} className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6 mb-6">
                        <div className="flex items-center gap-3 mb-2">
                            <div className={`p-2 rounded-xl bg-gradient-to-br ${color} text-white`}><Icon className="h-5 w-5" /></div>
                            <h3 className="font-bold text-lg text-gray-900 capitalize">{category.replace("_", " ")}</h3>
                        </div>
                        <p className="text-sm text-gray-500 mb-6">
                            {category === "scheduling" && "Appointment booking and availability checking"}
                            {category === "call_control" && "Call management functions"}
                            {category === "communication" && "Messaging and notifications"}
                        </p>

                        <div className="grid gap-4 md:grid-cols-2">
                            {tools.map((tool) => {
                                const isEnabled = enabledTools.includes(tool.id);
                                const isToggling = togglingTool === tool.id;
                                return (
                                    <div key={tool.id} className={`p-4 rounded-xl border transition-all ${isEnabled ? "border-[#0a4c2f]/30 bg-[#0a4c2f]/5" : "border-gray-100 bg-gray-50"}`}>
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <h4 className="font-bold text-gray-900">{tool.name}</h4>
                                                    {isEnabled && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700">Active</span>}
                                                </div>
                                                <p className="text-sm text-gray-500 mt-1">{tool.description}</p>
                                                <code className="text-xs text-gray-400 mt-2 block">{tool.config?.function?.name || tool.id}()</code>
                                            </div>
                                            {isToggling ? <Loader2 className="h-4 w-4 animate-spin text-[#0a4c2f]" /> : <Switch checked={isEnabled} onCheckedChange={() => toggleTool(tool.id)} />}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
