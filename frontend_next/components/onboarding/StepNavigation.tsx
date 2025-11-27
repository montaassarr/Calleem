import { Button } from "@/components/ui/button";
import { ArrowLeft, ArrowRight } from "lucide-react";

interface StepNavigationProps {
    currentStep: number;
    totalSteps: number;
    onNext: () => void;
    onPrev: () => void;
    onSkip?: () => void;
    onFinish?: () => void;
    canProceed?: boolean;
    isSkippable?: boolean;
    isSubmitting?: boolean;
}

export function StepNavigation({
    currentStep,
    totalSteps,
    onNext,
    onPrev,
    onSkip,
    onFinish,
    canProceed = true,
    isSkippable = false,
    isSubmitting = false,
}: StepNavigationProps) {
    const isFirstStep = currentStep === 1;
    const isLastStep = currentStep === totalSteps;

    return (
        <div className="flex items-center justify-between pt-6 border-t">
            <Button
                variant="outline"
                onClick={onPrev}
                disabled={isFirstStep || isSubmitting}
            >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
            </Button>

            <div className="flex gap-2">
                {isSkippable && !isLastStep && (
                    <Button
                        variant="ghost"
                        onClick={onSkip}
                        disabled={isSubmitting}
                    >
                        Skip
                    </Button>
                )}

                {isLastStep ? (
                    <Button
                        onClick={onFinish}
                        disabled={!canProceed || isSubmitting}
                        className="bg-gradient-to-r from-primary to-accent"
                    >
                        {isSubmitting ? "Saving..." : "Finish Setup"}
                    </Button>
                ) : (
                    <Button
                        onClick={onNext}
                        disabled={!canProceed || isSubmitting}
                    >
                        Next
                        <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                )}
            </div>
        </div>
    );
}
