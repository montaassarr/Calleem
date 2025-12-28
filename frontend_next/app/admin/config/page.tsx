"use client";

import React, { useEffect, useState } from 'react';
import { adminApi, BusinessConfig } from '@/lib/api/admin';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';

export default function ConfigPage() {
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [config, setConfig] = useState<BusinessConfig>({
        business_name: '',
        timezone: 'UTC',
        currency: 'USD'
    });

    const { toast } = useToast();

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                setLoading(true);
                const data = await adminApi.getConfig();
                setConfig(data);
            } catch (error) {
                toast({
                    title: "Error",
                    description: "Failed to fetch configuration",
                    variant: "destructive"
                });
            } finally {
                setLoading(false);
            }
        };
        fetchConfig();
    }, [toast]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setIsSubmitting(true);
            await adminApi.updateConfig(config);
            toast({ title: "Success", description: "Configuration updated successfully" });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update configuration",
                variant: "destructive"
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    if (loading) {
        return <div className="p-8 text-center">Loading configuration...</div>;
    }

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold mb-6">Business Configuration</h1>

            <form onSubmit={handleSubmit} className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle>General Information</CardTitle>
                        <CardDescription>Basic details about your business.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="business_name">Business Name</Label>
                                <Input
                                    id="business_name"
                                    value={config.business_name}
                                    onChange={(e) => setConfig({ ...config, business_name: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="email">Business Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    value={config.email || ''}
                                    onChange={(e) => setConfig({ ...config, email: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="phone">Phone Number</Label>
                                <Input
                                    id="phone"
                                    value={config.phone_number || ''}
                                    onChange={(e) => setConfig({ ...config, phone_number: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="address">Address</Label>
                                <Input
                                    id="address"
                                    value={config.address || ''}
                                    onChange={(e) => setConfig({ ...config, address: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="timezone">Timezone</Label>
                                <Input
                                    id="timezone"
                                    value={config.timezone}
                                    onChange={(e) => setConfig({ ...config, timezone: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="currency">Currency</Label>
                                <Input
                                    id="currency"
                                    value={config.currency}
                                    onChange={(e) => setConfig({ ...config, currency: e.target.value })}
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>API Integrations</CardTitle>
                        <CardDescription>Configure external services.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="vapi_key">VAPI API Key</Label>
                            <Input
                                id="vapi_key"
                                type="password"
                                value={config.vapi_api_key || ''}
                                onChange={(e) => setConfig({ ...config, vapi_api_key: e.target.value })}
                                placeholder="sk-..."
                            />
                        </div>
                        <Separator />
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="twilio_sid">Twilio Account SID</Label>
                                <Input
                                    id="twilio_sid"
                                    value={config.twilio_account_sid || ''}
                                    onChange={(e) => setConfig({ ...config, twilio_account_sid: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="twilio_token">Twilio Auth Token</Label>
                                <Input
                                    id="twilio_token"
                                    type="password"
                                    value={config.twilio_auth_token || ''}
                                    onChange={(e) => setConfig({ ...config, twilio_auth_token: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="twilio_phone">Twilio Phone Number</Label>
                                <Input
                                    id="twilio_phone"
                                    value={config.twilio_phone_number || ''}
                                    onChange={(e) => setConfig({ ...config, twilio_phone_number: e.target.value })}
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>AI Settings</CardTitle>
                        <CardDescription>Configure AI behavior.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="system_prompt">System Prompt</Label>
                            <Textarea
                                id="system_prompt"
                                className="min-h-[150px]"
                                value={config.system_prompt || ''}
                                onChange={(e) => setConfig({ ...config, system_prompt: e.target.value })}
                                placeholder="You are a helpful receptionist..."
                            />
                        </div>
                    </CardContent>
                </Card>

                <div className="flex justify-end">
                    <Button type="submit" size="lg" disabled={isSubmitting}>
                        {isSubmitting ? "Saving Changes..." : "Save Configuration"}
                    </Button>
                </div>
            </form>
        </div>
    );
}
