"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Save, ArrowLeft, Sparkles, Mic, MessageSquare, Zap, Play, Code, TestTube2 } from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import Link from "next/link";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import api from "@/lib/api";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

interface AgentConfig {
    id?: string;
    name: string;
    system_prompt: string;
    voice_settings: {
        provider: string;
        voice_id: string;
        stability?: number;
        similarity_boost?: number;
    };
    llm_model: string;
    llm_temperature: number;
    greeting_enabled?: boolean;
    greeting_message?: string;
}

export default function AISettingsPage() {
    const router = useRouter();
    const queryClient = useQueryClient();
    
    const [settings, setSettings] = useState<Partial<AgentConfig>>({
        name: "My AI Receptionist",
        llm_model: "llama-3.3-70b-versatile",
        llm_temperature: 0.7,
        system_prompt: "",
        voice_settings: {
            provider: "cartesia",
            voice_id: "79a125e8-cd45-4c13-8a67-188112f4dd22",
            stability: 0.5,
        },
        greeting_enabled: true,
        greeting_message: "Hello! I'm your AI receptionist. How can I help you today?",
    });

    const { data: agent, isLoading } = useQuery<AgentConfig>({
        queryKey: ["my-agent"],
        queryFn: async () => {
            const response = await api.get("/agents/my-agent");
            return response;
        },
    });

    useEffect(() => {
        if (agent) {
            setSettings(agent);
        }
    }, [agent]);

    const updateMutation = useMutation({
        mutationFn: async (data: Partial<AgentConfig>) => {
            return await api.put("/agents/my-agent", data);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["my-agent"] });
            toast.success("✅ Agent configuration saved!");
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || "Failed to save configuration");
        },
    });

    const handleSave = () => {
        updateMutation.mutate(settings);
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading agent configuration...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
            {/* Header */}
            <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => router.push('/dashboard/settings')}
                            >
                                <ArrowLeft className="w-5 h-5" />
                            </Button>
                            <div>
                                <h1 className="text-2xl font-bold flex items-center gap-2">
                                    <Sparkles className="w-6 h-6 text-primary" />
                                    Agent Builder
                                </h1>
                                <p className="text-sm text-muted-foreground">
                                    Configure your voice agent without writing code
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <Link href="/dashboard/voice-agent/chat">
                                <Button variant="outline" className="gap-2">
                                    <MessageSquare className="w-4 h-4" />
                                    Test Agent
                                </Button>
                            </Link>
                            <Button
                                className="gap-2 bg-primary"
                                onClick={handleSave}
                                disabled={updateMutation.isPending}
                            >
                                <Save className="w-4 h-4" />
                                {updateMutation.isPending ? "Deploying..." : "Deploy Agent"}
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="container mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Configuration */}
                    <div className="lg:col-span-2 space-y-6">
                        
                        {/* Agent Name */}
                        <div className="glass rounded-2xl p-6">
                            <h2 className="text-lg font-semibold mb-4">Agent Name</h2>
                            <Input
                                value={settings.name}
                                onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                                className="glass-strong"
                                placeholder="My AI Receptionist"
                            />
                            <p className="text-xs text-muted-foreground mt-2">
                                Used for agent identification and dispatch
                            </p>
                        </div>

                        {/* Instructions */}
                        <div className="glass rounded-2xl p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <MessageSquare className="w-5 h-5 text-primary" />
                                <h2 className="text-lg font-semibold">Instructions</h2>
                            </div>
                            <p className="text-sm text-muted-foreground mb-4">
                                Write a prompt to control your agent's identity and behavior. This is the most important component of any agent.
                            </p>
                            <Textarea
                                value={settings.system_prompt}
                                onChange={(e) => setSettings({ ...settings, system_prompt: e.target.value })}
                                className="glass-strong font-mono text-sm min-h-[300px]"
                                placeholder="You are a friendly and professional AI receptionist. Your job is to help customers book appointments, answer questions, and provide excellent service..."
                            />
                            <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
                                <Sparkles className="w-3 h-3" />
                                <span>Use {'{{metadata.variable}}'} for dynamic content</span>
                            </div>
                        </div>

                        {/* Welcome Greeting */}
                        <div className="glass rounded-2xl p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-lg font-semibold">Welcome Greeting</h2>
                                <Switch
                                    checked={settings.greeting_enabled}
                                    onCheckedChange={(checked) => setSettings({ ...settings, greeting_enabled: checked })}
                                />
                            </div>
                            {settings.greeting_enabled && (
                                <>
                                    <p className="text-sm text-muted-foreground mb-3">
                                        Customize what your agent says when a user joins the call
                                    </p>
                                    <Textarea
                                        value={settings.greeting_message}
                                        onChange={(e) => setSettings({ ...settings, greeting_message: e.target.value })}
                                        className="glass-strong"
                                        rows={3}
                                        placeholder="Hello! I'm your AI receptionist. How can I help you today?"
                                    />
                                </>
                            )}
                        </div>

                        {/* Models */}
                        <div className="glass rounded-2xl p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <Zap className="w-5 h-5 text-primary" />
                                <h2 className="text-lg font-semibold">Models</h2>
                            </div>
                            <p className="text-sm text-muted-foreground mb-4">
                                Configure the STT-LLM-TTS pipeline for your agent
                            </p>
                            
                            <Tabs defaultValue="llm" className="w-full">
                                <TabsList className="grid w-full grid-cols-3 glass-strong">
                                    <TabsTrigger value="llm">LLM</TabsTrigger>
                                    <TabsTrigger value="tts">TTS</TabsTrigger>
                                    <TabsTrigger value="stt">STT</TabsTrigger>
                                </TabsList>
                                
                                <TabsContent value="llm" className="space-y-4 mt-4">
                                    <div>
                                        <Label>Language Model</Label>
                                        <Select 
                                            value={settings.llm_model} 
                                            onValueChange={(value) => setSettings({ ...settings, llm_model: value })}
                                        >
                                            <SelectTrigger className="glass-strong mt-2">
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="llama-3.3-70b-versatile">Llama 3.3 70B (Recommended)</SelectItem>
                                                <SelectItem value="llama-3.1-70b-versatile">Llama 3.1 70B</SelectItem>
                                                <SelectItem value="mixtral-8x7b-32768">Mixtral 8x7B</SelectItem>
                                                <SelectItem value="gpt-4">GPT-4 (Requires API Key)</SelectItem>
                                                <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    
                                    <div>
                                        <div className="flex items-center justify-between mb-2">
                                            <Label>Temperature</Label>
                                            <span className="text-sm text-muted-foreground">
                                                {settings.llm_temperature?.toFixed(1) || '0.7'}
                                            </span>
                                        </div>
                                        <Slider
                                            value={[settings.llm_temperature || 0.7]}
                                            onValueChange={([value]) => setSettings({ ...settings, llm_temperature: value })}
                                            min={0}
                                            max={1}
                                            step={0.1}
                                            className="mt-2"
                                        />
                                        <p className="text-xs text-muted-foreground mt-2">
                                            Higher values = more creative, Lower values = more focused
                                        </p>
                                    </div>
                                </TabsContent>
                                
                                <TabsContent value="tts" className="space-y-4 mt-4">
                                    <div>
                                        <Label>Voice Provider</Label>
                                        <Select 
                                            value={settings.voice_settings?.provider} 
                                            onValueChange={(value) => setSettings({ 
                                                ...settings, 
                                                voice_settings: { ...settings.voice_settings!, provider: value }
                                            })}
                                        >
                                            <SelectTrigger className="glass-strong mt-2">
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="cartesia">Cartesia (Fast & Natural)</SelectItem>
                                                <SelectItem value="elevenlabs">ElevenLabs (Premium)</SelectItem>
                                                <SelectItem value="openai">OpenAI TTS</SelectItem>
                                                <SelectItem value="deepgram">Deepgram Aura</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    
                                    <div>
                                        <Label>Voice ID</Label>
                                        <Input
                                            value={settings.voice_settings?.voice_id || ''}
                                            onChange={(e) => setSettings({ 
                                                ...settings, 
                                                voice_settings: { ...settings.voice_settings!, voice_id: e.target.value }
                                            })}
                                            className="glass-strong mt-2 font-mono text-sm"
                                            placeholder="79a125e8-cd45-4c13-8a67-188112f4dd22"
                                        />
                                    </div>
                                    
                                    <div>
                                        <div className="flex items-center justify-between mb-2">
                                            <Label>Stability</Label>
                                            <span className="text-sm text-muted-foreground">
                                                {settings.voice_settings?.stability?.toFixed(2) || '0.50'}
                                            </span>
                                        </div>
                                        <Slider
                                            value={[settings.voice_settings?.stability || 0.5]}
                                            onValueChange={([value]) => setSettings({ 
                                                ...settings, 
                                                voice_settings: { ...settings.voice_settings!, stability: value }
                                            })}
                                            min={0}
                                            max={1}
                                            step={0.05}
                                            className="mt-2"
                                        />
                                    </div>
                                </TabsContent>
                                
                                <TabsContent value="stt" className="mt-4">
                                    <Alert className="glass-strong">
                                        <AlertDescription>
                                            Speech-to-text is automatically configured with Deepgram Nova-2 for best accuracy.
                                        </AlertDescription>
                                    </Alert>
                                </TabsContent>
                            </Tabs>
                        </div>

                        {/* Actions/Tools */}
                        <div className="glass rounded-2xl p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <Code className="w-5 h-5 text-primary" />
                                <h2 className="text-lg font-semibold">Actions</h2>
                            </div>
                            <p className="text-sm text-muted-foreground mb-4">
                                Extend your agent's functionality with tools and API integrations
                            </p>
                            <Alert className="glass-strong border-primary/20">
                                <Zap className="w-4 h-4" />
                                <AlertDescription>
                                    <strong>Built-in Tools:</strong> Your agent includes appointment booking, 
                                    weather lookup, discount calculator, and business status checker.
                                </AlertDescription>
                            </Alert>
                        </div>
                    </div>

                    {/* Sidebar - Info & Preview */}
                    <div className="space-y-6">
                        {/* Quick Info */}
                        <div className="glass rounded-2xl p-6">
                            <h3 className="font-semibold mb-4 flex items-center gap-2">
                                <Sparkles className="w-4 h-4 text-primary" />
                                Agent Features
                            </h3>
                            <div className="space-y-3 text-sm">
                                <div className="flex items-start gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2"></div>
                                    <div>
                                        <strong>Background voice cancellation</strong> for better comprehension
                                    </div>
                                </div>
                                <div className="flex items-start gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2"></div>
                                    <div>
                                        <strong>Preemptive generation</strong> for reduced latency
                                    </div>
                                </div>
                                <div className="flex items-start gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2"></div>
                                    <div>
                                        <strong>Turn detector</strong> for natural conversations
                                    </div>
                                </div>
                                <div className="flex items-start gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2"></div>
                                    <div>
                                        <strong>Function calling</strong> with built-in tools
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Preview */}
                        <div className="glass rounded-2xl p-6">
                            <h3 className="font-semibold mb-4 flex items-center gap-2">
                                <Play className="w-4 h-4 text-primary" />
                                Agent Preview
                            </h3>
                            <p className="text-sm text-muted-foreground mb-4">
                                Test your agent live as you configure it
                            </p>
                            <Link href="/dashboard/voice-agent/chat">
                                <Button className="w-full gap-2" variant="outline">
                                    <MessageSquare className="w-4 h-4" />
                                    Launch Test Session
                                </Button>
                            </Link>
                        </div>

                        {/* Variables Hint */}
                        <div className="glass rounded-2xl p-6">
                            <h3 className="font-semibold mb-3 text-sm">Dynamic Variables</h3>
                            <div className="space-y-2 text-xs text-muted-foreground">
                                <code className="block p-2 glass-strong rounded">
                                    {'{{metadata.user_name}}'}
                                </code>
                                <code className="block p-2 glass-strong rounded">
                                    {'{{metadata.business_name}}'}
                                </code>
                                <p className="mt-2">
                                    Use variables in instructions and greetings for personalization
                                </p>
                            </div>
                        </div>

                        {/* Status */}
                        {agent && (
                            <div className="glass rounded-2xl p-6">
                                <h3 className="font-semibold mb-3 text-sm">Deployment Status</h3>
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                    <span className="text-sm text-muted-foreground">Active</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
