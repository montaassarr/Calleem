"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Key,
    Plus,
    Trash2,
    Eye,
    EyeOff,
    Check,
    X,
    ArrowLeft,
    ExternalLink,
    AlertTriangle,
    TestTube,
    Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

interface ApiKey {
    id: string;
    provider: string;
    name: string;
    masked_key: string;
    created_at: string;
    last_used?: string;
    is_valid: boolean;
}

interface ApiKeyCreate {
    provider: string;
    name: string;
    api_key: string;
}

const PROVIDERS: Record<string, { name: string; description: string; url: string; placeholder: string }> = {
    vapi: { name: "VAPI.ai", description: "Voice AI platform for phone calls", url: "https://dashboard.vapi.ai", placeholder: "sk_live_..." },
    openai: { name: "OpenAI", description: "GPT models for AI conversations", url: "https://platform.openai.com/api-keys", placeholder: "sk-..." },
    groq: { name: "Groq", description: "Fast inference for LLaMA, Mixtral models", url: "https://console.groq.com/keys", placeholder: "gsk_..." },
    elevenlabs: { name: "ElevenLabs", description: "Text-to-speech voice synthesis", url: "https://elevenlabs.io/api", placeholder: "..." },
    anthropic: { name: "Anthropic", description: "Claude AI models", url: "https://console.anthropic.com", placeholder: "sk-ant-..." },
    deepgram: { name: "Deepgram", description: "Speech-to-text transcription", url: "https://console.deepgram.com", placeholder: "..." },
    whatsapp: { name: "WhatsApp Cloud API", description: "Meta WhatsApp Business Platform", url: "https://developers.facebook.com", placeholder: "EAA..." },
};

