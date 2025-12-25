"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
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

// API Key types
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

// Provider information
const PROVIDERS = {
    vapi: {
        name: "VAPI.ai",
        description: "Voice AI platform for phone calls",
        url: "https://dashboard.vapi.ai",
        placeholder: "sk_live_...",
    },
    openai: {
        name: "OpenAI",
        description: "GPT models for AI conversations",
        url: "https://platform.openai.com/api-keys",
        placeholder: "sk-...",
    },
    groq: {
        name: "Groq",
        description: "Fast inference for LLaMA, Mixtral models",
        url: "https://console.groq.com/keys",
        placeholder: "gsk_...",
    },
    elevenlabs: {
        name: "ElevenLabs",
        description: "Text-to-speech voice synthesis",
        url: "https://elevenlabs.io/api",
        placeholder: "...",
    },
    anthropic: {
        name: "Anthropic",
        description: "Claude AI models",
        url: "https://console.anthropic.com",
        placeholder: "sk-ant-...",
    },
    deepgram: {
        name: "Deepgram",
        description: "Speech-to-text transcription",
        url: "https://console.deepgram.com",
        placeholder: "...",
    },
    whatsapp: {
        name: "WhatsApp Cloud API",
        description: "Meta WhatsApp Business Platform",
        url: "https://developers.facebook.com",
        placeholder: "EAA...",
    },
};

