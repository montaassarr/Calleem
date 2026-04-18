import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Phone, Check, X, Shield, Lock, Loader2, Trash2, RefreshCw } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { phoneApi } from '@/lib/api-endpoints';

interface PhoneStatus {
    has_phone: boolean;
    phone_number?: string;
    provider?: string;
    is_active: boolean;
    created_at?: string;
}

export function PhoneNumberManager() {
    const { user } = useAuth();
    const { toast } = useToast();
    const [loading, setLoading] = useState(false);
    const [statusLoading, setStatusLoading] = useState(true);
    const [phoneStatus, setPhoneStatus] = useState<PhoneStatus | null>(null);

    // Form state
    const [accountSid, setAccountSid] = useState('');
    const [authToken, setAuthToken] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');

    const fetchStatus = useCallback(async () => {
        try {
            setStatusLoading(true);
            const tenantId = user?.tenant_id;
            if (!tenantId) return;

            const data = await phoneApi.getStatus(tenantId);
            setPhoneStatus(data);
        } catch (error) {
            console.error("Failed to fetch phone status:", error);
        } finally {
            setStatusLoading(false);
        }
    }, [user]);

    useEffect(() => {
        if (user?.tenant_id) {
            fetchStatus();
        }
    }, [user, fetchStatus]);

    const handleProvision = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!accountSid || !authToken || !phoneNumber) {
            toast({
                title: "Missing Information",
                description: "Please fill in all Twilio credentials.",
                variant: "destructive"
            });
            return;
        }

        try {
            setLoading(true);
            const tenantId = user?.tenant_id;
            if (!tenantId) {
                throw new Error("Tenant ID not found");
            }

            await phoneApi.provision(tenantId, {
                twilio_account_sid: accountSid,
                twilio_auth_token: authToken,
                phone_number: phoneNumber,
            });

            toast({
                title: "Success",
                description: "Phone number successfully integrated!",
            });

            // Reset form
            setAccountSid('');
            setAuthToken('');
            setPhoneNumber('');

            // Refresh status
            fetchStatus();

        } catch (error: any) {
            toast({
                title: "Error",
                description: error.message,
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    const handleSync = async () => {
        try {
            setLoading(true);
            const tenantId = user?.tenant_id;
            if (!tenantId) {
                throw new Error("Tenant ID not found");
            }

            const result = await phoneApi.syncFromVapi(tenantId);

            if (result.success) {
                toast({
                    title: "✅ Sync Successful",
                    description: result.synced
                        ? `Synced phone: ${result.phone_number}`
                        : "No phone numbers found in Vapi dashboard",
                });
                fetchStatus();
            }
        } catch (error: any) {
            toast({
                title: "Sync Failed",
                description: error.message || "Failed to sync from Vapi dashboard",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    const handleRemove = async () => {
        if (!confirm("Are you sure you want to remove this phone number? This will disconnect your AI assistant from calls.")) {
            return;
        }

        try {
            setLoading(true);
            const tenantId = user?.tenant_id;
            if (!tenantId) {
                throw new Error("Tenant ID not found");
            }

            await phoneApi.remove(tenantId, false);

            toast({
                title: "Removed",
                description: "Phone number disconnected.",
            });

            fetchStatus();

        } catch (error: any) {
            toast({
                title: "Error",
                description: error.message,
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    if (statusLoading) {
        return (
            <Card>
                <CardContent className="pt-6 flex justify-center">
                    <Loader2 className="h-6 w-6 animate-spin text-gray-500" />
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="w-full bg-white border-slate-200 shadow-sm text-slate-900">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Phone className="h-5 w-5" />
                    Phone Integration
                </CardTitle>
                <CardDescription>
                    Connect your Twilio phone number to enable AI voice management.
                </CardDescription>
            </CardHeader>

            <CardContent>
                {phoneStatus?.has_phone && phoneStatus.is_active ? (
                    <div className="space-y-4">
                        <Alert className="bg-green-50 border-green-200">
                            <Check className="h-4 w-4 text-green-600" />
                            <AlertTitle className="text-green-800">Active Connection</AlertTitle>
                            <AlertDescription className="text-green-700">
                                Your AI assistant is connected to <strong>{phoneStatus.phone_number}</strong> relying on <strong>{phoneStatus.provider?.toUpperCase()}</strong>.
                            </AlertDescription>
                        </Alert>

                        <div className="flex justify-between gap-2">
                            <Button
                                variant="outline"
                                onClick={handleSync}
                                disabled={loading}
                                className="gap-2 bg-white text-slate-900 hover:bg-slate-50 border-slate-200"
                            >
                                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                                Sync from Vapi
                            </Button>
                            <Button
                                variant="destructive"
                                onClick={handleRemove}
                                disabled={loading}
                                className="gap-2 bg-red-600 hover:bg-red-700 text-white"
                            >
                                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                                Disconnect Number
                            </Button>
                        </div>
                    </div>
                ) : (
                    <form onSubmit={handleProvision} className="space-y-4">
                        <Alert className="bg-blue-50 border-blue-200 mb-4">
                            <Shield className="h-4 w-4 text-blue-600" />
                            <AlertTitle className="text-blue-800">Secure Integration</AlertTitle>
                            <AlertDescription className="text-blue-700 text-xs">
                                Your credentials are encrypted using AES-256 before storage. We verify ownership before connecting.
                                <br />
                                <strong className="mt-2 block">💡 Tip:</strong> If you added a phone in the Vapi dashboard manually, click the "Sync from Vapi" button below.
                            </AlertDescription>
                        </Alert>

                        <div className="flex justify-end mb-4">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleSync}
                                disabled={loading}
                                className="gap-2 bg-white text-slate-900 hover:bg-slate-50 border-slate-200"
                            >
                                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                                Sync from Vapi Dashboard
                            </Button>
                        </div>

                        <div className="grid gap-2">
                            <Label htmlFor="sid">Twilio Account SID</Label>
                            <div className="relative">
                                <Lock className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                                <Input
                                    id="sid"
                                    placeholder="AC..."
                                    value={accountSid}
                                    onChange={(e) => setAccountSid(e.target.value)}
                                    className="pl-9 bg-white border-slate-200 text-slate-900"
                                    required
                                />
                            </div>
                        </div>

                        <div className="grid gap-2">
                            <Label htmlFor="token">Twilio Auth Token</Label>
                            <div className="relative">
                                <Lock className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                                <Input
                                    id="token"
                                    type="password"
                                    placeholder="Your auth token"
                                    value={authToken}
                                    onChange={(e) => setAuthToken(e.target.value)}
                                    className="pl-9 bg-white border-slate-200 text-slate-900"
                                    required
                                />
                            </div>
                        </div>

                        <div className="grid gap-2">
                            <Label htmlFor="phone">Phone Number (E.164)</Label>
                            <div className="relative">
                                <Phone className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                                <Input
                                    id="phone"
                                    placeholder="+1234567890"
                                    value={phoneNumber}
                                    onChange={(e) => setPhoneNumber(e.target.value)}
                                    className="pl-9 bg-white border-slate-200 text-slate-900"
                                    required
                                />
                            </div>
                            <p className="text-xs text-gray-500">Must include country code (e.g. +1 for US)</p>
                        </div>

                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Connecting...
                                </>
                            ) : (
                                "Connect Phone Number"
                            )}
                        </Button>
                    </form>
                )}
            </CardContent>
        </Card>
    );
}
