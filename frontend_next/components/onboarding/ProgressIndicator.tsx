import { CheckCircle2, Circle } from "lucide-react";

interface ProgressIndicatorProps {
    currentStep: number;
    totalSteps: number;
}

const steps = [
    { number: 1, title: "Welcome" },
    { number: 2, title: "Business Details" },
    { number: 3, title: "API Keys" },
    { number: 4, title: "Services" },
    { number: 5, title: "Business Hours" },
    { number: 6, title: "Complete" },
];

export function ProgressIndicator({ currentStep, totalSteps }: ProgressIndicatorProps) {
    return (
        <div className="w-full py-6">
            <div className="flex items-center justify-between max-w-4xl mx-auto">
                {steps.map((step, index) => (
                    <div key={step.number} className="flex items-center flex-1">
                        <div className="flex flex-col items-center flex-1">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all ${step.number < currentStep
                                        ? "bg-primary border-primary text-white"
                                        : step.number === currentStep
                                            ? "border-primary text-primary bg-primary/10"
                                            : "border-gray-300 text-gray-400"
                                    }`}
                            >
                                {step.number < currentStep ? (
                                    <CheckCircle2 className="w-5 h-5" />
                                ) : (
                                    <Circle className="w-5 h-5" />
                                )}
                            </div>
                            <p
                                className={`text-xs mt-2 font-medium ${step.number <= currentStep ? "text-foreground" : "text-muted-foreground"
                                    }`}
                            >
                                {step.title}
                            </p>
                        </div>
                        {index < steps.length - 1 && (
                            <div
                                className={`h-0.5 flex-1 mx-2 transition-all ${step.number < currentStep ? "bg-primary" : "bg-gray-300"
                                    }`}
                            />
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