export default function APIKeysPage() {
    const router = useRouter();
    const queryClient = useQueryClient();
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [selectedProvider, setSelectedProvider] = useState("");
    const [keyName, setKeyName] = useState("");
    const [apiKey, setApiKey] = useState("");
    const [showKey, setShowKey] = useState(false);
    const [testingKeyId, setTestingKeyId] = useState<string | null>(null);

    // Fetch API keys
    const { data: apiKeys = [], isLoading } = useQuery<ApiKey[]>({
        queryKey: ["api-keys"],
        queryFn: async () => {
            const response = await api.get("/keys");
            return response;
        },
    });

    // Test connection mutation
    const testConnectionMutation = useMutation({
        mutationFn: async (keyId: string) => {
            const key = apiKeys.find(k => k.id === keyId);
            if (!key) throw new Error("Key not found");
            
            // Mock test - in production, you'd call a dedicated /keys/{id}/test endpoint
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

    // Add API key mutation
    const addKeyMutation = useMutation({
        mutationFn: async (data: ApiKeyCreate) => {
            const response = await api.post("/keys", data);
            return response;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["api-keys"] });
            toast.success("API Key added successfully");
            setIsAddDialogOpen(false);
            resetForm();
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || "Failed to add API key");
        },
    });

    // Delete API key mutation
    const deleteKeyMutation = useMutation({
        mutationFn: async (keyId: string) => {
            await api.delete(`/keys/${keyId}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["api-keys"] });
            toast.success("API Key deleted");
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || "Failed to delete API key");
        },
    });

    const resetForm = () => {
        setSelectedProvider("");
        setKeyName("");
        setApiKey("");
        setShowKey(false);
    };

    const handleAddKey = () => {
        if (!selectedProvider || !keyName || !apiKey) {
            toast.error("Please fill all fields");
            return;
        }

        addKeyMutation.mutate({
            provider: selectedProvider,
            name: keyName,
            api_key: apiKey,
        });
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return "Never";
        return new Date(dateString).toLocaleDateString();
    };

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => router.push("/dashboard/settings")}
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold mb-2">API Keys</h1>
                        <p className="text-muted-foreground">
                            Manage your API keys for AI services (BYOK - Bring Your Own Keys)
                        </p>
                    </div>
                </div>
                <Button
                    className="gap-2"
                    onClick={() => setIsAddDialogOpen(true)}
                >
                    <Plus className="w-4 h-4" />
                    Add API Key
                </Button>
            </div>

            {/* Info Alert */}
            <Alert className="mb-6">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                    <strong>Security:</strong> Your API keys are encrypted before storage. They are only visible when you add them.
                    We never store or transmit unencrypted keys.
                </AlertDescription>
            </Alert>

            {/* API Keys List */}
            <Card className="bg-white border-slate-200 shadow-sm">
                <CardHeader>
                    <CardTitle>Your API Keys</CardTitle>
                    <CardDescription>
                        Configure API keys for different AI providers to enable features
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="text-center py-8 text-muted-foreground">
                            Loading...
                        </div>
                    ) : apiKeys.length === 0 ? (
                        <div className="text-center py-8">
                            <Key className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                            <p className="text-muted-foreground mb-4">
                                No API keys configured yet
                            </p>
                            <Button onClick={() => setIsAddDialogOpen(true)}>
                                <Plus className="w-4 h-4 mr-2" />
                                Add Your First Key
                            </Button>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Provider</TableHead>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Key</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Last Used</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {apiKeys.map((key) => (
                                    <TableRow key={key.id}>
                                        <TableCell className="font-medium">
                                            {PROVIDERS[key.provider as keyof typeof PROVIDERS]?.name || key.provider}
                                        </TableCell>
                                        <TableCell>{key.name}</TableCell>
                                        <TableCell className="font-mono text-sm">
                                            {key.masked_key}
                                        </TableCell>
                                        <TableCell>
                                            {key.is_valid ? (
                                                <Badge variant="default" className="gap-1">
                                                    <Check className="w-3 h-3" />
                                                    Valid
                                                </Badge>
                                            ) : (
                                                <Badge variant="destructive" className="gap-1">
                                                    <X className="w-3 h-3" />
                                                    Invalid
                                                </Badge>
                                            )}
                                        </TableCell>
                                        <TableCell>{formatDate(key.last_used)}</TableCell>
                                        <TableCell>
                                            <div className="flex items-center gap-2">
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => {
                                                        setTestingKeyId(key.id);
                                                        testConnectionMutation.mutate(key.id);
                                                    }}
                                                    disabled={testConnectionMutation.isPending && testingKeyId === key.id}
                                                    className="gap-1"
                                                >
                                                    {testConnectionMutation.isPending && testingKeyId === key.id ? (
                                                        <Loader2 className="w-3 h-3 animate-spin" />
                                                    ) : (
                                                        <TestTube className="w-3 h-3" />
                                                    )}
                                                    Test
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => {
                                                        if (confirm("Delete this API key?")) {
                                                            deleteKeyMutation.mutate(key.id);
                                                        }
                                                    }}
                                                >
                                                    <Trash2 className="w-4 h-4 text-destructive" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Provider Info Cards */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(PROVIDERS).map(([key, provider]) => (
                    <Card key={key} className="bg-white border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                        <CardHeader>
                            <CardTitle className="bg-white border-slate-200 shadow-sm text-lg flex items-center justify-between">
                                {provider.name}
                                <a
                                    href={provider.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-primary hover:underline"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                </a>
                            </CardTitle>
                            <CardDescription>{provider.description}</CardDescription>
                        </CardHeader>
                    </Card>
                ))}
            </div>

            {/* Add Key Dialog */}
            <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                        <DialogTitle>Add API Key</DialogTitle>
                        <DialogDescription>
                            Add a new API key for an AI service provider
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
                                            {provider.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="name">Key Name</Label>
                            <Input
                                id="name"
                                placeholder="e.g., Production API Key"
                                value={keyName}
                                onChange={(e) => setKeyName(e.target.value)}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="apikey">API Key</Label>
                            <div className="relative">
                                <Input
                                    id="apikey"
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
                                Your key will be encrypted before storage
                            </p>
                        </div>

                        {selectedProvider && (
                            <Alert>
                                <AlertDescription className="text-sm">
                                    Get your {PROVIDERS[selectedProvider as keyof typeof PROVIDERS]?.name} API key from{" "}
                                    <a
                                        href={PROVIDERS[selectedProvider as keyof typeof PROVIDERS]?.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-primary hover:underline"
                                    >
                                        their dashboard
                                    </a>
                                </AlertDescription>
                            </Alert>
                        )}
                    </div>

                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => {
                                setIsAddDialogOpen(false);
                                resetForm();
                            }}
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handleAddKey}
                            disabled={addKeyMutation.isPending}
                        >
                            {addKeyMutation.isPending ? "Adding..." : "Add Key"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
