"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Save, ArrowLeft, RefreshCw, AlertCircle } from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useConfig } from "@/hooks/use-config";
import { useAuth } from "@/contexts/AuthContext";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { toast } from "sonner";

export default function BusinessSettingsPage() {
    const router = useRouter();
    const { user, isAuthenticated } = useAuth();
    const tenantId = user?.tenant_id || user?.business_id || "default";
    const { config, isLoading, error, updateConfig, isUpdating, reloadConfig, isReloading } = useConfig(tenantId, isAuthenticated && !!tenantId);

    const [formData, setFormData] = useState({
        business_name: "",
        business_email: "",
        business_location: "",
        business_address: "",
        timezone: "America/New_York",
    });

    // Load config data into form
    useEffect(() => {
        if (config) {
            setFormData({
                business_name: config.business_name || "",
                business_email: config.business_email || "",
                business_location: config.business_location || "",
                business_address: config.business_address || "",
                timezone: config.timezone || "America/New_York",
            });
        }
    }, [config]);

    const handleSave = () => {
        updateConfig(formData, {
            onSuccess: () => toast.success("Business profile updated successfully"),
            onError: () => toast.error("Failed to update business profile"),
        });
    };

    const handleReload = () => {
        reloadConfig();
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
                        <h1 className="text-3xl font-bold mb-2">Business Profile</h1>
                        <p className="text-muted-foreground">
                            Manage your business information and operating hours
                        </p>
                    </div>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleReload}
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
                        Failed to load configuration. Please try again.
                    </AlertDescription>
                </Alert>
            )}

            <div className="grid grid-cols-1 gap-6">
                {/* Form */}
                <div className="bg-white border border-slate-200 shadow-sm rounded-2xl p-6">
                    {isLoading ? (
                        <div className="space-y-6">
                            <Skeleton className="h-20 w-full" />
                            <Skeleton className="h-20 w-full" />
                            <Skeleton className="h-32 w-full" />
                            <Skeleton className="h-20 w-full" />
                        </div>
                    ) : (
                        <div className="space-y-6">
                            <div>
                                <Label htmlFor="business_name">Business Name *</Label>
                                <Input
                                    id="business_name"
                                    value={formData.business_name}
                                    onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                                    className="bg-white border border-slate-200 shadow-sm mt-2"
                                    placeholder="Enter your business name"
                                />
                            </div>

                            <div>
                                <Label htmlFor="business_email">Email</Label>
                                <Input
                                    id="business_email"
                                    type="email"
                                    value={formData.business_email}
                                    onChange={(e) => setFormData({ ...formData, business_email: e.target.value })}
                                    className="bg-white border border-slate-200 shadow-sm mt-2"
                                    placeholder="contact@business.com"
                                />
                            </div>

                            <div>
                                <Label htmlFor="business_location">Location</Label>
                                <Input
                                    id="business_location"
                                    value={formData.business_location}
                                    onChange={(e) => setFormData({ ...formData, business_location: e.target.value })}
                                    className="bg-white border border-slate-200 shadow-sm mt-2"
                                    placeholder="Downtown Tunis, Avenue Habib Bourguiba"
                                />
                                <p className="text-xs text-muted-foreground mt-1">
                                    This is what the AI shares when callers ask where your business is located.
                                </p>
                            </div>

                            <div>
                                <Label htmlFor="business_address">Address</Label>
                                <Textarea
                                    id="business_address"
                                    value={formData.business_address}
                                    onChange={(e) => setFormData({ ...formData, business_address: e.target.value })}
                                    className="bg-white border border-slate-200 shadow-sm mt-2"
                                    rows={3}
                                    placeholder="123 Main St, City, State 12345"
                                />
                            </div>

                            <div>
                                <Label htmlFor="timezone">Timezone *</Label>
                                <Input
                                    id="timezone"
                                    value={formData.timezone}
                                    onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                                    className="bg-white border border-slate-200 shadow-sm mt-2"
                                    placeholder="America/New_York"
                                />
                                <p className="text-xs text-muted-foreground mt-1">
                                    Use IANA timezone format (e.g., America/New_York, Europe/London)
                                </p>
                            </div>

                            <div className="flex gap-3 pt-4">
                                <Button
                                    className="gap-2 bg-gradient-to-r from-primary to-accent"
                                    onClick={handleSave}
                                    disabled={isUpdating || !formData.business_name}
                                >
                                    {isUpdating ? (
                                        <>
                                            <RefreshCw className="w-4 h-4 animate-spin" />
                                            Saving...
                                        </>
                                    ) : (
                                        <>
                                            <Save className="w-4 h-4" />
                                            Save Changes
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
                    )}
                </div>
            </div>
        </div>
    );
}
