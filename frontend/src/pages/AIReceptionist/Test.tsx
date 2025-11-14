import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

const AIReceptionistTest = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'ai',
      text: 'Hello! I\'m your AI receptionist for Royal Fade Barbershop. How can I help you today?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [testPhone, setTestPhone] = useState('+1234567890');
  const { toast } = useToast();

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      text: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Note: Since there's no direct chat endpoint, we simulate the webhook flow
      // In production, you might want to add a test endpoint to the backend
      // For now, we'll show a simulated response
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        text: `[TEST MODE] I received your message: "${input}". In production, this would be processed by the AI and trigger appropriate actions like booking appointments. To test the full flow, send an SMS to your Twilio number.`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
      
      toast({
        title: "Test Message Sent",
        description: "Check conversations page for real AI interactions via SMS",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send test message",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold mb-2">AI Receptionist Test</h1>
            <p className="text-muted-foreground">Test your AI chatbot and see how it responds to customer queries</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chat Window */}
            <div className="lg:col-span-2 glass rounded-2xl flex flex-col h-[calc(100vh-250px)]">
              {/* Chat Header */}
              <div className="p-4 border-b border-white/10">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Royal Fade AI</h3>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                      <span className="text-xs text-muted-foreground">Online</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.role === 'ai' && (
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    )}
                    <div className={`max-w-[70%] ${message.role === 'user' ? 'order-1' : ''}`}>
                      <div
                        className={`rounded-2xl p-4 ${
                          message.role === 'user'
                            ? 'bg-gradient-to-r from-primary to-accent text-white'
                            : 'glass-strong'
                        }`}
                      >
                        <p className="text-sm">{message.text}</p>
                      </div>
                      <span className="text-xs text-muted-foreground mt-1 block px-2">
                        {formatTime(message.timestamp)}
                      </span>
                    </div>
                    {message.role === 'user' && (
                      <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0">
                        <User className="w-4 h-4" />
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="glass-strong rounded-2xl p-4">
                      <Loader2 className="w-4 h-4 animate-spin" />
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="p-4 border-t border-white/10">
                <div className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type your message..."
                    className="glass-strong"
                    disabled={isLoading}
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={isLoading || !input.trim()}
                    className="gap-2 bg-gradient-to-r from-primary to-accent"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
            </div>

            {/* Settings Panel */}
            <div className="space-y-6">
              {/* Test Info */}
              <div className="glass rounded-2xl p-6">
                <h3 className="font-semibold mb-4">Test Information</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-muted-foreground">Test Phone Number</label>
                    <Input
                      value={testPhone}
                      onChange={(e) => setTestPhone(e.target.value)}
                      className="glass-strong mt-1"
                      placeholder="+1234567890"
                    />
                  </div>
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <p className="text-xs text-yellow-800 dark:text-yellow-200">
                      <strong>Note:</strong> This is a simulation. Real AI conversations happen via SMS through Twilio.
                    </p>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="glass rounded-2xl p-6">
                <h3 className="font-semibold mb-4">Quick Test Messages</h3>
                <div className="space-y-2">
                  <Button
                    variant="outline"
                    className="w-full justify-start text-sm"
                    onClick={() => setInput("I want to book a haircut")}
                  >
                    Book appointment
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-sm"
                    onClick={() => setInput("What services do you offer?")}
                  >
                    Ask about services
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-sm"
                    onClick={() => setInput("What are your hours?")}
                  >
                    Business hours
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-sm"
                    onClick={() => setInput("Cancel my appointment")}
                  >
                    Cancel booking
                  </Button>
                </div>
              </div>

              {/* AI Status */}
              <div className="glass rounded-2xl p-6">
                <h3 className="font-semibold mb-4">AI Status</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Model</span>
                    <span className="text-sm font-medium">Groq Mixtral</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Status</span>
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                      Active
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Response Time</span>
                    <span className="text-sm font-medium">~1.5s</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AIReceptionistTest;
