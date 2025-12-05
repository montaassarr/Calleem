"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Save, Mic, Brain, Volume2, TestTube, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { apiEndpoints } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";

// LiveKit Cloud Inference Models (FREE - no API keys needed)
const STT_MODELS = [
  { value: "deepgram/nova-3", label: "Deepgram Nova 3", description: "Best accuracy, fastest" },
  { value: "deepgram/nova-2", label: "Deepgram Nova 2", description: "Great accuracy" },
  { value: "assemblyai/universal", label: "AssemblyAI Universal", description: "Multi-language" },
];

const LLM_MODELS = [
  { value: "openai/gpt-4o-mini", label: "GPT-4o Mini", description: "Fast, cost-effective" },
  { value: "openai/gpt-4o", label: "GPT-4o", description: "Most capable" },
  { value: "groq/llama-3.3-70b-versatile", label: "Llama 3.3 70B (Groq)", description: "Ultra fast" },
  { value: "groq/mixtral-8x7b-32768", label: "Mixtral 8x7B (Groq)", description: "Balanced" },
  { value: "anthropic/claude-3-haiku-20240307", label: "Claude 3 Haiku", description: "Fast & smart" },
];

const TTS_MODELS = [
  { value: "cartesia/sonic-2", label: "Cartesia Sonic 2", description: "Natural, fast" },
  { value: "cartesia/sonic-3", label: "Cartesia Sonic 3", description: "Latest, best quality" },
  { value: "elevenlabs/eleven_multilingual_v2", label: "ElevenLabs v2", description: "Ultra-realistic" },
  { value: "openai/tts-1", label: "OpenAI TTS-1", description: "Reliable" },
];

const TTS_VOICES = [
  { value: "79a125e8-cd45-4c13-8a67-188112f4dd22", label: "Sarah (Female, Professional)" },
  { value: "9626c31c-bec5-4cca-baa8-f8ba9e84c8bc", label: "Parker (Male, Friendly)" },
  { value: "a0e99841-438c-4a64-b679-ae501e7d6091", label: "Emma (Female, Warm)" },
  { value: "b7d50908-b17c-442d-ad8d-810c63997ed9", label: "James (Male, Professional)" },
];

interface AgentConfig {
  name: string;
  system_prompt: string;
  llm_model: string;
  stt_model: string;
  tts_model: string;
  voice_id: string;
  status: string;
}

export default function AISettingsPage() {
  const router = useRouter();
  const { toast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<AgentConfig>({
    name: "AI Receptionist",
    system_prompt: "You are a friendly AI receptionist. Help customers book appointments and answer questions.",
    llm_model: "openai/gpt-4o-mini",
    stt_model: "deepgram/nova-3",
    tts_model: "cartesia/sonic-2",
    voice_id: "79a125e8-cd45-4c13-8a67-188112f4dd22",
    status: "active",
  });

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(apiEndpoints.agents.getMyAgent(), {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      if (res.ok) {
        const agent = await res.json();
        setConfig({
          name: agent.name || "AI Receptionist",
          system_prompt: agent.system_prompt || config.system_prompt,
          llm_model: agent.llm_model || "openai/gpt-4o-mini",
          stt_model: agent.stt_model || "deepgram/nova-3",
          tts_model: agent.tts_model || "cartesia/sonic-2",
          voice_id: agent.voice_id || "79a125e8-cd45-4c13-8a67-188112f4dd22",
          status: agent.status || "active",
        });
      }
    } catch (error) {
      console.error("Failed to load config:", error);
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(apiEndpoints.agents.updateMyAgent(), {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(config),
      });

      if (res.ok) {
        toast({
          title: "Settings Saved",
          description: "Your AI configuration has been updated.",
        });
      } else {
        throw new Error("Failed to save");
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save settings. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">AI Agent Settings</h1>
            <p className="text-muted-foreground">
              Configure your voice AI models and behavior
            </p>
          </div>
        </div>
        <Button onClick={saveConfig} disabled={saving}>
          {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
          Save Changes
        </Button>
      </div>

      {/* Free Models Notice */}
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="py-4">
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className="bg-green-100 text-green-700">FREE</Badge>
            <span className="text-sm">
              All models are provided via <strong>LiveKit Cloud Inference</strong> — no external API keys required!
            </span>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="models" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="models">
            <Brain className="w-4 h-4 mr-2" />
            AI Models
          </TabsTrigger>
          <TabsTrigger value="voice">
            <Volume2 className="w-4 h-4 mr-2" />
            Voice
          </TabsTrigger>
          <TabsTrigger value="prompt">
            <TestTube className="w-4 h-4 mr-2" />
            Behavior
          </TabsTrigger>
        </TabsList>

        {/* AI Models Tab */}
        <TabsContent value="models" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="w-5 h-5" />
                Speech-to-Text (STT)
              </CardTitle>
              <CardDescription>
                Converts customer's voice into text for the AI to understand
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Select 
                value={config.stt_model} 
                onValueChange={(value) => setConfig({ ...config, stt_model: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select STT model" />
                </SelectTrigger>
                <SelectContent>
                  {STT_MODELS.map((model) => (
                    <SelectItem key={model.value} value={model.value}>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{model.label}</span>
                        <span className="text-muted-foreground text-xs">— {model.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Language Model (LLM)
              </CardTitle>
              <CardDescription>
                The brain of your AI — processes the conversation and generates responses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Select 
                value={config.llm_model} 
                onValueChange={(value) => setConfig({ ...config, llm_model: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select LLM" />
                </SelectTrigger>
                <SelectContent>
                  {LLM_MODELS.map((model) => (
                    <SelectItem key={model.value} value={model.value}>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{model.label}</span>
                        <span className="text-muted-foreground text-xs">— {model.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Volume2 className="w-5 h-5" />
                Text-to-Speech (TTS)
              </CardTitle>
              <CardDescription>
                Converts AI responses back into natural speech
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Select 
                value={config.tts_model} 
                onValueChange={(value) => setConfig({ ...config, tts_model: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select TTS model" />
                </SelectTrigger>
                <SelectContent>
                  {TTS_MODELS.map((model) => (
                    <SelectItem key={model.value} value={model.value}>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{model.label}</span>
                        <span className="text-muted-foreground text-xs">— {model.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Voice Tab */}
        <TabsContent value="voice" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Voice Selection</CardTitle>
              <CardDescription>
                Choose the voice your AI will use when speaking to customers
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Voice</Label>
                <Select 
                  value={config.voice_id} 
                  onValueChange={(value) => setConfig({ ...config, voice_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select voice" />
                  </SelectTrigger>
                  <SelectContent>
                    {TTS_VOICES.map((voice) => (
                      <SelectItem key={voice.value} value={voice.value}>
                        {voice.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Behavior Tab */}
        <TabsContent value="prompt" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Name</CardTitle>
              <CardDescription>
                What should customers call your AI receptionist?
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Input
                value={config.name}
                onChange={(e) => setConfig({ ...config, name: e.target.value })}
                placeholder="AI Receptionist"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Prompt</CardTitle>
              <CardDescription>
                Instructions that define your AI's personality and behavior
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                value={config.system_prompt}
                onChange={(e) => setConfig({ ...config, system_prompt: e.target.value })}
                placeholder="You are a friendly AI receptionist..."
                rows={6}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Test Button */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Test Your Agent</h3>
              <p className="text-sm text-muted-foreground">
                Try a test call to hear your new configuration
              </p>
            </div>
            <Button onClick={() => router.push("/dashboard/voice-agent/test")}>
              <TestTube className="w-4 h-4 mr-2" />
              Start Test Call
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
