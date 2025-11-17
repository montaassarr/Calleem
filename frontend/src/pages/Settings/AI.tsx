import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Save, ArrowLeft, RefreshCw, AlertCircle } from "lucide-react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useConfig } from "@/hooks/use-config";
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
  const { config, isLoading, error, updateConfig, isUpdating, reloadConfig, isReloading } = useConfig();
  
  const [formData, setFormData] = useState({
    model: "llama-3.1-70b-versatile",
    temperature: 0.7,
    max_tokens: 500,
    system_prompt: "",
  });

  useEffect(() => {
    if (config?.ai_config) {
      setFormData({
        model: config.ai_config.model || "llama-3.1-70b-versatile",
        temperature: config.ai_config.temperature || 0.7,
        max_tokens: config.ai_config.max_tokens || 500,
        system_prompt: config.ai_config.system_prompt || "",
      });
    }
  }, [config]);

  const handleSave = () => {
    updateConfig({
      ai_config: formData
    });
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
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
            <Button
              variant="outline"
              size="sm"
              onClick={() => reloadConfig()}
              disabled={isReloading}
              className="gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${isReloading ? 'animate-spin' : ''}`} />
              Reload
            </Button>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Failed to load AI configuration. Please try again.
              </AlertDescription>
            </Alert>
          )}

          {/* Form */}
          <div className="glass rounded-2xl p-6 max-w-3xl">
            {isLoading ? (
              <div className="space-y-6">
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-40 w-full" />
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <Label htmlFor="model">AI Model *</Label>
                  <Select value={formData.model} onValueChange={(value) => setFormData({ ...formData, model: value })}>
                    <SelectTrigger className="glass-strong mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="llama-3.1-70b-versatile">Groq LLaMA 3.1 70B (Recommended)</SelectItem>
                      <SelectItem value="llama-3.3-70b-versatile">Groq LLaMA 3.3 70B</SelectItem>
                      <SelectItem value="mixtral-8x7b-32768">Groq Mixtral 8x7B</SelectItem>
                      <SelectItem value="gemma2-9b-it">Groq Gemma2 9B</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground mt-1">
                    Choose the AI model for conversation handling
                  </p>
                </div>

                <div>
                  <Label htmlFor="temperature">Temperature</Label>
                  <div className="flex items-center gap-4 mt-2">
                    <Slider
                      id="temperature"
                      min={0}
                      max={1}
                      step={0.1}
                      value={[formData.temperature]}
                      onValueChange={(value) => setFormData({ ...formData, temperature: value[0] })}
                      className="flex-1"
                    />
                    <span className="text-sm font-semibold w-12 text-center">
                      {formData.temperature.toFixed(1)}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Higher values make output more random (creative), lower values more focused
                  </p>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label htmlFor="system_prompt">System Prompt</Label>
                    <div className="text-xs text-muted-foreground">
                      {formData.system_prompt.length} characters
                    </div>
                  </div>
                  <Textarea
                    id="system_prompt"
                    value={formData.system_prompt}
                    onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                    className="glass-strong min-h-[300px] font-mono text-sm"
                    placeholder="You are Ava, a friendly AI receptionist for {business_name}..."
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Define the AI's personality and behavior. Use {'{business_name}'}, {'{services}'}, {'{business_hours}'} for dynamic values.
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button 
                    className="gap-2 bg-gradient-to-r from-primary to-accent"
                    onClick={handleSave}
                    disabled={isUpdating}
                  >
                    {isUpdating ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        Save Configuration
                      </>
                    )}
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => navigate('/settings')}
                    disabled={isUpdating}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default AISettings;
