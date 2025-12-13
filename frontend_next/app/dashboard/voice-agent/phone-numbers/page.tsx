"use client";

import { PhoneNumberManager } from "@/components/dashboard/PhoneNumberManager";
import { Separator } from "@/components/ui/separator";

export default function PhoneNumbersPage() {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-medium">Phone Number Management</h3>
                <p className="text-sm text-muted-foreground">
                    Connect your Twilio account or purchase a number (coming soon) to enable voice capabilities.
                </p>
            </div>
            <Separator />

            <div className="max-w-2xl">
                <PhoneNumberManager />
            </div>
        </div>
    );
}
