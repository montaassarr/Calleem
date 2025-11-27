import { CheckCircle2, Building2, Key, Scissors, Clock } from "lucide-react";
import { useOnboarding } from "@/contexts/OnboardingContext";

export function CompleteStep() {
    const { data } = useOnboarding();

    const hasApiKeys = data.groqApiKey || data.twilioAccountSid;
    const enabledDays = Object.entries(data.businessHours).filter(([_, hours]) => hours.enabled);

    return (
        <div className="max-w-2xl mx-auto space-y-8 py-8">
            <div className="text-center space-y-4">
                <div className="w-20 h-20 mx-auto bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
                    <CheckCircle2 className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-4xl font-bold">You're All Set! 🎉</h1>
                <p className="text-xl text-muted-foreground">
                    Your business is configured and ready to go
                </p>
            </div>

            <div className="glass rounded-2xl p-6 space-y-6">
                <h2 className="text-lg font-semibold">Configuration Summary</h2>

                <div className="space-y-4">
                    {/* Business Details */}
                    <div className="flex gap-4 p-4 rounded-lg bg-white/50 dark:bg-white/5">
                        <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0">
                            <Building2 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div className="flex-1">
                            <h3 className="font-semibold mb-1">Business Details</h3>
                            <p className="text-sm text-muted-foreground">{data.businessName}</p>
                            <p className="text-sm text-muted-foreground">{data.email}</p>
                            <p className="text-sm text-muted-foreground">{data.phone}</p>
                        </div>
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                    </div>

                    {/* API Keys */}
                    <div className="flex gap-4 p-4 rounded-lg bg-white/50 dark:bg-white/5">
                        <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center flex-shrink-0">
                            <Key className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div className="flex-1">
                            <h3 className="font-semibold mb-1">API Keys</h3>
                            <p className="text-sm text-muted-foreground">
                                {hasApiKeys
                                    ? "Configured and ready for AI conversations"
                                    : "Not configured (you can add these later)"}
                            </p>
                        </div>
                        {hasApiKeys && <CheckCircle2 className="w-5 h-5 text-green-600" />}
                    </div>

                    {/* Services */}
                    <div className="flex gap-4 p-4 rounded-lg bg-white/50 dark:bg-white/5">
                        <div className="w-10 h-10 rounded-full bg-orange-100 dark:bg-orange-900 flex items-center justify-center flex-shrink-0">
                            <Scissors className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                        </div>
                        <div className="flex-1">
                            <h3 className="font-semibold mb-1">Services</h3>
                            <p className="text-sm text-muted-foreground">
                                {data.services.length} service{data.services.length !== 1 ? "s" : ""} configured
                            </p>
                            {data.services.length > 0 && (
                                <ul className="text-sm text-muted-foreground mt-1">
                                    {data.services.slice(0, 3).map((service, i) => (
                                        <li key={i}>• {service.name} - ${service.price}</li>
                                    ))}
                                    {data.services.length > 3 && (
                                        <li>• and {data.services.length - 3} more...</li>
                                    )}
                                </ul>
                            )}
                        </div>
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                    </div>

                    {/* Business Hours */}
                    <div className="flex gap-4 p-4 rounded-lg bg-white/50 dark:bg-white/5">
                        <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center flex-shrink-0">
                            <Clock className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                        <div className="flex-1">
                            <h3 className="font-semibold mb-1">Business Hours</h3>
                            <p className="text-sm text-muted-foreground">
                                Open {enabledDays.length} day{enabledDays.length !== 1 ? "s" : ""} per week
                            </p>
                        </div>
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                    </div>
                </div>
            </div>

            <div className="glass rounded-xl p-6 space-y-3">
                <h3 className="font-semibold">What's Next?</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        Explore your dashboard and familiarize yourself with the features
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        Test the AI receptionist by sending a message
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        Configure additional settings in the Settings menu
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        Invite team members to collaborate
                    </li>
                </ul>
            </div>
        </div>
    );
}
