"use client";

import { Phone } from "lucide-react";

export default function BuyPhoneNumberPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <button onClick={() => window.history.back()} className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center gap-2">
        ← Back
      </button>

      <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100">
          <h3 className="font-bold text-lg text-gray-900">Phone Number Provisioning</h3>
        </div>
        <div className="text-center py-16 px-6">
          <div className="mx-auto w-16 h-16 rounded-full bg-[#0a4c2f]/10 flex items-center justify-center mb-4">
            <Phone className="w-7 h-7 text-[#0a4c2f]" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Coming Soon</h2>
          <p className="text-gray-500 mb-6 max-w-sm mx-auto">
            Direct phone number purchasing via Vapi is being integrated.
            Please contact support to provision a number manually for now.
          </p>
          <button
            onClick={() => window.open('mailto:support@callflow.ai')}
            className="px-6 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-xl font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
            <span className="relative z-10">Contact Support</span>
          </button>
        </div>
      </div>
    </div>
  );
}
