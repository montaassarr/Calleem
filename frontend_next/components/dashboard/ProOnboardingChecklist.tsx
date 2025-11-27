"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, Sparkles, ArrowRight, X } from "lucide-react";
import { useConfig } from "@/contexts/ConfigContext";
import { motion, AnimatePresence } from "framer-motion";

interface OnboardingStep {
    id: string;
    title: string;
    description: string;
    action: string;
    link: string;
    completed: boolean;
}

export function ProOnboardingChecklist() {
    const { config } = useConfig();
    const [isVisible, setIsVisible] = useState(true);
    const [steps, setSteps] = useState<OnboardingStep[]>([
        {
            id: "connect_vapi",
            title: "Connect Vapi API",
            description: "Add your Vapi API key to enable voice calls",
            action: "Add API Key",
            link: "/dashboard/settings/integrations",
            completed: false
        },
        {
            id: "setup_automations",
            title: "Enable Smart Automations",
            description: "Turn on Google Calendar, Airtable, or WhatsApp confirmations",
            action: "Configure Automations",
            link: "/dashboard/automations",
            completed: false
        },
        {
            id: "test_voice",
            title: "Test Your AI Voice",
            description: "Make a test call to hear your AI receptionist in action",
            action: "Test Now",
            link: "/dashboard/voice-agent/test",
            completed: false
        },
        {
            id: "customize_prompt",
            title: "Customize AI Personality",
            description: "Edit the system prompt to match your brand voice",
            action: "Customize",
            link: "/dashboard/settings/ai",
            completed: false
        },
        {
            id: "add_services",
            title: "Add Your Services",
            description: "List the services your AI can book appointments for",
            action: "Add Services",
            link: "/dashboard/services",
            completed: false
        }
    ]);

    // Check completion status based on config
    useEffect(() => {
        if (!config) return;

        setSteps(prev => prev.map(step => {
            let completed = false;

            switch (step.id) {
                case "connect_vapi":
                    completed = !!(config as any).vapi_api_key;
                    break;
                case "setup_automations":
                    const automations = (config as any).automations || {};
                    completed = Object.values(automations).some(v => v === true);
                    break;
                case "test_voice":
                    // Could check if user has made any test calls
                    completed = false; // Implement based on your tracking
                    break;
                case "customize_prompt":
                    completed = !!(config as any).system_prompt && (config as any).system_prompt !== "";
                    break;
                case "add_services":
                    // Could check if services exist
                    completed = false; // Implement based on your data
                    break;
            }

            return { ...step, completed };
        }));
    }, [config]);

    const completedCount = steps.filter(s => s.completed).length;
    const totalSteps = steps.length;
    const progress = (completedCount / totalSteps) * 100;
    const isComplete = completedCount === totalSteps;

    // Hide checklist if user has dismissed it or completed all steps
    const shouldShow = isVisible && !isComplete && (config as any)?.plan === "pro";

    if (!shouldShow) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="mb-6"
            >
                <Card className="border-yellow-500/50 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 relative overflow-hidden">
                    {/* Dismiss button */}
                    <button
                        onClick={() => setIsVisible(false)}
                        className="absolute top-4 right-4 p-1 rounded-full hover:bg-white/10 transition-colors z-10"
                    >
                        <X className="w-4 h-4 text-white/60 hover:text-white" />
                    </button>

                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <CardTitle className="text-xl">Welcome to Pro! 🎉</CardTitle>
                                <CardDescription>
                                    Complete these 5 steps to get the most out of Smart Automations
                                </CardDescription>
                            </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="mt-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium text-white/80">
                                    {completedCount} of {totalSteps} completed
                                </span>
                                <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-500 border-yellow-500/30">
                                    {Math.round(progress)}%
                                </Badge>
                            </div>
                            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progress}%` }}
                                    transition={{ duration: 0.5, ease: "easeOut" }}
                                    className="h-full bg-gradient-to-r from-yellow-500 to-orange-500"
                                />
                            </div>
                        </div>
                    </CardHeader>

                    <CardContent>
                        <div className="space-y-3">
                            {steps.map((step, index) => (
                                <motion.div
                                    key={step.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className={`flex items-center justify-between p-4 rounded-lg transition-all ${step.completed
                                            ? "bg-green-500/10 border border-green-500/20"
                                            : "bg-white/5 border border-white/10 hover:border-white/20"
                                        }`}
                                >
                                    <div className="flex items-start gap-3 flex-1">
                                        {step.completed ? (
                                            <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                                        ) : (
                                            <Circle className="w-5 h-5 text-white/40 mt-0.5 flex-shrink-0" />
                                        )}
                                        <div>
                                            <h4 className={`font-medium ${step.completed ? "text-green-500" : "text-white"}`}>
                                                {step.title}
                                            </h4>
                                            <p className="text-sm text-white/60 mt-0.5">
                                                {step.description}
                                            </p>
                                        </div>
                                    </div>
                                    {!step.completed && (
                                        <Button
                                            size="sm"
                                            variant="ghost"
                                            className="ml-4 text-yellow-500 hover:text-yellow-400 hover:bg-yellow-500/10"
                                            onClick={() => window.location.href = step.link}
                                        >
                                            {step.action}
                                            <ArrowRight className="w-4 h-4 ml-1" />
                                        </Button>
                                    )}
                                </motion.div>
                            ))}
                        </div>

                        {/* Estimated time */}
                        <div className="mt-4 p-3 bg-white/5 rounded-lg border border-white/10">
                            <p className="text-sm text-white/60 text-center">
                                ⏱️ Estimated time: <span className="font-medium text-white">5 minutes</span>
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </motion.div>
        </AnimatePresence>
    );
}
