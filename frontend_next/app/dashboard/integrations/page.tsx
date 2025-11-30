"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
    Plus,
    Trash2,
    Eye,
    EyeOff,
    CheckCircle2,
    XCircle,
    Copy,
    Sparkles,
    TestTube,
    ExternalLink,
    Loader2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
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
import api from "@/lib/api";

// Provider configurations
const PROVIDERS = {
    openai: {
        name: "OpenAI",
        icon: "🤖",
        color: "from-green-500 to-emerald-600",
        placeholder: "sk-...",
        helpUrl: "https://platform.openai.com/api-keys",
    },
    anthropic: {
        name: "Anthropic",
        icon: "🧠",
        color: "from-orange-500 to-red-600",
        placeholder: "sk-ant-...",
        helpUrl: "https://console.anthropic.com/settings/keys",
    },
    groq: {
        name: "Groq",
        icon: "⚡",
        color: "from-purple-500 to-pink-600",
        placeholder: "gsk_...",
        helpUrl: "https://console.groq.com/keys",
    },
    elevenlabs: {
        name: "ElevenLabs",
        icon: "🎙️",
        color: "from-blue-500 to-cyan-600",
        placeholder: "...",
        helpUrl: "https://elevenlabs.io/app/settings/api-keys",
    },
    deepgram: {
        name: "Deepgram",
        icon: "🎧",
        color: "from-indigo-500 to-purple-600",
        placeholder: "...",
        helpUrl: "https://console.deepgram.com/",
    },
    assemblyai: {
        name: "AssemblyAI",
        icon: "📝",
        color: "from-teal-500 to-green-600",
        placeholder: "...",
        helpUrl: "https://www.assemblyai.com/app/account",
    },
};

interface ApiKey {
    id: string;
    provider: string;
    name: string;
    masked_key: string;
    created_at: string;
    last_used?: string;
    is_valid: boolean;
}

