import { Sparkles, Rocket, Shield } from "lucide-react";

export function WelcomeStep() {
    return (
        <div className="max-w-2xl mx-auto text-center space-y-8 py-12">
            <div className="space-y-4">
                <div className="w-20 h-20 mx-auto bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center">
                    <Rocket className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-4xl font-bold">Welcome to AI Receptionist! 🎉</h1>
                <p className="text-xl text-muted-foreground">
                    Let's get your business set up in just a few minutes
                </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6 pt-8">
                <div className="glass rounded-2xl p-6 space-y-3">
                    <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto">
                        <Sparkles className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <h3 className="font-semibold">AI-Powered</h3>
                    <p className="text-sm text-muted-foreground">
                        Automated appointment booking and customer conversations
                    </p>
                </div>

                <div className="glass rounded-2xl p-6 space-y-3">
                    <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto">
                        <Shield className="w-6 h-6 text-green-600 dark:text-green-400" />
                    </div>
                    <h3 className="font-semibold">Secure & Private</h3>
                    <p className="text-sm text-muted-foreground">
                        Your data is isolated and protected with enterprise-grade security
                    </p>
                </div>

                <div className="glass rounded-2xl p-6 space-y-3">
                    <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto">
                        <Rocket className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                    </div>
                    <h3 className="font-semibold">Quick Setup</h3>
                    <p className="text-sm text-muted-foreground">
                        Get started in minutes with our guided setup wizard
                    </p>
                </div>
            </div>

            <div className="glass rounded-xl p-6 text-left space-y-3">
                <h3 className="font-semibold text-lg">What we'll configure:</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        Business information (name, contact details, timezone)
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        API keys for AI and messaging (optional, can add later)
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        Your services and pricing
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                        Business hours and availability
                    </li>
                </ul>
            </div>
        </div>
    );
}
