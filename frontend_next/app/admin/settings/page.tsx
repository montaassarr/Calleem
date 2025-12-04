"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Settings as SettingsIcon, Save, Database, Globe, Bell, Shield } from "lucide-react";
import { toast } from "sonner";

export default function GlobalSettingsPage() {
    const handleSave = () => {
        toast.success("Settings saved successfully!");
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold mb-2">Global Settings</h1>
                <p className="text-muted-foreground">
                    Configure platform-wide settings and defaults
                </p>
            </div>

            {/* Platform Settings */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Globe className="h-5 w-5" />
                        <CardTitle>Platform Configuration</CardTitle>
                    </div>
                    <CardDescription>
                        General platform settings
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                            <Label>Platform Name</Label>
                            <Input defaultValue="AI Receptionist SaaS" />
                        </div>
                        <div className="space-y-2">
                            <Label>Support Email</Label>
                            <Input type="email" defaultValue="support@example.com" />
                        </div>
                        <div className="space-y-2">
                            <Label>Default Timezone</Label>
                            <Input defaultValue="UTC" />
                        </div>
                        <div className="space-y-2">
                            <Label>Default Currency</Label>
                            <Input defaultValue="USD" />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* AI Configuration */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <SettingsIcon className="h-5 w-5" />
                        <CardTitle>AI Configuration</CardTitle>
                    </div>
                    <CardDescription>
                        Default AI settings for new businesses
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                            <Label>Default AI Model</Label>
                            <Input defaultValue="Groq Mixtral-8x7b" />
                        </div>
                        <div className="space-y-2">
                            <Label>Default Voice Provider</Label>
                            <Input defaultValue="ElevenLabs" />
                        </div>
                        <div className="space-y-2">
                            <Label>Max Call Duration (seconds)</Label>
                            <Input type="number" defaultValue="300" />
                        </div>
                        <div className="space-y-2">
                            <Label>Call Recording Retention (days)</Label>
                            <Input type="number" defaultValue="30" />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Plan Limits */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Database className="h-5 w-5" />
                        <CardTitle>Plan Limits</CardTitle>
                    </div>
                    <CardDescription>
                        Configure limits for each subscription tier
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div>
                        <h3 className="font-semibold mb-3">Free Plan</h3>
                        <div className="grid gap-4 md:grid-cols-3">
                            <div className="space-y-2">
                                <Label>Max Appointments/Month</Label>
                                <Input type="number" defaultValue="50" />
                            </div>
                            <div className="space-y-2">
                                <Label>Max AI Calls/Month</Label>
                                <Input type="number" defaultValue="100" />
                            </div>
                            <div className="space-y-2">
                                <Label>Price</Label>
                                <Input defaultValue="$0" disabled />
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 className="font-semibold mb-3">Pro Plan</h3>
                        <div className="grid gap-4 md:grid-cols-3">
                            <div className="space-y-2">
                                <Label>Max Appointments/Month</Label>
                                <Input defaultValue="Unlimited" disabled />
                            </div>
                            <div className="space-y-2">
                                <Label>Max AI Calls/Month</Label>
                                <Input defaultValue="Unlimited" disabled />
                            </div>
                            <div className="space-y-2">
                                <Label>Price</Label>
                                <Input defaultValue="$49/month" />
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 className="font-semibold mb-3">Enterprise Plan</h3>
                        <div className="grid gap-4 md:grid-cols-3">
                            <div className="space-y-2">
                                <Label>Max Appointments/Month</Label>
                                <Input defaultValue="Unlimited" disabled />
                            </div>
                            <div className="space-y-2">
                                <Label>Max AI Calls/Month</Label>
                                <Input defaultValue="Unlimited" disabled />
                            </div>
                            <div className="space-y-2">
                                <Label>Price</Label>
                                <Input defaultValue="$199/month" />
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Notifications */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Bell className="h-5 w-5" />
                        <CardTitle>Notifications</CardTitle>
                    </div>
                    <CardDescription>
                        Platform notification settings
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <Label>Email Notifications</Label>
                            <p className="text-sm text-muted-foreground">Send emails for appointments</p>
                        </div>
                        <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <Label>SMS Notifications</Label>
                            <p className="text-sm text-muted-foreground">Send SMS reminders</p>
                        </div>
                        <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <Label>Admin Alerts</Label>
                            <p className="text-sm text-muted-foreground">Alert admin for errors</p>
                        </div>
                        <Switch defaultChecked />
                    </div>
                </CardContent>
            </Card>

            {/* Security */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        <CardTitle>Security</CardTitle>
                    </div>
                    <CardDescription>
                        Platform security settings
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <Label>Maintenance Mode</Label>
                            <p className="text-sm text-muted-foreground">Enable maintenance mode</p>
                        </div>
                        <Switch />
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <Label>Public API Access</Label>
                            <p className="text-sm text-muted-foreground">Allow public API access</p>
                        </div>
                        <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <Label>2FA Required</Label>
                            <p className="text-sm text-muted-foreground">Require 2FA for all users</p>
                        </div>
                        <Switch />
                    </div>
                </CardContent>
            </Card>

            {/* Save Button */}
            <div className="flex justify-end">
                <Button size="lg" onClick={handleSave} className="gap-2">
                    <Save className="h-4 w-4" />
                    Save All Settings
                </Button>
            </div>
        </div>
    );
}
