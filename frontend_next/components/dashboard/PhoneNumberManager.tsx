import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Phone, Check, X, Shield, Lock, Loader2, Trash2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/contexts/AuthContext';

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

    // Get token from storage
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    // Form state
    const [accountSid, setAccountSid] = useState('');
    const [authToken, setAuthToken] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');

    useEffect(() => {
        if (user?.email) {
            fetchStatus();
        }
    }, [user]);

    const fetchStatus = async () => {
        try {
            setStatusLoading(true);
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/phone-numbers/status/${user?.email}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (res.ok) {
                const data = await res.json();
                setPhoneStatus(data);
            }
        } catch (error) {
            console.error("Failed to fetch phone status:", error);
        } finally {
            setStatusLoading(false);
        }
    };

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
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/phone-numbers/provision/${user?.email}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    twilio_account_sid: accountSid,
                    twilio_auth_token: authToken,
                    phone_number: phoneNumber
                })
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || "Provisioning failed");
            }

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

    const handleRemove = async () => {
        if (!confirm("Are you sure you want to remove this phone number? This will disconnect your AI assistant from calls.")) {
            return;
        }

        try {
            setLoading(true);
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/phone-numbers/${user?.email}?delete_from_vapi=false`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Removal failed");
            }

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
        <Card className="w-full">
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

                        <div className="flex justify-end">
                            <Button
                                variant="destructive"
                                onClick={handleRemove}
                                disabled={loading}
                                className="gap-2"
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
                            </AlertDescription>
                        </Alert>

                        <div className="grid gap-2">
                            <Label htmlFor="sid">Twilio Account SID</Label>
                            <div className="relative">
                                <Lock className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                                <Input
                                    id="sid"
                                    placeholder="AC..."
                                    value={accountSid}
                                    onChange={(e) => setAccountSid(e.target.value)}
                                    className="pl-9"
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
                                    className="pl-9"
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
                                    className="pl-9"
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