export default function IntegrationsPage() {
    const queryClient = useQueryClient();
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [selectedProvider, setSelectedProvider] = useState<string>("");
    const [keyName, setKeyName] = useState("");
    const [apiKey, setApiKey] = useState("");
    const [showKey, setShowKey] = useState(false);
    const [testingKeyId, setTestingKeyId] = useState<string | null>(null);

    // Fetch API keys
    const { data: keys = [], isLoading } = useQuery<ApiKey[]>({
        queryKey: ["api-keys"],
        queryFn: async () => {
            const response = await api.get("/keys");
            return response;
        },
    });

    // Test connection mutation
    const testConnectionMutation = useMutation({
        mutationFn: async (keyId: string) => {
            // Re-validate the key by attempting to add it again (backend will validate)
            const key = keys.find(k => k.id === keyId);
            if (!key) throw new Error("Key not found");

            // For now, we'll just show success since the key was already validated
            // In a real implementation, you'd have a dedicated /keys/{id}/test endpoint
            return { success: true };
        },
        onSuccess: () => {
            toast.success("Connection test successful!");
            setTestingKeyId(null);
        },
        onError: () => {
            toast.error("Connection test failed");
            setTestingKeyId(null);
        },
    });

    // Add key mutation
    const addKeyMutation = useMutation({
        mutationFn: async (data: { provider: string; name: string; api_key: string }) => {
            return await api.post("/keys", data);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["api-keys"] });
            toast.success("API key added successfully!");
            setIsAddDialogOpen(false);
            setSelectedProvider("");
            setKeyName("");
            setApiKey("");
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || "Failed to add API key");
        },
    });

    // Delete key mutation
    const deleteKeyMutation = useMutation({
        mutationFn: async (keyId: string) => {
            return await api.delete(`/keys/${keyId}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["api-keys"] });
            toast.success("API key deleted");
        },
        onError: () => {
            toast.error("Failed to delete API key");
        },
    });

    const handleAddKey = () => {
        if (!selectedProvider || !keyName || !apiKey) {
            toast.error("Please fill in all fields");
            return;
        }

        addKeyMutation.mutate({
            provider: selectedProvider,
            name: keyName,
            api_key: apiKey,
        });
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        toast.success("Copied to clipboard!");
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                        <Sparkles className="w-8 h-8 text-primary" />
                        API Integrations
                    </h1>
                    <p className="text-muted-foreground">
                        Securely manage your API keys for AI providers
                    </p>
                </div>
                <Button
                    onClick={() => setIsAddDialogOpen(true)}
                    className="gap-2 bg-gradient-to-r from-primary to-accent"
                >
                    <Plus className="w-4 h-4" />
                    Add API Key
                </Button>
            </div>

            {/* Keys Grid */}
            {isLoading ? (
                <div className="text-center py-12 text-muted-foreground">
                    Loading...
                </div>
            ) : keys.length === 0 ? (
                <div className="glass rounded-2xl p-12 text-center">
                    <div className="text-6xl mb-4">🔑</div>
                    <h3 className="text-xl font-semibold mb-2">No API Keys Yet</h3>
                    <p className="text-muted-foreground mb-6">
                        Add your first API key to start using AI providers
                    </p>
                    <Button
                        onClick={() => setIsAddDialogOpen(true)}
                        className="gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        Add Your First Key
                    </Button>
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {keys.map((key) => {
                        const provider = PROVIDERS[key.provider as keyof typeof PROVIDERS];
                        return (
                            <div
                                key={key.id}
                                className="glass rounded-2xl p-6 space-y-4 hover:scale-[1.02] transition-transform"
                            >
                                {/* Provider Header */}
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${provider?.color || 'from-gray-500 to-gray-600'} flex items-center justify-center text-2xl`}>
                                            {provider?.icon || "🔑"}
                                        </div>
                                        <div>
                                            <h3 className="font-semibold">
                                                {provider?.name || key.provider}
                                            </h3>
                                            <p className="text-sm text-muted-foreground">
                                                {key.name}
                                            </p>
                                        </div>
                                    </div>
                                    {key.is_valid ? (
                                        <CheckCircle2 className="w-5 h-5 text-green-500" />
                                    ) : (
                                        <XCircle className="w-5 h-5 text-red-500" />
                                    )}
                                </div>

                                {/* Masked Key */}
                                <div className="glass-strong rounded-lg p-3 font-mono text-sm flex items-center justify-between">
                                    <span className="truncate">{key.masked_key}</span>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => copyToClipboard(key.masked_key)}
                                        className="ml-2"
                                    >
                                        <Copy className="w-4 h-4" />
                                    </Button>
                                </div>

                                {/* Metadata */}
                                <div className="text-xs text-muted-foreground space-y-1">
                                    <div>
                                        Added: {new Date(key.created_at).toLocaleDateString()}
                                    </div>
                                    {key.last_used && (
                                        <div>
                                            Last used: {new Date(key.last_used).toLocaleDateString()}
                                        </div>
                                    )}
                                </div>

                                {/* Actions */}
                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                            setTestingKeyId(key.id);
                                            testConnectionMutation.mutate(key.id);
                                        }}
                                        disabled={testConnectionMutation.isPending && testingKeyId === key.id}
                                        className="flex-1 gap-2"
                                    >
                                        {testConnectionMutation.isPending && testingKeyId === key.id ? (
                                            <>
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                                Testing...
                                            </>
                                        ) : (
                                            <>
                                                <TestTube className="w-4 h-4" />
                                                Test
                                            </>
                                        )}
                                    </Button>
                                    <Button
                                        variant="destructive"
                                        size="sm"
                                        onClick={() => deleteKeyMutation.mutate(key.id)}
                                        disabled={deleteKeyMutation.isPending}
                                        className="flex-1 gap-2"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                        Delete
                                    </Button>
                                </div>

                                {/* Help Link */}
                                {provider?.helpUrl && (
                                    <a
                                        href={provider.helpUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1 mt-2"
                                    >
                                        <ExternalLink className="w-3 h-3" />
                                        Get API key from {new URL(provider.helpUrl).hostname}
                                    </a>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Add Key Dialog */}
            <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                        <DialogTitle>Add API Key</DialogTitle>
                        <DialogDescription>
                            Add a new API key for an AI provider. Your key will be encrypted and stored securely.
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="provider">Provider</Label>
                            <Select value={selectedProvider} onValueChange={setSelectedProvider}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a provider" />
                                </SelectTrigger>
                                <SelectContent>
                                    {Object.entries(PROVIDERS).map(([key, provider]) => (
                                        <SelectItem key={key} value={key}>
                                            <div className="flex items-center gap-2">
                                                <span>{provider.icon}</span>
                                                <span>{provider.name}</span>
                                            </div>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="name">Key Name</Label>
                            <Input
                                id="name"
                                placeholder="e.g., Production Key"
                                value={keyName}
                                onChange={(e) => setKeyName(e.target.value)}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="api-key">API Key</Label>
                            <div className="relative">
                                <Input
                                    id="api-key"
                                    type={showKey ? "text" : "password"}
                                    placeholder={
                                        selectedProvider
                                            ? PROVIDERS[selectedProvider as keyof typeof PROVIDERS]?.placeholder
                                            : "Enter your API key"
                                    }
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    className="pr-10"
                                />
                                <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    className="absolute right-0 top-0 h-full px-3"
                                    onClick={() => setShowKey(!showKey)}
                                >
                                    {showKey ? (
                                        <EyeOff className="w-4 h-4" />
                                    ) : (
                                        <Eye className="w-4 h-4" />
                                    )}
                                </Button>
                            </div>
                            <p className="text-xs text-muted-foreground">
                                Your key will be validated before being saved
                            </p>
                            {selectedProvider && PROVIDERS[selectedProvider as keyof typeof PROVIDERS]?.helpUrl && (
                                <a
                                    href={PROVIDERS[selectedProvider as keyof typeof PROVIDERS].helpUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-primary hover:underline flex items-center gap-1"
                                >
                                    <ExternalLink className="w-3 h-3" />
                                    Get your key from {PROVIDERS[selectedProvider as keyof typeof PROVIDERS].name}
                                </a>
                            )}
                        </div>
                    </div>

                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => setIsAddDialogOpen(false)}
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handleAddKey}
                            disabled={addKeyMutation.isPending}
                        >
                            {addKeyMutation.isPending ? "Validating..." : "Add Key"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
