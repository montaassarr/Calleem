import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Vapi from "@vapi-ai/web";
import {
  Activity,
  AlertTriangle,
  History,
  Mic,
  MicOff,
  PhoneCall,
  PhoneOff,
  Radio,
  RefreshCcw,
  ShieldCheck,
  Waves,
} from "lucide-react";

import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { voiceApi, businessConfigApi } from "@/api";
import { useToast } from "@/hooks/use-toast";
import type { VoiceCallHistoryItem } from "@/lib/types";
import { Link } from "react-router-dom";

const formatDate = (value?: string) => {
  if (!value) return "Unknown";
  try {
    return new Date(value).toLocaleString();
  } catch (error) {
    return value;
  }
};

type WebCallState = "idle" | "connecting" | "live";

const VoiceAgentPage = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const publicKey = import.meta.env.VITE_VAPI_PUBLIC_KEY;
  const assistantIdOverride = import.meta.env.VITE_VAPI_ASSISTANT_ID;

  const [customerNumber, setCustomerNumber] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [callNotes, setCallNotes] = useState("");
  const [webCallState, setWebCallState] = useState<WebCallState>("idle");
  const [webCallError, setWebCallError] = useState<string | null>(null);
  const [muted, setMuted] = useState(false);
  const [vapiClient, setVapiClient] = useState<Vapi | null>(null);

  const {
    data: businessConfig,
    isLoading: isConfigLoading,
    isError: isConfigError,
  } = useQuery({
    queryKey: ["business-config"],
    queryFn: () => businessConfigApi.getConfig(),
  });

  const voiceFeatureEnabled = businessConfig?.features_enabled?.voice_agent ?? false;

  const {
    data: voiceStatus,
    isLoading: isStatusLoading,
    isError: isStatusError,
    error: voiceStatusError,
  } = useQuery({
    queryKey: ["voice-agent", "status"],
    queryFn: () => voiceApi.testAgent(),
    enabled: voiceFeatureEnabled,
    retry: 1,
    refetchOnWindowFocus: false,
  });

  const {
    data: callHistory,
    isLoading: isHistoryLoading,
    isError: isHistoryError,
  } = useQuery({
    queryKey: ["voice-agent", "history"],
    queryFn: () => voiceApi.callHistory(25),
    enabled: voiceFeatureEnabled,
    refetchInterval: 30000,
  });

  useEffect(() => {
    if (!publicKey) {
      setVapiClient(null);
      return;
    }

    const client = new Vapi(publicKey);
    setVapiClient(client);

    return () => {
      try {
        client.stop?.();
      } catch (error) {
        // no-op cleanup
      }
    };
  }, [publicKey]);

  useEffect(() => {
    if (webCallState === "idle") {
      setMuted(false);
      setWebCallError(null);
    }
  }, [webCallState]);

  const featureMutation = useMutation({
    mutationFn: (enabled: boolean) =>
      businessConfigApi.updateFeatureFlags({
        ...(businessConfig?.features_enabled || {}),
        voice_agent: enabled,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["business-config"] });
      toast({
        title: "Voice agent updated",
        description: "Feature flag saved",
      });
    },
    onError: (error: any) => {
      toast({
        variant: "destructive",
        title: "Failed to update voice settings",
        description: error?.response?.data?.detail || "Unexpected error",
      });
    },
  });

  const startCallMutation = useMutation({
    mutationFn: () =>
      voiceApi.startCall({
        customer_number: customerNumber,
        customer_name: customerName || undefined,
        metadata: callNotes ? { notes: callNotes } : undefined,
      }),
    onSuccess: () => {
      toast({
        title: "Call queued",
        description: "Vapi is dialing the client",
      });
      setCustomerNumber("");
      setCustomerName("");
      setCallNotes("");
      queryClient.invalidateQueries({ queryKey: ["voice-agent", "history"] });
    },
    onError: (error: any) => {
      toast({
        variant: "destructive",
        title: "Call failed",
        description: error?.response?.data?.detail || "Unable to start call",
      });
    },
  });

  const assistantId = useMemo(() => {
    return assistantIdOverride || voiceStatus?.assistant_id || null;
  }, [assistantIdOverride, voiceStatus?.assistant_id]);

  const handleStartWebCall = async () => {
    if (!vapiClient) {
      toast({
        variant: "destructive",
        title: "Missing Vapi public key",
        description: "Set VITE_VAPI_PUBLIC_KEY to enable in-browser calls",
      });
      return;
    }

    if (!assistantId) {
      toast({
        variant: "destructive",
        title: "Assistant unavailable",
        description: "Enable the voice agent and re-run diagnostics",
      });
      return;
    }

    try {
      setWebCallState("connecting");
      setWebCallError(null);
      await vapiClient.start(assistantId);
      setWebCallState("live");
      toast({ title: "Browser call started", description: "You are live with the agent" });
    } catch (error: any) {
      setWebCallState("idle");
      setWebCallError(error?.message || "Unable to start WebRTC session");
      toast({
        variant: "destructive",
        title: "Web call failed",
        description: error?.message || "Check console for details",
      });
    }
  };

  const handleStopWebCall = async () => {
    if (!vapiClient) return;
    try {
      await vapiClient.stop?.();
    } finally {
      setWebCallState("idle");
    }
  };

  const handleToggleMute = () => {
    if (!vapiClient) return;
    const nextMuted = !muted;
    try {
      vapiClient.setMuted?.(nextMuted);
      setMuted(nextMuted);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Mute toggle failed",
        description: "Browser client did not accept the command",
      });
    }
  };

  const canStartCall = customerNumber.trim().length >= 8;
  const callItems: VoiceCallHistoryItem[] = callHistory?.items || [];

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64">
        <DashboardHeader />
        <div className="p-6 space-y-6">
          <div>
            <h1 className="text-3xl font-bold mb-1">Voice Agent Control Room</h1>
            <p className="text-muted-foreground">
              Monitor the Groq-powered Vapi assistant, start outbound tests, and run WebRTC sessions.
            </p>
          </div>

          {!voiceFeatureEnabled && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Voice agent is disabled</AlertTitle>
              <AlertDescription>
                Toggle the feature flag below to enable the Vapi integration for this business. Requests will fail until
                it is enabled.
              </AlertDescription>
            </Alert>
          )}

          {!publicKey && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Missing Vapi public key</AlertTitle>
              <AlertDescription>
                Set <code className="font-mono">VITE_VAPI_PUBLIC_KEY</code> in your frontend .env file to test in-browser calls.
              </AlertDescription>
            </Alert>
          )}

          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            <div className="glass rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Feature Flag</p>
                  <h3 className="text-lg font-semibold">Voice Agent Access</h3>
                </div>
                <Switch
                  checked={voiceFeatureEnabled}
                  disabled={featureMutation.isPending || isConfigLoading || isConfigError}
                  onCheckedChange={(checked) => featureMutation.mutate(checked)}
                />
              </div>
              <p className="text-sm text-muted-foreground">
                When enabled, authenticated dashboard users can trigger the Vapi assistant and view call history.
              </p>
              <div className="flex items-center gap-2 text-xs">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                <span>{voiceFeatureEnabled ? "Enabled for this business" : "Disabled until toggled on"}</span>
              </div>
            </div>

            <div className="glass rounded-2xl p-5 space-y-3">
              <div className="flex items-center gap-3">
                <Radio className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-sm text-muted-foreground">Backend Diagnostics</p>
                  <h3 className="text-lg font-semibold">Assistant Status</h3>
                </div>
              </div>
              {voiceFeatureEnabled ? (
                <div>
                  {isStatusLoading && <p className="text-sm text-muted-foreground">Running diagnostics...</p>}
                  {voiceStatus && (
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Assistant ID</span>
                        <Badge variant="secondary">{voiceStatus.assistant_id || "pending"}</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Groq Model</span>
                        <span className="font-medium">{voiceStatus.groq_model}</span>
                      </div>
                    </div>
                  )}
                  {isStatusError && !isStatusLoading && (
                    <p className="text-sm text-destructive">
                      {(voiceStatusError as any)?.response?.data?.detail || "Voice agent unavailable"}
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Enable the feature to run diagnostics.</p>
              )}
            </div>

            <div className="glass rounded-2xl p-5 space-y-3">
              <div className="flex items-center gap-3">
                <Waves className="h-8 w-8 text-accent" />
                <div>
                  <p className="text-sm text-muted-foreground">Browser Session</p>
                  <h3 className="text-lg font-semibold">WebRTC Test</h3>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                Use your microphone to speak with the assistant directly from this dashboard.
              </p>
              <div className="flex flex-wrap gap-3">
                <Button
                  onClick={handleStartWebCall}
                  disabled={!voiceFeatureEnabled || webCallState === "connecting" || webCallState === "live"}
                  className="gap-2"
                >
                  <PhoneCall className="h-4 w-4" />
                  {webCallState === "live" ? "Live" : webCallState === "connecting" ? "Connecting" : "Start"}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleStopWebCall}
                  disabled={webCallState === "idle"}
                  className="gap-2"
                >
                  <PhoneOff className="h-4 w-4" />
                  Stop
                </Button>
                <Button
                  variant="ghost"
                  onClick={handleToggleMute}
                  disabled={webCallState === "idle"}
                  className="gap-2"
                >
                  {muted ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  {muted ? "Unmute" : "Mute"}
                </Button>
              </div>
              {assistantId && (
                <p className="text-xs text-muted-foreground">Using assistant {assistantId}</p>
              )}
              {webCallError && <p className="text-xs text-destructive">{webCallError}</p>}
              <Link to="/voice-agent/test" className="text-xs font-medium text-primary hover:underline">
                Open advanced WebRTC test ↗
              </Link>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="glass rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold">Start Outbound Test Call</h3>
                  <p className="text-sm text-muted-foreground">Trigger a Vapi dial-out to any E.164 number.</p>
                </div>
                <Activity className="h-6 w-6 text-primary" />
              </div>
              <form
                className="space-y-4"
                onSubmit={(event) => {
                  event.preventDefault();
                  if (!canStartCall || startCallMutation.isPending) return;
                  startCallMutation.mutate();
                }}
              >
                <div>
                  <label className="text-sm font-medium">Client Phone Number</label>
                  <Input
                    required
                    placeholder="+15555551234"
                    value={customerNumber}
                    onChange={(event) => setCustomerNumber(event.target.value)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Client Name (optional)</label>
                  <Input
                    placeholder="Jordan Client"
                    value={customerName}
                    onChange={(event) => setCustomerName(event.target.value)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Notes / Metadata</label>
                  <Textarea
                    placeholder="Any context you want to send along with the call"
                    rows={3}
                    value={callNotes}
                    onChange={(event) => setCallNotes(event.target.value)}
                  />
                </div>
                <Button
                  type="submit"
                  disabled={!voiceFeatureEnabled || !canStartCall || startCallMutation.isPending}
                  className="gap-2"
                >
                  <PhoneCall className="h-4 w-4" />
                  {startCallMutation.isPending ? "Queuing..." : "Start Call"}
                </Button>
              </form>
            </div>

            <div className="glass rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold">Recent Calls</h3>
                  <p className="text-sm text-muted-foreground">Latest 25 voice sessions captured in Mongo.</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2"
                  onClick={() => queryClient.invalidateQueries({ queryKey: ["voice-agent", "history"] })}
                  disabled={!voiceFeatureEnabled || isHistoryLoading}
                >
                  <RefreshCcw className="h-4 w-4" />
                  Refresh
                </Button>
              </div>

              {!voiceFeatureEnabled && (
                <p className="text-sm text-muted-foreground">Enable the voice agent to view call history.</p>
              )}

              {voiceFeatureEnabled && isHistoryLoading && (
                <p className="text-sm text-muted-foreground">Loading latest calls...</p>
              )}

              {voiceFeatureEnabled && isHistoryError && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>Unable to fetch history</AlertTitle>
                  <AlertDescription>Try refreshing after ensuring the agent is enabled.</AlertDescription>
                </Alert>
              )}

              {voiceFeatureEnabled && !isHistoryLoading && callItems.length === 0 && (
                <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-muted-foreground/40 p-6 text-center text-sm text-muted-foreground">
                  <History className="h-6 w-6 mb-2" />
                  No calls logged yet.
                </div>
              )}

              {voiceFeatureEnabled && callItems.length > 0 && (
                <div className="space-y-3 max-h-[420px] overflow-y-auto pr-2">
                  {callItems.map((call) => (
                    <div key={call.id} className="rounded-xl border border-white/10 p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{call.customer?.name || "Unknown"}</p>
                          <p className="text-xs text-muted-foreground">{call.customer?.number || "N/A"}</p>
                        </div>
                        <Badge
                          variant={
                            call.status?.toLowerCase() === "completed"
                              ? "secondary"
                              : call.status?.toLowerCase() === "failed"
                              ? "destructive"
                              : "default"
                          }
                        >
                          {call.status || "pending"}
                        </Badge>
                      </div>
                      <div className="text-xs text-muted-foreground flex items-center gap-2">
                        <ShieldCheck className="h-3.5 w-3.5" />
                        {formatDate(call.created_at)}
                      </div>
                      {call.metadata?.notes && (
                        <p className="text-sm text-muted-foreground">Notes: {call.metadata.notes}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default VoiceAgentPage;