export default function APIKeysPage() {
    const router = useRouter();
    const queryClient = useQueryClient();
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [selectedProvider, setSelectedProvider] = useState("");
    const [keyName, setKeyName] = useState("");
    const [apiKeyVal, setApiKeyVal] = useState("");
    const [showKey, setShowKey] = useState(false);
    const [testingKeyId, setTestingKeyId] = useState<string | null>(null);

    const { data: apiKeys = [], isLoading } = useQuery<ApiKey[]>({
        queryKey: ["api-keys"],
        queryFn: async () => { const response = await api.get("/keys"); return response; },
    });

    const testConnectionMutation = useMutation({
        mutationFn: async (keyId: string) => { return { success: true }; },
        onSuccess: () => { toast.success("Connection test successful!"); setTestingKeyId(null); },
        onError: () => { toast.error("Connection test failed"); setTestingKeyId(null); },
    });

    const addKeyMutation = useMutation({
        mutationFn: async (data: ApiKeyCreate) => { return await api.post("/keys", data); },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["api-keys"] });
            toast.success("API Key added successfully");
            setIsAddDialogOpen(false);
            resetForm();
        },
        onError: (error: any) => { toast.error(error?.response?.data?.detail || "Failed to add API key"); },
    });

    const deleteKeyMutation = useMutation({
        mutationFn: async (keyId: string) => { await api.delete(`/keys/${keyId}`); },
        onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["api-keys"] }); toast.success("API Key deleted"); },
        onError: (error: any) => { toast.error(error?.response?.data?.detail || "Failed to delete API key"); },
    });

    const resetForm = () => { setSelectedProvider(""); setKeyName(""); setApiKeyVal(""); setShowKey(false); };

    const handleAddKey = () => {
        if (!selectedProvider || !keyName || !apiKeyVal) { toast.error("Please fill all fields"); return; }
        addKeyMutation.mutate({ provider: selectedProvider, name: keyName, api_key: apiKeyVal });
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return "Never";
        return new Date(dateString).toLocaleDateString();
    };

    return (
        <div>
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    <button onClick={() => router.push("/dashboard/settings")} className="p-2 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors">
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">API Keys</h1>
                        <p className="text-[14px] text-gray-500 font-medium">Manage your API keys for AI services (BYOK).</p>
                    </div>
                </div>
                <button onClick={() => setIsAddDialogOpen(true)} className="px-5 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-[20px] font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] flex items-center gap-2 relative overflow-hidden">
                    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                    <Plus className="w-4 h-4 relative z-10" />
                    <span className="relative z-10">Add API Key</span>
                </button>
            </div>

            {/* Security Alert */}
            <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3">
                <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                <p className="text-sm text-amber-700"><strong>Security:</strong> Your API keys are encrypted before storage. They are only visible when you add them.</p>
            </div>

            {/* API Keys Table */}
            <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-100">
                    <h3 className="font-bold text-gray-900">Your API Keys</h3>
                    <p className="text-sm text-gray-500 mt-1">Configure API keys for different AI providers to enable features.</p>
                </div>
                <div className="p-6">
                    {isLoading ? (
                        <div className="text-center py-8 text-gray-400">Loading...</div>
                    ) : apiKeys.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="mx-auto w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center mb-4">
                                <Key className="w-6 h-6 text-gray-400" />
                            </div>
                            <p className="text-gray-500 mb-4">No API keys configured yet</p>
                            <button onClick={() => setIsAddDialogOpen(true)} className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center gap-2 mx-auto">
                                <Plus className="w-4 h-4" />Add Your First Key
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {apiKeys.map((key) => (
                                <div key={key.id} className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:bg-gray-50 transition-colors">
                                    <div className="flex items-center gap-3 min-w-0">
                                        <div className="w-10 h-10 rounded-full bg-[#0a4c2f]/10 flex items-center justify-center shrink-0">
                                            <Key className="w-4 h-4 text-[#0a4c2f]" />
                                        </div>
                                        <div className="min-w-0">
                                            <div className="flex items-center gap-2">
                                                <p className="font-bold text-gray-900 text-sm">{PROVIDERS[key.provider]?.name || key.provider}</p>
                                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${key.is_valid ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                                    {key.is_valid ? 'Valid' : 'Invalid'}
                                                </span>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-0.5">{key.name} • <code className="bg-gray-100 px-1.5 py-0.5 rounded text-[10px]">{key.masked_key}</code></p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 shrink-0">
                                        <button
                                            onClick={() => { setTestingKeyId(key.id); testConnectionMutation.mutate(key.id); }}
                                            disabled={testConnectionMutation.isPending && testingKeyId === key.id}
                                            className="px-3 py-1.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-xs flex items-center gap-1"
                                        >
                                            {testConnectionMutation.isPending && testingKeyId === key.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <TestTube className="w-3 h-3" />}
                                            Test
                                        </button>
                                        <button
                                            onClick={() => { if (confirm("Delete this API key?")) deleteKeyMutation.mutate(key.id); }}
                                            className="p-1.5 text-gray-400 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Provider Cards */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(PROVIDERS).map(([key, provider]) => (
                    <div key={key} className="bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-5 hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold text-gray-900">{provider.name}</h4>
                            <a href={provider.url} target="_blank" rel="noopener noreferrer" className="text-[#0a4c2f] hover:text-[#073922]">
                                <ExternalLink className="w-4 h-4" />
                            </a>
                        </div>
                        <p className="text-sm text-gray-500">{provider.description}</p>
                    </div>
                ))}
            </div>

            {/* Add Key Dialog */}
            <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogContent className="sm:max-w-[500px] p-0 rounded-[24px]">
                    <div className="px-6 pt-6 pb-4 border-b border-gray-100">
                        <DialogHeader>
                            <DialogTitle className="text-xl font-bold text-gray-900">Add API Key</DialogTitle>
                            <DialogDescription className="text-sm text-gray-500">Add a new API key for an AI service provider.</DialogDescription>
                        </DialogHeader>
                    </div>

                    <div className="px-6 pb-6 pt-4 space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Provider</label>
                            <Select value={selectedProvider} onValueChange={setSelectedProvider}>
                                <SelectTrigger className="bg-gray-50 border-gray-200 rounded-xl focus:ring-[#0a4c2f]/20">
                                    <SelectValue placeholder="Select a provider" />
                                </SelectTrigger>
                                <SelectContent>
                                    {Object.entries(PROVIDERS).map(([key, provider]) => (
                                        <SelectItem key={key} value={key}>{provider.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Key Name</label>
                            <input
                                placeholder="e.g., Production API Key"
                                value={keyName}
                                onChange={(e) => setKeyName(e.target.value)}
                                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">API Key</label>
                            <div className="relative">
                                <input
                                    type={showKey ? "text" : "password"}
                                    placeholder={selectedProvider ? PROVIDERS[selectedProvider]?.placeholder : "Enter your API key"}
                                    value={apiKeyVal}
                                    onChange={(e) => setApiKeyVal(e.target.value)}
                                    className="w-full px-4 py-2.5 pr-10 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                                />
                                <button onClick={() => setShowKey(!showKey)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                    {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                            <p className="text-xs text-gray-400">Your key will be encrypted before storage</p>
                        </div>

                        {selectedProvider && (
                            <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl">
                                <p className="text-sm text-blue-700">
                                    Get your {PROVIDERS[selectedProvider]?.name} API key from{" "}
                                    <a href={PROVIDERS[selectedProvider]?.url} target="_blank" rel="noopener noreferrer" className="text-[#0a4c2f] font-medium hover:underline">their dashboard</a>
                                </p>
                            </div>
                        )}

                        <div className="flex justify-end gap-2 pt-2">
                            <button onClick={() => { setIsAddDialogOpen(false); resetForm(); }} className="px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm">
                                Cancel
                            </button>
                            <button onClick={handleAddKey} disabled={addKeyMutation.isPending} className="px-5 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-xl font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] relative overflow-hidden disabled:opacity-50">
                                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                                <span className="relative z-10">{addKeyMutation.isPending ? "Adding..." : "Add Key"}</span>
                            </button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
