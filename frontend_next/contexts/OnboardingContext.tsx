"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface OnboardingData {
    // Step 2: Business Details
    businessName: string;
    phone: string;
    email: string;
    address: string;
    timezone: string;

    // Step 3: API Keys
    groqApiKey: string;
    twilioAccountSid: string;
    twilioAuthToken: string;
    twilioPhoneNumber: string;

    // Step 4: Services
    services: Array<{
        name: string;
        duration_minutes: number;
        price: number;
        description?: string;
    }>;

    // Step 5: Business Hours
    businessHours: {
        [key: string]: {
            enabled: boolean;
            open: string;
            close: string;
        };
    };
}

interface OnboardingContextType {
    currentStep: number;
    data: OnboardingData;
    setCurrentStep: (step: number) => void;
    updateData: (updates: Partial<OnboardingData>) => void;
    nextStep: () => void;
    prevStep: () => void;
    resetOnboarding: () => void;
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

const initialData: OnboardingData = {
    businessName: "",
    phone: "",
    email: "",
    address: "",
    timezone: "America/New_York",
    groqApiKey: "",
    twilioAccountSid: "",
    twilioAuthToken: "",
    twilioPhoneNumber: "",
    services: [],
    businessHours: {
        monday: { enabled: true, open: "09:00", close: "17:00" },
        tuesday: { enabled: true, open: "09:00", close: "17:00" },
        wednesday: { enabled: true, open: "09:00", close: "17:00" },
        thursday: { enabled: true, open: "09:00", close: "17:00" },
        friday: { enabled: true, open: "09:00", close: "17:00" },
        saturday: { enabled: true, open: "10:00", close: "16:00" },
        sunday: { enabled: false, open: "10:00", close: "16:00" },
    },
};

export function OnboardingProvider({ children }: { children: ReactNode }) {
    const [currentStep, setCurrentStep] = useState(1);
    const [data, setData] = useState<OnboardingData>(initialData);

    const updateData = (updates: Partial<OnboardingData>) => {
        setData((prev) => ({ ...prev, ...updates }));
    };

    const nextStep = () => {
        setCurrentStep((prev) => Math.min(prev + 1, 6));
    };

    const prevStep = () => {
        setCurrentStep((prev) => Math.max(prev - 1, 1));
    };

    const resetOnboarding = () => {
        setCurrentStep(1);
        setData(initialData);
    };

    return (
        <OnboardingContext.Provider
            value={{
                currentStep,
                data,
                setCurrentStep,
                updateData,
                nextStep,
                prevStep,
                resetOnboarding,
            }}
        >
            {children}
        </OnboardingContext.Provider>
    );
}

export function useOnboarding() {
    const context = useContext(OnboardingContext);
    if (context === undefined) {
        throw new Error("useOnboarding must be used within an OnboardingProvider");
    }
    return context;
}
