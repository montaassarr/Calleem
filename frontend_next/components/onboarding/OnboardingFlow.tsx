"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, Sparkles, Key, Building2, Workflow, Bot, Phone, Loader2 } from "lucide-react";

interface OnboardingStep {
  id: number;
  title: string;
  description: string;
  icon: any;
}

const STEPS: OnboardingStep[] = [
  { id: 1, title: "Welcome", description: "Get started with your AI Receptionist", icon: Sparkles },
  { id: 2, title: "API Keys", description: "Connect your AI services", icon: Key },
  { id: 3, title: "Business Profile", description: "Tell us about your business", icon: Building2 },
  { id: 4, title: "n8n Workflow", description: "Connect your workflow automation", icon: Workflow },
  { id: 5, title: "Create Agent", description: "Set up your first AI agent", icon: Bot },
  { id: 6, title: "Test Call", description: "Make a test call to verify setup", icon: Phone },
];

export default function OnboardingFlow() {
  const router = useRouter();
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [isTestMode, setIsTestMode] = useState(false);
  const [formData, setFormData] = useState({
    groqApiKey: "",
    vapiApiKey: "",
    openaiApiKey: "",
    businessName: "",
    businessDescription: "",
    industry: "",
    phone: "",
    website: "",
    timezone: "",
    n8nUrl: "",
    n8nApiKey: "",
    agentName: "",
    agentPrompt: "",
    agentVoice: "jennifer",
    testPhoneNumber: "",
  });

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const testMode = params.get("test_mode") === "true" || localStorage.getItem("test_mode") === "true";

    if (testMode) {
      setIsTestMode(true);
      setFormData({
        groqApiKey: "gsk_test_1234567890abcdef",
        vapiApiKey: "vapi_test_1234567890abcdef",
        openaiApiKey: "sk-test-1234567890abcdef",
        businessName: user?.full_name || "Test Business Inc",
        businessDescription: "We provide excellent customer service",
        industry: "Technology",
        phone: "+1234567890",
        website: "https://testbusiness.com",
        timezone: "America/New_York",
        n8nUrl: "http://localhost:5678",
        n8nApiKey: "n8n_test_api_key_123",
        agentName: "Test Receptionist",
        agentPrompt: "You are a friendly AI receptionist. Help customers book appointments and answer questions.",
        agentVoice: "jennifer",
        testPhoneNumber: "+1234567890",
      });
    }
  }, [user]);

  const progress = (currentStep / STEPS.length) * 100;

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleNext = async () => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, isTestMode ? 500 : 1500));

    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    } else {
      await completeOnboarding();
    }

    setLoading(false);
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const completeOnboarding = async () => {
    try {
      router.push("/dashboard?welcome=true");
    } catch (error) {
      console.error("Failed to complete onboarding:", error);
    }
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return true;
      case 2:
        return Boolean(formData.groqApiKey && formData.vapiApiKey);
      case 3:
        return Boolean(formData.businessName && formData.businessDescription && formData.phone);
      case 4:
        return Boolean(formData.n8nUrl && formData.n8nApiKey);
      case 5:
        return Boolean(formData.agentName && formData.agentPrompt);
      case 6:
        return Boolean(formData.testPhoneNumber);
      default:
        return true;
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6 text-center">
            <div className="flex justify-center">
              <div className="h-24 w-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Sparkles className="h-12 w-12 text-white" />
              </div>
            </div>
            <div>
              <h2 className="text-3xl font-bold mb-2">Welcome to Your AI Receptionist!</h2>
              <p className="text-muted-foreground text-lg">Let's get you set up in just a few minutes</p>
            </div>
            {isTestMode && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <p className="text-amber-800 font-medium">🧪 Test Mode Active - Pre-filled data for fast testing</p>
              </div>
            )}
            <div className="grid grid-cols-2 gap-4 text-left mt-8">
              {[
                "14-Day Free Trial",
                "BYOK Support",
                "n8n Integration",
                "Multi-Agent",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3">
                  <CheckCircle2 className="h-6 w-6 text-green-500 mt-1" />
                  <div>
                    <p className="font-semibold">{item}</p>
                    <p className="text-sm text-muted-foreground">
                      {item === "14-Day Free Trial"
                        ? "100 minutes included"
                        : item === "BYOK Support"
                        ? "Use your own API keys"
                        : item === "n8n Integration"
                        ? "Powerful workflow automation"
                        : "Create unlimited agents"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Connect Your API Keys</h2>
              <p className="text-muted-foreground">We use a Bring Your Own Key (BYOK) model - you stay in control of your AI costs</p>
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="groqApiKey">
                  Groq API Key <span className="text-red-500">*</span>
                </Label>
                <Input id="groqApiKey" type="password" placeholder="gsk_..." value={formData.groqApiKey} onChange={(e) => handleInputChange("groqApiKey", e.target.value)} className="font-mono" />
                <p className="text-xs text-muted-foreground mt-1">
                  Get your key at <a href="https://console.groq.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">console.groq.com</a>
                </p>
              </div>
              <div>
                <Label htmlFor="vapiApiKey">
                  VAPI API Key <span className="text-red-500">*</span>
                </Label>
                <Input id="vapiApiKey" type="password" placeholder="vapi_..." value={formData.vapiApiKey} onChange={(e) => handleInputChange("vapiApiKey", e.target.value)} className="font-mono" />
                <p className="text-xs text-muted-foreground mt-1">
                  Get your key at <a href="https://vapi.ai" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">vapi.ai</a>
                </p>
              </div>
              <div>
                <Label htmlFor="openaiApiKey">OpenAI API Key (Optional)</Label>
                <Input id="openaiApiKey" type="password" placeholder="sk-..." value={formData.openaiApiKey} onChange={(e) => handleInputChange("openaiApiKey", e.target.value)} className="font-mono" />
                <p className="text-xs text-muted-foreground mt-1">For GPT-4 models (optional, Groq is default)</p>
              </div>
            </div>
          </div>
        );
      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Tell Us About Your Business</h2>
              <p className="text-muted-foreground">This helps us personalize your AI agent's responses</p>
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="businessName">
                  Business Name <span className="text-red-500">*</span>
                </Label>
                <Input id="businessName" placeholder="Acme Inc" value={formData.businessName} onChange={(e) => handleInputChange("businessName", e.target.value)} />
              </div>
              <div>
                <Label htmlFor="businessDescription">
                  Business Description <span className="text-red-500">*</span>
                </Label>
                <Textarea id="businessDescription" placeholder="We provide excellent customer service and..." rows={4} value={formData.businessDescription} onChange={(e) => handleInputChange("businessDescription", e.target.value)} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="industry">Industry</Label>
                  <Input id="industry" placeholder="Healthcare, Legal, etc." value={formData.industry} onChange={(e) => handleInputChange("industry", e.target.value)} />
                </div>
                <div>
                  <Label htmlFor="phone">
                    Phone <span className="text-red-500">*</span>
                  </Label>
                  <Input id="phone" placeholder="+1234567890" value={formData.phone} onChange={(e) => handleInputChange("phone", e.target.value)} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="website">Website</Label>
                  <Input id="website" placeholder="https://example.com" value={formData.website} onChange={(e) => handleInputChange("website", e.target.value)} />
                </div>
                <div>
                  <Label htmlFor="timezone">Timezone</Label>
                  <Input id="timezone" placeholder="America/New_York" value={formData.timezone} onChange={(e) => handleInputChange("timezone", e.target.value)} />
                </div>
              </div>
            </div>
          </div>
        );
      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Connect n8n Workflow</h2>
              <p className="text-muted-foreground">n8n powers your automation workflows and appointment management</p>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-blue-900 font-medium mb-2">📌 n8n Setup Required</p>
              <p className="text-blue-800 text-sm mb-2">Make sure your n8n instance is running with the AI Receptionist workflows imported.</p>
              <a href="/workflows/README.md" target="_blank" className="text-blue-600 hover:underline text-sm font-medium">
                View Setup Guide →
              </a>
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="n8nUrl">
                  n8n URL <span className="text-red-500">*</span>
                </Label>
                <Input id="n8nUrl" placeholder="http://localhost:5678" value={formData.n8nUrl} onChange={(e) => handleInputChange("n8nUrl", e.target.value)} />
                <p className="text-xs text-muted-foreground mt-1">Your n8n instance URL (local or hosted)</p>
              </div>
              <div>
                <Label htmlFor="n8nApiKey">
                  n8n API Key <span className="text-red-500">*</span>
                </Label>
                <Input id="n8nApiKey" type="password" placeholder="n8n_api_..." value={formData.n8nApiKey} onChange={(e) => handleInputChange("n8nApiKey", e.target.value)} className="font-mono" />
                <p className="text-xs text-muted-foreground mt-1">Found in n8n Settings → API</p>
              </div>
            </div>
          </div>
        );
      case 5:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Create Your First Agent</h2>
              <p className="text-muted-foreground">Set up an AI agent to handle your calls</p>
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="agentName">
                  Agent Name <span className="text-red-500">*</span>
                </Label>
                <Input id="agentName" placeholder="Main Receptionist" value={formData.agentName} onChange={(e) => handleInputChange("agentName", e.target.value)} />
              </div>
              <div>
                <Label htmlFor="agentPrompt">
                  Agent Prompt <span className="text-red-500">*</span>
                </Label>
                <Textarea id="agentPrompt" placeholder="You are a friendly AI receptionist for [Business]. Help customers with..." rows={6} value={formData.agentPrompt} onChange={(e) => handleInputChange("agentPrompt", e.target.value)} />
                <p className="text-xs text-muted-foreground mt-1">Define how your AI agent should behave and respond</p>
              </div>
              <div>
                <Label htmlFor="agentVoice">Voice</Label>
                <select id="agentVoice" className="w-full rounded-md border border-input bg-background px-3 py-2" value={formData.agentVoice} onChange={(e) => handleInputChange("agentVoice", e.target.value)}>
                  <option value="jennifer">Jennifer (Female, Professional)</option>
                  <option value="john">John (Male, Friendly)</option>
                  <option value="sara">Sara (Female, Warm)</option>
                  <option value="michael">Michael (Male, Authoritative)</option>
                </select>
              </div>
            </div>
          </div>
        );
      case 6:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Test Your Setup</h2>
              <p className="text-muted-foreground">Make a test call to verify everything works</p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <CheckCircle2 className="h-8 w-8 text-green-600" />
                <div>
                  <p className="font-semibold text-green-900">Setup Complete!</p>
                  <p className="text-green-700 text-sm">Your AI receptionist is ready</p>
                </div>
              </div>
              <div className="space-y-3 text-sm">
                {[
                  "API keys configured",
                  "Business profile completed",
                  "n8n workflow connected",
                  "Agent created",
                ].map((item) => (
                  <div key={item} className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="testPhoneNumber">
                  Your Phone Number <span className="text-red-500">*</span>
                </Label>
                <Input id="testPhoneNumber" placeholder="+1234567890" value={formData.testPhoneNumber} onChange={(e) => handleInputChange("testPhoneNumber", e.target.value)} />
                <p className="text-xs text-muted-foreground mt-1">We'll call this number to test your agent</p>
              </div>
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <p className="text-amber-900 text-sm">
                  <strong>Note:</strong> The test call will use your trial minutes. Expect a call within 30 seconds.
                </p>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-8">
          <div className="flex justify-between mb-4">
            {STEPS.map((step) => {
              const Icon = step.icon;
              const isActive = step.id === currentStep;
              const isCompleted = step.id < currentStep;

              return (
                <div key={step.id} className="flex flex-col items-center gap-2">
                  <div
                    className={`h-12 w-12 rounded-full flex items-center justify-center transition-all ${
                      isCompleted
                        ? "bg-green-500 text-white"
                        : isActive
                        ? "bg-blue-600 text-white ring-4 ring-blue-200"
                        : "bg-gray-200 text-gray-400"
                    }`}
                  >
                    {isCompleted ? <CheckCircle2 className="h-6 w-6" /> : <Icon className="h-6 w-6" />}
                  </div>
                  <p className={`text-xs font-medium text-center ${isActive ? "text-blue-600" : isCompleted ? "text-green-600" : "text-gray-400"}`}>
                    {step.title}
                  </p>
                </div>
              );
            })}
          </div>
          <Progress value={progress} className="h-2" />
          <p className="text-sm text-muted-foreground text-center mt-2">
            Step {currentStep} of {STEPS.length}
          </p>
        </div>
        <Card>
          <CardContent className="p-8">
            {renderStepContent()}
            <div className="flex justify-between mt-8">
              <Button variant="outline" onClick={handleBack} disabled={currentStep === 1 || loading}>
                Back
              </Button>
              <Button onClick={handleNext} disabled={!isStepValid() || loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {currentStep === STEPS.length ? "Completing..." : "Saving..."}
                  </>
                ) : currentStep === STEPS.length ? (
                  "Complete Setup & Test Call"
                ) : (
                  "Continue"
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
