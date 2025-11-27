"use client";

import { useState } from "react";
import { OnboardingProvider, useOnboarding } from "@/contexts/OnboardingContext";
import { ProgressIndicator } from "@/components/onboarding/ProgressIndicator";
import { StepNavigation } from "@/components/onboarding/StepNavigation";
import { WelcomeStep } from "@/components/onboarding/WelcomeStep";
import { BusinessDetailsStep } from "@/components/onboarding/BusinessDetailsStep";
import { ApiKeysStep } from "@/components/onboarding/ApiKeysStep";
import { ServicesStep } from "@/components/onboarding/ServicesStep";
import { BusinessHoursStep } from "@/components/onboarding/BusinessHoursStep";
import { CompleteStep } from "@/components/onboarding/CompleteStep";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { businessConfigApi } from "@/lib/api-endpoints";
import { servicesApi } from "@/lib/api-endpoints";
import { adminApi } from "@/lib/api/admin";
import { useAuth } from "@/contexts/AuthContext";

function OnboardingWizard() {
    const { currentStep, data, nextStep, prevStep, setCurrentStep } = useOnboarding();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const router = useRouter();
    const { user } = useAuth();

    const renderStep = () => {
        switch (currentStep) {
            case 1:
                return <WelcomeStep />;
            case 2:
                return <BusinessDetailsStep />;
            case 3:
                return <ApiKeysStep />;
            case 4:
                return <ServicesStep />;
            case 5:
                return <BusinessHoursStep />;
            case 6:
                return <CompleteStep />;
            default:
                return <WelcomeStep />;
        }
    };

    const canProceed = () => {
        switch (currentStep) {
            case 1:
                return true; // Welcome step
            case 2:
                return data.businessName && data.phone && data.email && data.timezone;
            case 3:
                return true; // API keys are optional
            case 4:
                return data.services.length > 0 && data.services.every(s => s.name && s.duration_minutes && s.price >= 0);
            case 5:
                return true; // Business hours have defaults
            case 6:
                return true; // Complete step
            default:
                return false;
        }
    };

    const handleNext = () => {
        if (canProceed()) {
            nextStep();
        } else {
            toast.error("Please fill in all required fields");
        }
    };

    const handleSkip = () => {
        // Only API keys step is skippable
        if (currentStep === 3) {
            nextStep();
        }
    };

    const handleFinish = async () => {
        try {
            setIsSubmitting(true);

            // 1. Update business config
            const configData = {
                business_name: data.businessName,
                phone_number: data.phone,
                email: data.email,
                address: data.address,
                timezone: data.timezone,
                groq_api_key: data.groqApiKey || undefined,
                twilio_account_sid: data.twilioAccountSid || undefined,
                twilio_auth_token: data.twilioAuthToken || undefined,
                twilio_phone_number: data.twilioPhoneNumber || undefined,
            };

            // Since updateConfig doesn't exist in api-endpoints, use admin API
            await adminApi.updateConfig(configData);

            // 2. Create services
            for (const service of data.services) {
                await servicesApi.create({
                    name: service.name,
                    duration_minutes: service.duration_minutes,
                    price: service.price,
                    description: service.description || "",
                    active: true,
                });
            }

            // 3. Save business hours (would need a dedicated endpoint, for now skip or add to config)
            // TODO: Add business hours endpoint

            // 4. Mark tenant as configured
            if (user?.tenant_id) {
                await adminApi.updateTenant(user.tenant_id, { is_configured: true });
            }

            toast.success("Setup complete! Welcome to your dashboard 🎉");

            // Redirect to dashboard
            setTimeout(() => {
                router.push("/dashboard");
            }, 1000);
        } catch (error: any) {
            console.error("Onboarding error:", error);
            toast.error(error.response?.data?.detail || "Failed to complete setup. Please try again.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
            <div className="container mx-auto px-4 py-8">
                <ProgressIndicator currentStep={currentStep} totalSteps={6} />

                <div className="mt-8 mb-8">
                    {renderStep()}
                </div>

                <div className="max-w-2xl mx-auto">
                    <StepNavigation
                        currentStep={currentStep}
                        totalSteps={6}
                        onNext={handleNext}
                        onPrev={prevStep}
                        onSkip={handleSkip}
                        onFinish={handleFinish}
                        canProceed={canProceed()}
                        isSkippable={currentStep === 3}
                        isSubmitting={isSubmitting}
                    />
                </div>
            </div>
        </div>
    );
}

export default function OnboardingPage() {
    return (
        <OnboardingProvider>
            <OnboardingWizard />
        </OnboardingProvider>
    );
}
