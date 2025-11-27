import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, Key, AlertCircle } from "lucide-react";
import { useOnboarding } from "@/contexts/OnboardingContext";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export function ApiKeysStep() {
    const { data, updateData } = useOnboarding();
    const [showKeys, setShowKeys] = useState({
        groq: false,
        twilioSid: false,
        twilioToken: false,
    });

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="space-y-2">
                <h2 className="text-2xl font-bold">API Keys (Optional)</h2>
                <p className="text-muted-foreground">
                    Configure your AI and messaging integrations. You can skip this and add them later in settings.
                </p>
            </div>

            <div className="glass rounded-xl p-4 border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/20">
                <div className="flex gap-3">
                    <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                    <div className="space-y-1">
                        <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                            You can skip this step
                        </p>
                        <p className="text-xs text-blue-700 dark:text-blue-300">
                            API keys can be added later from Settings → Integrations
                        </p>
                    </div>
                </div>
            </div>

            {/* Groq AI */}
            <div className="glass rounded-2xl p-6 space-y-4">
                <div className="flex items-center gap-2">
                    <Key className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-lg">Groq AI</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                    Fast AI inference for conversation handling
                </p>

                <div className="space-y-2">
                    <Label htmlFor="groqApiKey">API Key</Label>
                    <div className="relative">
                        <Input
                            id="groqApiKey"
                            type={showKeys.groq ? "text" : "password"}
                            placeholder="gsk_..."
                            value={data.groqApiKey}
                            onChange={(e) => updateData({ groqApiKey: e.target.value })}
                        />
                        <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="absolute right-0 top-0"
                            onClick={() => setShowKeys({ ...showKeys, groq: !showKeys.groq })}
                        >
                            {showKeys.groq ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">
                        Get your API key from{" "}
                        <a
                            href="https://console.groq.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline"
                        >
                            console.groq.com
                        </a>
                    </p>
                </div>
            </div>

            {/* Twilio */}
            <div className="glass rounded-2xl p-6 space-y-4">
                <div className="flex items-center gap-2">
                    <Key className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-lg">Twilio</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                    SMS and WhatsApp messaging platform
                </p>

                <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <Label htmlFor="twilioAccountSid">Account SID</Label>
                        <div className="relative">
                            <Input
                                id="twilioAccountSid"
                                type={showKeys.twilioSid ? "text" : "password"}
                                placeholder="AC..."
                                value={data.twilioAccountSid}
                                onChange={(e) => updateData({ twilioAccountSid: e.target.value })}
                            />
                            <Button
                                type="button"
                                variant="ghost"
                                size="icon"
                                className="absolute right-0 top-0"
                                onClick={() => setShowKeys({ ...showKeys, twilioSid: !showKeys.twilioSid })}
                            >
                                {showKeys.twilioSid ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </Button>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="twilioAuthToken">Auth Token</Label>
                        <div className="relative">
                            <Input
                                id="twilioAuthToken"
                                type={showKeys.twilioToken ? "text" : "password"}
                                placeholder="..."
                                value={data.twilioAuthToken}
                                onChange={(e) => updateData({ twilioAuthToken: e.target.value })}
                            />
                            <Button
                                type="button"
                                variant="ghost"
                                size="icon"
                                className="absolute right-0 top-0"
                                onClick={() => setShowKeys({ ...showKeys, twilioToken: !showKeys.twilioToken })}
                            >
                                {showKeys.twilioToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </Button>
                        </div>
                    </div>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="twilioPhoneNumber">Phone Number</Label>
                    <Input
                        id="twilioPhoneNumber"
                        type="tel"
                        placeholder="+1234567890"
                        value={data.twilioPhoneNumber}
                        onChange={(e) => updateData({ twilioPhoneNumber: e.target.value })}
                    />
                </div>

                <p className="text-xs text-muted-foreground">
                    Get your credentials from{" "}
                    <a
                        href="https://console.twilio.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                    >
                        console.twilio.com
                    </a>
                </p>
            </div>
        </div>
    );
}
