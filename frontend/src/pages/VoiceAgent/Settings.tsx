import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Save,
  Settings as SettingsIcon,
  Mic,
  Code,
  Wrench,
  Sparkles,
  Loader2,
} from "lucide-react";

import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { voiceApi } from "@/api";
import type { VoiceConfiguration, VoiceModel, VoiceOption, VoiceTool } from "@/lib/types";
import { useConfig } from "@/contexts/ConfigContext";

const VoiceSettingsPage = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { refreshConfig } = useConfig();

  // Fetch current config
  const { data: config, isLoading: isConfigLoading } = useQuery({
    queryKey: ["voice-config"],
    queryFn: () => voiceApi.getConfig(),
  });

  // Fetch available models
  const { data: modelsData } = useQuery({
    queryKey: ["voice-models"],
    queryFn: () => voiceApi.getModels(),
  });

  // Fetch available voices
  const { data: voicesData } = useQuery({
    queryKey: ["voice-options"],
    queryFn: () => voiceApi.getVoices(),
  });

  // Fetch available tools
  const { data: toolsData } = useQuery({
    queryKey: ["voice-tools"],
    queryFn: () => voiceApi.getTools(),
  });

  // Local state for form
  const [formData, setFormData] = useState<Partial<VoiceConfiguration>>({});

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: VoiceConfiguration) => voiceApi.updateConfig(data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ["voice-config"] });
      await refreshConfig(); // Refresh global config
      toast({ title: "Voice configuration saved successfully" });
    },
    onError: (error: any) => {
      toast({
        variant: "destructive",
        title: "Failed to save configuration",
        description: error?.response?.data?.detail || "An error occurred",
      });
    },
  });

  // Initialize form data when config loads
  useEffect(() => {
    if (config) {
      setFormData(config);
    }
  }, [config]);

  const handleSave = () => {
    if (!formData) return;
    updateMutation.mutate(formData as VoiceConfiguration);
  };

  const updateField = <K extends keyof VoiceConfiguration>(field: K, value: VoiceConfiguration[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const toggleTool = (toolName: string) => {
    const currentTools = formData.enabled_tools || [];
    const newTools = currentTools.includes(toolName)
      ? currentTools.filter((t) => t !== toolName)
      : [...currentTools, toolName];
    updateField("enabled_tools", newTools);
  };

  if (isConfigLoading) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 ml-64">
          <DashboardHeader />
          <div className="flex items-center justify-center h-96">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </main>
      </div>
    );
  }

  const allModels: VoiceModel[] = [
    ...(modelsData?.groq || []),
    ...(modelsData?.openai || []),
  ];

  const voices = voicesData?.voices || [];
  const tools = toolsData?.tools || [];

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64">
        <DashboardHeader />
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-1">Voice Agent Configuration</h1>
              <p className="text-muted-foreground">
                Configure your AI voice receptionist just like Vapi dashboard
              </p>
            </div>
            <Button
              onClick={handleSave}
              disabled={updateMutation.isPending}
              className="gap-2"
            >
              {updateMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              Save Configuration
            </Button>
          </div>

          <Tabs defaultValue="model" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 lg:w-auto">
              <TabsTrigger value="model" className="gap-2">
                <SettingsIcon className="h-4 w-4" />
                Model
              </TabsTrigger>
              <TabsTrigger value="voice" className="gap-2">
                <Mic className="h-4 w-4" />
                Voice
              </TabsTrigger>
              <TabsTrigger value="prompt" className="gap-2">
                <Code className="h-4 w-4" />
                Prompt
              </TabsTrigger>
              <TabsTrigger value="tools" className="gap-2">
                <Wrench className="h-4 w-4" />
                Tools
              </TabsTrigger>
            </TabsList>

            {/* MODEL TAB */}
            <TabsContent value="model" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Model Configuration</CardTitle>
                  <CardDescription>
                    Choose the AI model and configure its behavior
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid gap-6 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="model_provider">Provider</Label>
                      <Select
                        value={formData.model_provider || "groq"}
                        onValueChange={(value) => updateField("model_provider", value)}
                      >
                        <SelectTrigger id="model_provider">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="groq">Groq</SelectItem>
                          <SelectItem value="openai">OpenAI</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="model_name">Model</Label>
                      <Select
                        value={formData.model_name || "llama-3.3-70b-versatile"}
                        onValueChange={(value) => updateField("model_name", value)}
                      >
                        <SelectTrigger id="model_name">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {allModels
                            .filter((m) => m.provider === (formData.model_provider || "groq"))
                            .map((model) => (
                              <SelectItem key={model.id} value={model.id}>
                                {model.name}
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="temperature">Temperature</Label>
                      <span className="text-sm text-muted-foreground">
                        {formData.temperature?.toFixed(1) || "0.7"}
                      </span>
                    </div>
                    <Slider
                      id="temperature"
                      min={0}
                      max={1}
                      step={0.1}
                      value={[formData.temperature || 0.7]}
                      onValueChange={([value]) => updateField("temperature", value)}
                      className="w-full"
                    />
                    <p className="text-xs text-muted-foreground">
                      Higher values make output more creative, lower values more focused
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="max_tokens">Max Tokens</Label>
                    <Input
                      id="max_tokens"
                      type="number"
                      value={formData.max_tokens || 500}
                      onChange={(e) => updateField("max_tokens", parseInt(e.target.value))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="first_message">First Message (Greeting)</Label>
                    <Input
                      id="first_message"
                      placeholder="Hi, this is Ava from the barbershop..."
                      value={formData.first_message || ""}
                      onChange={(e) => updateField("first_message", e.target.value)}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* VOICE TAB */}
            <TabsContent value="voice" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Voice Selection</CardTitle>
                  <CardDescription>
                    Choose the voice for your AI receptionist
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="voice_provider">Voice Provider</Label>
                    <Select
                      value={formData.voice_provider || "openai"}
                      onValueChange={(value) => updateField("voice_provider", value)}
                    >
                      <SelectTrigger id="voice_provider">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="openai">OpenAI</SelectItem>
                        <SelectItem value="elevenlabs">ElevenLabs</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3">
                    <Label>Available Voices</Label>
                    <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                      {voices
                        .filter((v) =>
                          formData.voice_provider === "elevenlabs"
                            ? v.category !== "openai"
                            : v.category === "openai"
                        )
                        .map((voice) => (
                          <Card
                            key={voice.voice_id}
                            className={`cursor-pointer transition-colors ${formData.voice_id === voice.voice_id
                              ? "border-primary bg-primary/5"
                              : "hover:border-primary/50"
                              }`}
                            onClick={() => updateField("voice_id", voice.voice_id)}
                          >
                            <CardContent className="p-4">
                              <div className="font-medium">{voice.name}</div>
                              {voice.description && (
                                <p className="text-xs text-muted-foreground mt-1">
                                  {voice.description}
                                </p>
                              )}
                              <div className="flex gap-2 mt-2 flex-wrap">
                                {voice.gender && (
                                  <span className="text-xs px-2 py-0.5 rounded-full bg-muted">
                                    {voice.gender}
                                  </span>
                                )}
                                {voice.accent && (
                                  <span className="text-xs px-2 py-0.5 rounded-full bg-muted">
                                    {voice.accent}
                                  </span>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                    </div>
                  </div>

                  {voicesData && !voicesData.elevenlabs_configured && (
                    <div className="rounded-lg border border-yellow-500/50 bg-yellow-500/10 p-4">
                      <p className="text-sm text-yellow-600 dark:text-yellow-400">
                        <strong>Note:</strong> ElevenLabs API key not configured. Add
                        ELEVENLABS_API_KEY to your environment to access more voices.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* PROMPT TAB */}
            <TabsContent value="prompt" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>System Prompt</CardTitle>
                  <CardDescription>
                    Define your AI receptionist's personality and instructions
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    id="system_prompt"
                    placeholder="You are Ava, the friendly AI receptionist for..."
                    value={formData.system_prompt || ""}
                    onChange={(e) => updateField("system_prompt", e.target.value)}
                    rows={15}
                    className="font-mono text-sm"
                  />
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="gap-2">
                      <Sparkles className="h-4 w-4" />
                      Generate with AI
                    </Button>
                  </div>
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p><strong>Available variables:</strong></p>
                    <p>• {"{"}{"{"} business_name {"}"}{"}"} - Your business name</p>
                    <p>• {"{"}{"{"} services_list {"}"}{"}"} - List of services</p>
                    <p>• {"{"}{"{"} business_hours {"}"}{"}"} - Operating hours</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* TOOLS TAB */}
            <TabsContent value="tools" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Voice Agent Tools</CardTitle>
                  <CardDescription>
                    Enable tools that allow the AI to interact with your appointment system
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {tools.map((tool) => {
                      const toolName = tool.function?.name || "";
                      const isEnabled = (formData.enabled_tools || []).includes(toolName);

                      return (
                        <div
                          key={toolName}
                          className="flex items-start justify-between p-4 rounded-lg border"
                        >
                          <div className="space-y-1">
                            <div className="font-medium">{toolName}</div>
                            <p className="text-sm text-muted-foreground">
                              {tool.function?.description}
                            </p>
                          </div>
                          <Switch
                            checked={isEnabled}
                            onCheckedChange={() => toggleTool(toolName)}
                          />
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Advanced Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="end_call_on_goodbye">End call on goodbye</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically end call when customer says goodbye
                      </p>
                    </div>
                    <Switch
                      id="end_call_on_goodbye"
                      checked={formData.end_call_on_goodbye !== false}
                      onCheckedChange={(checked) => updateField("end_call_on_goodbye", checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="record_calls">Record calls</Label>
                      <p className="text-sm text-muted-foreground">
                        Save call recordings for quality assurance
                      </p>
                    </div>
                    <Switch
                      id="record_calls"
                      checked={formData.record_calls !== false}
                      onCheckedChange={(checked) => updateField("record_calls", checked)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="silence_timeout">Silence timeout (seconds)</Label>
                    <Input
                      id="silence_timeout"
                      type="number"
                      value={formData.silence_timeout_seconds || 30}
                      onChange={(e) =>
                        updateField("silence_timeout_seconds", parseInt(e.target.value))
                      }
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
};

export default VoiceSettingsPage;
