"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Phone, Settings, Play, RefreshCw, Mic, Volume2, FileText,
  Wrench, Save, Loader2, CheckCircle, XCircle
} from "lucide-react";
import { vapiApi, assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

export default function VoiceAgentControlCenter() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("overview");
  const [assistant, setAssistant] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Quick edit state
  const [firstMessage, setFirstMessage] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await vapiApi.getMyAssistant();
      setAssistant(data);

      // Load personality for quick edit
      if (data.configured) {
        try {
          const personality = await assistantApi.getPersonality();
          setFirstMessage(personality.first_message || "");
          setSystemPrompt(personality.system_prompt || "");
        } catch { }
      }
    } catch (error) {
      console.error("Failed to load assistant:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const savePersonality = async () => {
    try {
      setSaving(true);
      await assistantApi.updatePersonality({
        first_message: firstMessage,
        system_prompt: systemPrompt,
        temperature: 0.7
      });
      toast({
        title: "Saved",
        description: "Personality updated successfully"
      });
    } catch (error) {
      console.error("Save failed:", error);
      toast({
        title: "Error",
        description: "Failed to save changes",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Receptionist Control Center</h1>
          <p className="text-muted-foreground mt-1">
            Configure and manage your voice AI assistant
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => window.location.href = "/dashboard/voice-agent/test"}>
            <Play className="w-4 h-4 mr-2" />
            Test Call
          </Button>
          <Button onClick={loadData} variant="ghost" disabled={loading}>
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* Quick Nav Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Link href="/dashboard/voice-agent/voice" className="block">
          <Card className="bg-white border-slate-200 shadow-sm hover:border-primary/50 transition-colors cursor-pointer h-full">
            <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Volume2 className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-semibold">Voice</p>
                  <p className="text-sm text-muted-foreground">Configure voice</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard/voice-agent/knowledge-base" className="block">
          <Card className="bg-white border-slate-200 shadow-sm hover:border-primary/50 transition-colors cursor-pointer h-full">
            <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <FileText className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="font-semibold">Knowledge Base</p>
                  <p className="text-sm text-muted-foreground">Upload docs</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard/voice-agent/tools" className="block">
          <Card className="bg-white border-slate-200 shadow-sm hover:border-primary/50 transition-colors cursor-pointer h-full">
            <CardContent className="bg-white border-slate-200 shadow-sm pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Wrench className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="font-semibold">Tools</p>
                  <p className="text-sm text-muted-foreground">Enable features</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>

      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">
            <Mic className="w-4 h-4 mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="personality">
            <Settings className="w-4 h-4 mr-2" />
            Quick Edit
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid gap-6">
            {/* Assistant Status */}
            <Card className="bg-white border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle>Assistant Status</CardTitle>
                <CardDescription>Current configuration</CardDescription>
              </CardHeader>
              <CardContent className="bg-white border-slate-200 shadow-sm space-y-4">
                {loading ? (
                  <div className="flex justify-center py-4">
                    <Loader2 className="h-6 w-6 animate-spin" />
                  </div>
                ) : (
                  <>
                    <div className="flex justify-between items-center p-3 bg-slate-100 rounded-lg">
                      <span className="font-medium">Status</span>
                      {assistant?.configured ? (
                        <Badge className="bg-green-600">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Active
                        </Badge>
                      ) : (
                        <Badge variant="destructive">
                          <XCircle className="w-3 h-3 mr-1" />
                          Not Configured
                        </Badge>
                      )}
                    </div>

                    <div className="flex justify-between items-center p-3 bg-slate-100 rounded-lg">
                      <span className="font-medium">Assistant ID</span>
                      <code className="text-xs bg-background px-2 py-1 rounded">
                        {assistant?.assistant_id?.slice(0, 12) || 'N/A'}...
                      </code>
                    </div>

                    <div className="flex justify-between items-center p-3 bg-slate-100 rounded-lg">
                      <span className="font-medium">Voice</span>
                      <span className="text-sm">
                        {assistant?.voice?.voiceId?.slice(0, 10) || 'Default'}...
                      </span>
                    </div>

                    <div className="flex justify-between items-center p-3 bg-slate-100 rounded-lg">
                      <span className="font-medium">Model</span>
                      <Badge variant="outline">
                        {assistant?.model?.model || 'gpt-4o-mini'}
                      </Badge>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="personality" className="mt-6">
          <Card className="bg-white border-slate-200 shadow-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Personality & Prompt</CardTitle>
                  <CardDescription>Customize how your AI responds</CardDescription>
                </div>
                <Button onClick={savePersonality} disabled={saving}>
                  {saving ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4 mr-2" />
                  )}
                  Save Changes
                </Button>
              </div>
            </CardHeader>
            <CardContent className="bg-white border-slate-200 shadow-sm space-y-6">
              <div className="space-y-2">
                <Label>First Message (Greeting)</Label>
                <Input
                  value={firstMessage}
                  onChange={(e) => setFirstMessage(e.target.value)}
                  placeholder="Hello! Thank you for calling..."
                />
                <p className="text-xs text-muted-foreground">
                  What the AI says when answering a call
                </p>
              </div>

              <div className="space-y-2">
                <Label>System Prompt (Instructions)</Label>
                <Textarea
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  placeholder="You are a helpful AI receptionist..."
                  className="min-h-[200px] font-mono text-sm"
                />
                <p className="text-xs text-muted-foreground">
                  Detailed instructions for how the AI should behave, what services to offer, business hours, etc.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
