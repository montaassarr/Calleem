"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    Save,
    ArrowLeft,
    RefreshCw,
    AlertCircle,
    Plus,
    Trash2,
    GripVertical
} from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useConfig } from "@/hooks/use-config";
import { Switch } from "@/components/ui/switch";
import {
    Card,
    CardContent,
    CardHeader,
} from "@/components/ui/card";
import { toast } from "sonner";

interface Service {
    name: string;
    description: string;
    duration_minutes: number;
    price: number;
    is_active: boolean;
}

export default function ServicesSettingsPage() {
    const router = useRouter();
    const { config, isLoading, error, updateConfig, isUpdating, reloadConfig, isReloading } = useConfig();

    const [services, setServices] = useState<Service[]>([]);

    useEffect(() => {
        if (config?.services) {
            setServices(config.services.map(s => ({
                name: s.name,
                description: s.description || "",
                duration_minutes: s.duration_minutes,
                price: s.price,
                is_active: s.is_active ?? true,
            })));
        }
    }, [config]);

    const handleSave = () => {
        updateConfig({
            services: services
        }, {
            onSuccess: () => toast.success("Services configuration updated successfully"),
            onError: () => toast.error("Failed to update services configuration"),
        });
    };

    const addService = () => {
        setServices([...services, {
            name: "",
            description: "",
            duration_minutes: 30,
            price: 0,
            is_active: true,
        }]);
    };

    const removeService = (index: number) => {
        setServices(services.filter((_, i) => i !== index));
    };

    const updateService = (index: number, field: keyof Service, value: any) => {
        const updated = [...services];
        updated[index] = { ...updated[index], [field]: value };
        setServices(updated);
    };

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => router.push('/dashboard/settings')}
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold mb-2">Services Management</h1>
                        <p className="text-muted-foreground">
                            Configure your business services, pricing, and durations
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
                <Alert variant="destructive" className="mb-6 max-w-4xl">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        Failed to load services configuration. Please try again.
                    </AlertDescription>
                </Alert>
            )}

            {/* Services List */}
            <div className="max-w-4xl space-y-4 mb-6">
                {isLoading ? (
                    <>
                        <Skeleton className="h-48 w-full" />
                        <Skeleton className="h-48 w-full" />
                    </>
                ) : (
                    <>
                        {services.map((service, index) => (
                            <Card key={index} className="glass">
                                <CardHeader className="pb-3">
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-center gap-3 flex-1">
                                            <GripVertical className="w-5 h-5 text-muted-foreground cursor-move" />
                                            <div className="flex-1">
                                                <Input
                                                    value={service.name}
                                                    onChange={(e) => updateService(index, 'name', e.target.value)}
                                                    placeholder="Service name (e.g., Classic Haircut)"
                                                    className="glass-strong text-lg font-semibold"
                                                    disabled={isUpdating}
                                                />
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Switch
                                                checked={service.is_active}
                                                onCheckedChange={(checked) => updateService(index, 'is_active', checked)}
                                                disabled={isUpdating}
                                            />
                                            <span className="text-sm text-muted-foreground min-w-[60px]">
                                                {service.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => removeService(index)}
                                                disabled={isUpdating}
                                            >
                                                <Trash2 className="w-4 h-4 text-destructive" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <Label>Description</Label>
                                        <Textarea
                                            value={service.description}
                                            onChange={(e) => updateService(index, 'description', e.target.value)}
                                            placeholder="Brief description of the service..."
                                            className="glass-strong mt-2 min-h-[80px]"
                                            disabled={isUpdating}
                                        />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label>Duration (minutes)</Label>
                                            <Input
                                                type="number"
                                                value={service.duration_minutes}
                                                onChange={(e) => updateService(index, 'duration_minutes', parseInt(e.target.value) || 0)}
                                                className="glass-strong mt-2"
                                                min={5}
                                                step={5}
                                                disabled={isUpdating}
                                            />
                                        </div>
                                        <div>
                                            <Label>Price (TND)</Label>
                                            <Input
                                                type="number"
                                                value={service.price}
                                                onChange={(e) => updateService(index, 'price', parseFloat(e.target.value) || 0)}
                                                className="glass-strong mt-2"
                                                min={0}
                                                step={0.5}
                                                disabled={isUpdating}
                                            />
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}

                        {/* Add Service Button */}
                        <Button
                            variant="outline"
                            className="w-full glass-strong gap-2"
                            onClick={addService}
                            disabled={isUpdating}
                        >
                            <Plus className="w-4 h-4" />
                            Add New Service
                        </Button>
                    </>
                )}
            </div>

            {/* Save Button */}
            <div className="max-w-4xl">
                <div className="flex gap-3">
                    <Button
                        className="gap-2 bg-gradient-to-r from-primary to-accent"
                        onClick={handleSave}
                        disabled={isUpdating || isLoading || services.length === 0}
                    >
                        {isUpdating ? (
                            <>
                                <RefreshCw className="w-4 h-4 animate-spin" />
                                Saving...
                            </>
                        ) : (
                            <>
                                <Save className="w-4 h-4" />
                                Save Services
                            </>
                        )}
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => router.push('/dashboard/settings')}
                        disabled={isUpdating}
                    >
                        Cancel
                    </Button>
                </div>
            </div>

            {/* Info */}
            <div className="glass rounded-lg p-4 max-w-4xl mt-6 border border-blue-500/20">
                <p className="text-sm text-blue-600 dark:text-blue-400">
                    💡 <strong>Tip:</strong> Services marked as inactive won&apos;t be available for booking but will remain in your database. Drag the grip icon to reorder services (coming soon).
                </p>
            </div>
        </div>
    );
}
