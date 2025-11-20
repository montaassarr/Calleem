import { useEffect, useState, useRef } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import Vapi from "@vapi-ai/web";
import { Phone, PhoneOff, Mic, MicOff, Loader2, Settings2, CheckCircle2, AlertCircle } from "lucide-react";

import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { voiceApi } from "@/api";

interface Message {
  time: string;
  type: "user" | "assistant" | "system";
  content: string;
}

const VoiceChat = () => {
  const { toast } = useToast();
  const [vapi, setVapi] = useState<Vapi | null>(null);
  const [connected, setConnected] = useState(false);
  const [assistantIsSpeaking, setAssistantIsSpeaking] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const conversationIdRef = useRef<string | null>(null);

  // Fetch Vapi configuration from backend
  const { data: vapiConfig, isLoading: configLoading } = useQuery({
    queryKey: ["vapi-config"],
    queryFn: () => voiceApi.getVapiConfig(),
  });

  // Initialize Vapi client
  useEffect(() => {
    if (!vapiConfig?.publicKey) return;

    const vapiClient = new Vapi(vapiConfig.publicKey);
    
    // Event listeners
    vapiClient.on("call-start", () => {
      console.log("Call started");
      setConnected(true);
      addMessage("system", "Call connected");
    });

    vapiClient.on("call-end", () => {
      console.log("Call ended");
      setConnected(false);
      setAssistantIsSpeaking(false);
      setVolumeLevel(0);
      addMessage("system", "Call ended");
    });

    vapiClient.on("speech-start", () => {
      console.log("Assistant started speaking");
      setAssistantIsSpeaking(true);
    });

    vapiClient.on("speech-end", () => {
      console.log("Assistant stopped speaking");
      setAssistantIsSpeaking(false);
    });

    vapiClient.on("volume-level", (volume: number) => {
      setVolumeLevel(volume);
    });

    vapiClient.on("message", (message: any) => {
      console.log("Received message:", message);
      
      if (message.type === "transcript") {
        if (message.transcriptType === "final") {
          if (message.role === "user") {
            addMessage("user", message.transcript);
          } else if (message.role === "assistant") {
            addMessage("assistant", message.transcript);
          }
        }
      } else if (message.type === "function-call") {
        addMessage("system", `Function called: ${message.functionCall.name}`);
      } else if (message.type === "hang") {
        addMessage("system", "Call ended by assistant");
      }
    });

    vapiClient.on("error", (error: any) => {
      console.error("Vapi error:", error);
      addMessage("system", `Error: ${error.message || error}`);
      toast({
        variant: "destructive",
        title: "Vapi Error",
        description: error.message || "An error occurred",
      });
    });

    setVapi(vapiClient);

    return () => {
      vapiClient.stop();
    };
  }, [vapiConfig, toast]);

  const addMessage = (type: "user" | "assistant" | "system", content: string) => {
    setMessages(prev => [...prev, {
      time: new Date().toLocaleTimeString(),
      type,
      content,
    }]);
  };

  // Start call mutation
  const startCallMutation = useMutation({
    mutationFn: async () => {
      if (!vapi || !vapiConfig?.assistantId) {
        throw new Error("Vapi not initialized or no assistant configured");
      }

      addMessage("system", "Starting call...");
      
      // Start the call using the assistant ID from backend
      await vapi.start(vapiConfig.assistantId);
      
      return true;
    },
    onError: (error: any) => {
      console.error("Error starting call:", error);
      toast({
        variant: "destructive",
        title: "Failed to start call",
        description: error.message || "Could not connect to voice assistant",
      });
      addMessage("system", `Failed to start: ${error.message}`);
    },
  });

  const startCall = () => {
    startCallMutation.mutate();
  };

  const endCall = () => {
    if (vapi) {
      vapi.stop();
    }
  };

  const toggleMute = () => {
    if (vapi) {
      const newMutedState = !isMuted;
      vapi.setMuted(newMutedState);
      setIsMuted(newMutedState);
      addMessage("system", newMutedState ? "Microphone muted" : "Microphone unmuted");
    }
  };

  if (configLoading) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 ml-64">
          <DashboardHeader />
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>
        </main>
      </div>
    );
  }

  if (!vapiConfig) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <main className="flex-1 ml-64">
          <DashboardHeader />
          <div className="p-6">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Configuration Required</AlertTitle>
              <AlertDescription>
                Please configure your Vapi settings in Voice Agent → Settings first.
              </AlertDescription>
            </Alert>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold mb-2">Voice Chat</h1>
            <p className="text-muted-foreground">
              Talk to your AI receptionist using professional voice technology
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Call Controls */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="w-5 h-5" />
                  Call Controls
                </CardTitle>
                <CardDescription>
                  Powered by Vapi AI
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Status</span>
                  <Badge variant={connected ? "default" : "outline"}>
                    {connected ? "Connected" : "Idle"}
                  </Badge>
                </div>

                {connected && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Assistant</span>
                      <Badge variant={assistantIsSpeaking ? "default" : "secondary"}>
                        {assistantIsSpeaking ? "Speaking" : "Listening"}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm">Volume</span>
                      <span className="text-sm font-mono">{Math.round(volumeLevel * 100)}%</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm">Microphone</span>
                      <Badge variant={isMuted ? "destructive" : "default"}>
                        {isMuted ? "Muted" : "Active"}
                      </Badge>
                    </div>
                  </>
                )}

                {!connected ? (
                  <Button 
                    onClick={startCall} 
                    disabled={startCallMutation.isPending}
                    className="w-full gap-2"
                  >
                    {startCallMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        <Phone className="w-4 h-4" />
                        Start Call
                      </>
                    )}
                  </Button>
                ) : (
                  <>
                    <Button 
                      onClick={toggleMute} 
                      variant="outline" 
                      className="w-full gap-2"
                    >
                      {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                      {isMuted ? "Unmute" : "Mute"}
                    </Button>
                    <Button 
                      onClick={endCall} 
                      variant="destructive" 
                      className="w-full gap-2"
                    >
                      <PhoneOff className="w-4 h-4" />
                      End Call
                    </Button>
                  </>
                )}

                <div className="pt-4 border-t">
                  <div className="flex items-start gap-2 text-xs text-muted-foreground">
                    <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium">Professional Voice AI</p>
                      <p>Crystal-clear audio, natural conversation, real-time responses</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Conversation */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Live Conversation</CardTitle>
                <CardDescription>
                  Real-time transcript of your voice chat
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-[500px] overflow-y-auto">
                  {messages.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      <Phone className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p className="font-medium">No conversation yet</p>
                      <p className="text-sm">Click "Start Call" to begin talking!</p>
                    </div>
                  ) : (
                    messages.map((message, index) => (
                      <div
                        key={index}
                        className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg p-3 ${
                            message.type === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : message.type === 'assistant'
                              ? 'bg-muted'
                              : 'bg-accent/50'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-semibold opacity-70">
                              {message.type === 'user' ? 'You' : 
                               message.type === 'assistant' ? 'AI Assistant' : 'System'}
                            </span>
                            <span className="text-xs opacity-50">{message.time}</span>
                          </div>
                          <p className="text-sm">{message.content}</p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Features */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings2 className="w-5 h-5" />
                Features
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Natural Conversation</p>
                    <p className="text-sm text-muted-foreground">Speak naturally - the AI understands context</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Appointment Booking</p>
                    <p className="text-sm text-muted-foreground">Book appointments by voice automatically</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Real-time Transcription</p>
                    <p className="text-sm text-muted-foreground">See everything said in real-time</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default VoiceChat;
