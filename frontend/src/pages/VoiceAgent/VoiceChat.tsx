import { useState, useEffect, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { Mic, MicOff, Volume2, VolumeX, Phone, PhoneOff, Loader2 } from "lucide-react";

import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import axios from "axios";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const VoiceChat = () => {
  const { toast } = useToast();
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isCallActive, setIsCallActive] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [interimTranscript, setInterimTranscript] = useState("");
  
  const recognitionRef = useRef<any>(null);
  const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null);
  const conversationIdRef = useRef<string | null>(null);

  // Initialize speech recognition
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast({
        variant: "destructive",
        title: "Speech Recognition Not Supported",
        description: "Your browser doesn't support speech recognition. Please use Chrome or Edge.",
      });
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      setInterimTranscript(interim);

      if (final) {
        handleUserSpeech(final);
        setInterimTranscript("");
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      if (event.error !== 'no-speech') {
        toast({
          variant: "destructive",
          title: "Recognition Error",
          description: `Speech recognition error: ${event.error}`,
        });
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      if (isCallActive) {
        // Restart recognition if call is still active
        setTimeout(() => {
          try {
            recognition.start();
          } catch (e) {
            console.log('Recognition already started');
          }
        }, 100);
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isCallActive, toast]);

  // Send message to AI
  const sendMessageMutation = useMutation({
    mutationFn: async (userMessage: string) => {
      const response = await axios.post('http://localhost:8001/webhook/whatsapp', {
        message: userMessage,
        from: "voice_user",
        conversation_id: conversationIdRef.current,
      });
      return response.data;
    },
    onSuccess: (data) => {
      const aiResponse = data.response || data.message || "I didn't understand that.";
      
      // Add AI message to chat
      setMessages(prev => [...prev, {
        role: "assistant",
        content: aiResponse,
        timestamp: new Date(),
      }]);

      // Speak the response
      speakText(aiResponse);

      // Store conversation ID
      if (data.conversation_id) {
        conversationIdRef.current = data.conversation_id;
      }
    },
    onError: (error: any) => {
      console.error('Error sending message:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to communicate with AI agent",
      });
    },
  });

  const handleUserSpeech = (transcript: string) => {
    // Add user message to chat
    setMessages(prev => [...prev, {
      role: "user",
      content: transcript,
      timestamp: new Date(),
    }]);

    // Send to AI
    sendMessageMutation.mutate(transcript);
  };

  const speakText = (text: string) => {
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    // Get a female voice if available
    const voices = window.speechSynthesis.getVoices();
    const femaleVoice = voices.find(voice => 
      voice.name.includes('Female') || 
      voice.name.includes('Samantha') ||
      voice.name.includes('Victoria') ||
      voice.name.includes('Zira')
    );
    if (femaleVoice) {
      utterance.voice = femaleVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    synthesisRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const startCall = () => {
    setIsCallActive(true);
    setMessages([]);
    conversationIdRef.current = null;

    // Start listening
    try {
      recognitionRef.current?.start();
    } catch (e) {
      console.log('Recognition already started');
    }

    // Greet the user
    const greeting = "Hello! Welcome to the salon. How can I help you today?";
    setMessages([{
      role: "assistant",
      content: greeting,
      timestamp: new Date(),
    }]);
    speakText(greeting);

    toast({
      title: "Call Started",
      description: "Start speaking to book an appointment!",
    });
  };

  const endCall = () => {
    setIsCallActive(false);
    
    // Stop listening
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    // Stop speaking
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsListening(false);
    setInterimTranscript("");

    toast({
      title: "Call Ended",
      description: "Voice session has been terminated.",
    });
  };

  const toggleMute = () => {
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
    } else if (isCallActive && recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.log('Recognition already started');
      }
    }
  };

  const toggleSpeaker = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold mb-2">Voice Chat</h1>
            <p className="text-muted-foreground">
              Talk to the AI receptionist using your microphone
            </p>
          </div>

          {!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window) && (
            <Alert variant="destructive" className="mb-6">
              <AlertTitle>Browser Not Supported</AlertTitle>
              <AlertDescription>
                Speech recognition is not supported in your browser. Please use Google Chrome or Microsoft Edge.
              </AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Call Controls */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="w-5 h-5" />
                  Call Controls
                </CardTitle>
                <CardDescription>
                  Start a voice conversation
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Status</span>
                  <Badge variant={isCallActive ? "default" : "outline"}>
                    {isCallActive ? "Active" : "Idle"}
                  </Badge>
                </div>

                {isCallActive && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Microphone</span>
                      <Badge variant={isListening ? "default" : "secondary"}>
                        {isListening ? "Listening" : "Muted"}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm">Speaker</span>
                      <Badge variant={isSpeaking ? "default" : "secondary"}>
                        {isSpeaking ? "Speaking" : "Silent"}
                      </Badge>
                    </div>
                  </>
                )}

                {!isCallActive ? (
                  <Button onClick={startCall} className="w-full gap-2">
                    <Phone className="w-4 h-4" />
                    Start Call
                  </Button>
                ) : (
                  <>
                    <div className="flex gap-2">
                      <Button 
                        onClick={toggleMute} 
                        variant="outline" 
                        className="flex-1 gap-2"
                      >
                        {isListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
                        {isListening ? "Mute" : "Unmute"}
                      </Button>
                      <Button 
                        onClick={toggleSpeaker} 
                        variant="outline" 
                        className="flex-1 gap-2"
                      >
                        {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                        Speaker
                      </Button>
                    </div>
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

                {interimTranscript && (
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-xs text-muted-foreground mb-1">Listening...</p>
                    <p className="text-sm italic">{interimTranscript}</p>
                  </div>
                )}

                {sendMessageMutation.isPending && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    AI is thinking...
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Conversation */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Conversation</CardTitle>
                <CardDescription>
                  Real-time transcript of your voice chat
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-[500px] overflow-y-auto">
                  {messages.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <p>No messages yet. Start a call to begin!</p>
                    </div>
                  ) : (
                    messages.map((message, index) => (
                      <div
                        key={index}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg p-3 ${
                            message.role === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-muted'
                          }`}
                        >
                          <p className="text-sm">{message.content}</p>
                          <p className="text-xs opacity-70 mt-1">
                            {message.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Instructions */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>How to Use</CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="space-y-2 text-sm">
                <li className="flex gap-2">
                  <span className="font-bold">1.</span>
                  <span>Click "Start Call" to begin your voice session</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold">2.</span>
                  <span>Allow microphone access when prompted by your browser</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold">3.</span>
                  <span>Wait for the AI to greet you, then start speaking</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold">4.</span>
                  <span>Say things like: "I want to book a haircut", "What services do you offer?", "Show me available times for tomorrow"</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold">5.</span>
                  <span>The AI will respond with voice and you'll see the transcript on screen</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold">6.</span>
                  <span>Click "End Call" when you're done</span>
                </li>
              </ol>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default VoiceChat;
