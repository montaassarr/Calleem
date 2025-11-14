import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Save, ArrowLeft, Sparkles } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";

const AISettings = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [settings, setSettings] = useState({
    model: "mixtral-8x7b-32768",
    temperature: 0.7,
    max_tokens: 500,
    greeting_message: "Hello! I'm your AI receptionist for Royal Fade Barbershop. How can I help you today?",
    system_prompt: "You are a helpful and professional receptionist for a barbershop. Be friendly, efficient, and help customers book appointments.",
    tone: "friendly",
  });

  const handleSave = () => {
    // TODO: Save to backend
    toast({
      title: "AI Settings Saved",
      description: "AI configuration has been updated successfully",
    });
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center gap-4 mb-6">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/settings')}
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold mb-2">AI Configuration</h1>
              <p className="text-muted-foreground">
                Configure AI behavior, prompts, and model settings
              </p>
            </div>
          </div>

          {/* Form */}
          <div className="glass rounded-2xl p-6 max-w-3xl">
            <div className="space-y-6">
              <div>
                <Label htmlFor="model">AI Model</Label>
                <Select value={settings.model} onValueChange={(value) => setSettings({ ...settings, model: value })}>
                  <SelectTrigger className="glass-strong mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mixtral-8x7b-32768">Groq Mixtral 8x7B (Recommended)</SelectItem>
                    <SelectItem value="llama2-70b-4096">Groq LLaMA2 70B</SelectItem>
                    <SelectItem value="gemma-7b-it">Groq Gemma 7B</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground mt-1">
                  Choose the AI model for conversation handling
                </p>
              </div>

              <div>
                <Label htmlFor="tone">Conversation Tone</Label>
                <Select value={settings.tone} onValueChange={(value) => setSettings({ ...settings, tone: value })}>
                  <SelectTrigger className="glass-strong mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="professional">Professional</SelectItem>
                    <SelectItem value="friendly">Friendly</SelectItem>
                    <SelectItem value="casual">Casual</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label htmlFor="temperature">Temperature (Creativity)</Label>
                  <span className="text-sm text-muted-foreground">{settings.temperature.toFixed(1)}</span>
                </div>
                <Slider
                  value={[settings.temperature]}
                  onValueChange={([value]) => setSettings({ ...settings, temperature: value })}
                  min={0}
                  max={1}
                  step={0.1}
                  className="mt-2"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Higher values make responses more creative, lower values more focused
                </p>
              </div>

              <div>
                <Label htmlFor="max_tokens">Max Response Length</Label>
                <Input
                  id="max_tokens"
                  type="number"
                  value={settings.max_tokens}
                  onChange={(e) => setSettings({ ...settings, max_tokens: parseInt(e.target.value) })}
                  className="glass-strong mt-2"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Maximum number of tokens in AI responses (default: 500)
                </p>
              </div>

              <div>
                <Label htmlFor="greeting_message">Greeting Message</Label>
                <Textarea
                  id="greeting_message"
                  value={settings.greeting_message}
                  onChange={(e) => setSettings({ ...settings, greeting_message: e.target.value })}
                  className="glass-strong mt-2"
                  rows={3}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  First message customers receive when starting a conversation
                </p>
              </div>

              <div>
                <Label htmlFor="system_prompt">System Prompt</Label>
                <Textarea
                  id="system_prompt"
                  value={settings.system_prompt}
                  onChange={(e) => setSettings({ ...settings, system_prompt: e.target.value })}
                  className="glass-strong mt-2"
                  rows={5}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Instructions that define the AI's behavior and personality
                </p>
              </div>

              <div className="flex gap-3 pt-4">
                <Button 
                  className="gap-2 bg-gradient-to-r from-primary to-accent"
                  onClick={handleSave}
                >
                  <Save className="w-4 h-4" />
                  Save Configuration
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => navigate('/settings')}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>

          {/* Preview */}
          <div className="glass rounded-2xl p-6 max-w-3xl mt-6">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-primary" />
              <h3 className="text-lg font-semibold">Preview</h3>
            </div>
            <div className="glass-strong rounded-lg p-4">
              <p className="text-sm">{settings.greeting_message}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AISettings;
