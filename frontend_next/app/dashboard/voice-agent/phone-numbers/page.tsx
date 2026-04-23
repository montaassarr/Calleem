"use client";

import { PhoneNumberManager } from "@/components/dashboard/PhoneNumberManager";

export default function PhoneNumbersPage() {
    return (
        <div>
            <div className="mb-8">
                <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Phone Number Management</h1>
                <p className="text-[14px] text-gray-500 font-medium">
                    Connect your Twilio account or purchase a number to enable voice capabilities.
                </p>
            </div>
            <div className="max-w-2xl">
                <PhoneNumberManager />
            </div>
        </div>
    );
}
