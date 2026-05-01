"use client";

import { Building, Bot, Clock } from "lucide-react";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
    const router = useRouter();

    const sections = [
        { title: "Business Profile", description: "Manage your business information and contact details", icon: Building, path: "/dashboard/settings/business", color: "from-blue-500 to-cyan-500" },
        { title: "AI Configuration", description: "Configure AI Voice Assistant (Vapi)", icon: Bot, path: "/dashboard/settings/ai", color: "from-[#187848] to-[#0a4c2f]" },
        { title: "Business Hours", description: "Set your weekly operating hours and schedule", icon: Clock, path: "/dashboard/settings/hours", color: "from-amber-500 to-yellow-500" },
    ];

    return (
        <div>
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Settings</h1>
                <p className="text-[14px] text-gray-500 font-medium">Configure your AI receptionist and business settings.</p>
            </div>

            {/* Settings Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sections.map((section) => (
                    <div
                        key={section.path}
                        onClick={() => router.push(section.path)}
                        className="bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6 hover:shadow-md transition-all cursor-pointer group"
                    >
                        <div className="flex items-start gap-4">
                            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${section.color} flex items-center justify-center group-hover:scale-110 transition-transform shrink-0`}>
                                <section.icon className="w-6 h-6 text-white" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <h3 className="font-bold text-gray-900 mb-1">{section.title}</h3>
                                <p className="text-sm text-gray-500">{section.description}</p>
                            </div>
                            <div className="text-gray-400 group-hover:translate-x-1 transition-transform text-lg">→</div>
                        </div>
                    </div>
                ))}
            </div>

            {/* System Info */}
            <div className="mt-6 bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                <h3 className="font-bold text-gray-900 mb-4">System Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        { label: "Version", value: "1.0.0" },
                        { label: "Last Updated", value: new Date().toLocaleDateString() },
                        { label: "Environment", value: "Development" },
                    ].map((info) => (
                        <div key={info.label} className="bg-gray-50 rounded-xl p-3">
                            <p className="text-[11px] text-gray-400 font-medium uppercase tracking-wide mb-1">{info.label}</p>
                            <p className="font-bold text-gray-900 text-sm">{info.value}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
