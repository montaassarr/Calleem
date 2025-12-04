"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Phone, PhoneCall, Settings, Zap, TrendingUp, Play, Pause, Plus, Edit, Trash2, RefreshCw } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { apiEndpoints } from "@/lib/api-endpoints";

interface VoiceAgent {
  id: string;
  name: string;
  status: "active" | "inactive" | "testing";
  livekit_queue?: string;
  phone_numbers: PhoneNumber[];
  total_calls: number;
  successful_calls: number;
  created_at: string;
}

interface PhoneNumber {
  id: string;
  number: string;
  provider: "livekit" | "twilio" | "external";
  status: "active" | "inactive";
  country: string;
}

interface CallStats {
  today: number;
  this_week: number;
  this_month: number;
  total_duration_minutes: number;
  average_duration_minutes: number;
  success_rate: number;
  successful_calls?: number; // Optional for backward compatibility
}

export default function VoiceAgentControlCenter() {
  const [agent, setAgent] = useState<VoiceAgent | null>(null);
  const [phoneNumbers, setPhoneNumbers] = useState<PhoneNumber[]>([]);
  const [callStats, setCallStats] = useState<CallStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    loadData();
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const [agentRes, phoneRes, statsRes] = await Promise.all([
        fetch(apiEndpoints.agents.getMyAgent(), {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(apiEndpoints.voiceAgent.phoneNumbers(), {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(apiEndpoints.voiceAgent.stats(), {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (agentRes.ok) setAgent(await agentRes.json());
      if (phoneRes.ok) setPhoneNumbers(await phoneRes.json());
      if (statsRes.ok) setCallStats(await statsRes.json());
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfigureAgent = () => {
    window.location.href = "/dashboard/settings/ai";
  };

  const handleBuyPhoneNumber = () => {
    window.location.href = "/dashboard/voice-agent/phone-numbers/buy";
  };

  const handleToggleAgent = async (agentId: string, currentStatus: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const newStatus = currentStatus === "active" ? "inactive" : "active";
      const res = await fetch(apiEndpoints.agents.update(agentId), {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (res.ok) {
        await loadData();
      }
    } catch (error) {
      console.error("Failed to toggle agent:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Voice Agent Control Center</h1>
          <p className="text-muted-foreground mt-1">
            Manage your AI receptionists, phone numbers, and automations - all in one place
          </p>
        </div>
        <div className="flex gap-3">
          <Button onClick={loadData} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={handleBuyPhoneNumber} variant="outline">
            <Phone className="w-4 h-4 mr-2" />
            Buy Phone Number
          </Button>
          <Button onClick={handleConfigureAgent}>
            <Settings className="w-4 h-4 mr-2" />
            Configure AI
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Today's Calls</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{callStats?.today || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              +{Math.round(((callStats?.today || 0) / Math.max(callStats?.this_week || 1, 1)) * 100)}% from avg
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">This Week</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{callStats?.this_week || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {callStats?.average_duration_minutes.toFixed(1)} min avg duration
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{callStats?.success_rate.toFixed(0)}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              {callStats?.successful_calls || 0} successful calls
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Agent Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{agent?.status === "active" ? "Active" : "Inactive"}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {phoneNumbers.filter(p => p.status === "active").length} phone numbers
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">
            <TrendingUp className="w-4 h-4 mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="agents">
            <PhoneCall className="w-4 h-4 mr-2" />
            AI Agents
          </TabsTrigger>
          <TabsTrigger value="phones">
            <Phone className="w-4 h-4 mr-2" />
            Phone Numbers
          </TabsTrigger>
          <TabsTrigger value="automations">
            <Zap className="w-4 h-4 mr-2" />
            Automations
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4 mt-6">
          <Alert>
            <AlertDescription>
              🎉 <strong>Everything is managed here!</strong> LiveKit queues, n8n automations, and reporting are all wired
              through this control center—no external Vapi dashboards required.
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks to get you started</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button variant="outline" className="h-20 justify-start" onClick={handleConfigureAgent}>
                <div className="flex items-start gap-3">
                  <Settings className="w-5 h-5 mt-1" />
                  <div className="text-left">
                    <div className="font-semibold">Configure AI Agent</div>
                    <div className="text-sm text-muted-foreground">Manage voice, prompt, and tools</div>
                  </div>
                </div>
              </Button>

              <Button variant="outline" className="h-20 justify-start" onClick={handleBuyPhoneNumber}>
                <div className="flex items-start gap-3">
                  <Phone className="w-5 h-5 mt-1" />
                  <div className="text-left">
                    <div className="font-semibold">Buy Phone Number</div>
                    <div className="text-sm text-muted-foreground">Get a new number for your agent</div>
                  </div>
                </div>
              </Button>

              <Button variant="outline" className="h-20 justify-start" onClick={() => window.location.href = "/dashboard/voice-agent/test"}>
                <div className="flex items-start gap-3">
                  <Play className="w-5 h-5 mt-1" />
                  <div className="text-left">
                    <div className="font-semibold">Test Agent</div>
                    <div className="text-sm text-muted-foreground">Try your agent with test calls</div>
                  </div>
                </div>
              </Button>

              <Button variant="outline" className="h-20 justify-start" onClick={() => setActiveTab("automations")}>
                <div className="flex items-start gap-3">
                  <Zap className="w-5 h-5 mt-1" />
                  <div className="text-left">
                    <div className="font-semibold">Configure Automations</div>
                    <div className="text-sm text-muted-foreground">Set up WhatsApp, Calendar sync, etc.</div>
                  </div>
                </div>
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Agent Tab */}
        <TabsContent value="agents" className="space-y-4 mt-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Your AI Agent Configuration</h2>
            <Button onClick={handleConfigureAgent}>
              <Settings className="w-4 h-4 mr-2" />
              Configure Agent
            </Button>
          </div>

          {!agent ? (
            <Card>
              <CardContent className="py-12 text-center">
                <PhoneCall className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Loading agent...</h3>
                <p className="text-muted-foreground mb-4">Your AI receptionist configuration is being loaded</p>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle>{agent.name}</CardTitle>
                    <CardDescription>
                      AI receptionist for your business
                    </CardDescription>
                  </div>
                  <Badge variant={agent.status === "active" ? "default" : "secondary"}>
                    {agent.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold">{agent.total_calls || 0}</div>
                    <div className="text-sm text-muted-foreground">Total Calls</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">{agent.successful_calls || 0}</div>
                    <div className="text-sm text-muted-foreground">Successful</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {agent.total_calls > 0 
                        ? Math.round((agent.successful_calls / agent.total_calls) * 100) 
                        : 0}%
                    </div>
                    <div className="text-sm text-muted-foreground">Success Rate</div>
                  </div>
                </div>

                <div className="flex gap-2 justify-end">
                  <Button variant="outline" size="sm" onClick={handleConfigureAgent}>
                    <Edit className="w-4 h-4 mr-2" />
                    Edit Configuration
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => window.location.href = "/dashboard/voice-agent/test"}>
                    <Play className="w-4 h-4 mr-2" />
                    Test Agent
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Phone Numbers Tab */}
        <TabsContent value="phones" className="space-y-4 mt-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Phone Numbers</h2>
            <Button onClick={handleBuyPhoneNumber}>
              <Plus className="w-4 h-4 mr-2" />
              Buy Number
            </Button>
          </div>

          {phoneNumbers.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Phone className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No phone numbers yet</h3>
                <p className="text-muted-foreground mb-4">Buy a phone number to receive calls</p>
                <Button onClick={handleBuyPhoneNumber}>Buy Your First Number</Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {phoneNumbers.map((phone) => (
                <Card key={phone.id}>
                  <CardContent className="py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <Phone className="w-5 h-5 text-muted-foreground" />
                        <div>
                          <div className="font-semibold">{phone.number}</div>
                          <div className="text-sm text-muted-foreground">
                            {phone.provider.toUpperCase()} • {phone.country}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge variant={phone.status === "active" ? "default" : "secondary"}>
                          {phone.status}
                        </Badge>
                        <Button variant="outline" size="sm">
                          <Settings className="w-4 h-4 mr-2" />
                          Configure
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Automations Tab */}
        <TabsContent value="automations" className="space-y-4 mt-6">
          <h2 className="text-2xl font-bold">Automation Workflows</h2>
          <p className="text-muted-foreground">
            Configure what happens automatically when appointments are booked or calls end
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Google Calendar Sync</CardTitle>
                <CardDescription>Automatically add appointments to your calendar</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Status</span>
                    <Badge variant="outline">Not Connected</Badge>
                  </div>
                  <Button className="w-full">Connect Google Calendar</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>WhatsApp Notifications</CardTitle>
                <CardDescription>Send confirmations and reminders via WhatsApp</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Status</span>
                    <Badge variant="outline">Not Connected</Badge>
                  </div>
                  <Button className="w-full">Connect WhatsApp</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Email Notifications</CardTitle>
                <CardDescription>Receive email alerts for new bookings</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Status</span>
                    <Badge variant="default">Active</Badge>
                  </div>
                  <Button variant="outline" className="w-full">Configure</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Slack Notifications</CardTitle>
                <CardDescription>Get notified in Slack for every call</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Status</span>
                    <Badge variant="outline">Not Connected</Badge>
                  </div>
                  <Button className="w-full">Connect Slack</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
