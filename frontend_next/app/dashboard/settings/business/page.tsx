"use client";

import { Save, ArrowLeft, RefreshCw, AlertCircle } from "lucide-react";
import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useConfig } from "@/hooks/use-config";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export default function BusinessSettingsPage() {
    const router = useRouter();
    const { user, isAuthenticated } = useAuth();
    const tenantId = user?.tenant_id || user?.business_id || "default";
    const { config, isLoading, error, updateConfig, isUpdating, reloadConfig, isReloading } = useConfig(tenantId, isAuthenticated && !!tenantId);

    const [formData, setFormData] = useState({
        business_name: "",
        business_email: "",
        business_phone: "",
        business_location: "",
        business_address: "",
        timezone: "America/New_York",
    });

    useEffect(() => {
        if (config) {
            setFormData({
                business_name: config.business_name || "",
                business_email: config.business_email || "",
                business_phone: config.business_phone || "",
                business_location: config.business_location || "",
                business_address: config.business_address || "",
                timezone: config.timezone || "America/New_York",
            });
        }
    }, [config]);

    const handleSave = () => {
        updateConfig(formData, {
            onSuccess: () => toast.success("Business profile updated successfully"),
            onError: () => toast.error("Failed to update business profile"),
        });
    };

    const timezoneOptions = useMemo(() => {
        const intlAny = Intl as any;
        const timezones = typeof Intl !== "undefined" && typeof intlAny.supportedValuesOf === "function"
            ? intlAny.supportedValuesOf("timeZone")
            : ["UTC", "America/New_York", "Europe/London", "Europe/Paris", "Asia/Dubai"];

        const now = new Date();

        const formatOffset = (timezone: string) => {
            const tzPart = new Intl.DateTimeFormat("en-US", {
                timeZone: timezone,
                timeZoneName: "shortOffset",
            }).formatToParts(now).find((p) => p.type === "timeZoneName")?.value || "GMT+00:00";
            return tzPart;
        };

        const placeLabel = (timezone: string) => {
            const [region, city] = timezone.split("/");
            if (!city) return timezone;
            return `${city.replace(/_/g, " ")}, ${region.replace(/_/g, " ")}`;
        };

        return timezones.map((tz) => ({
            value: tz,
            label: `(${formatOffset(tz)}) ${placeLabel(tz)} - ${tz}`,
        }));
    }, []);

    const fields = [
        { id: "business_name", label: "Business Name *", placeholder: "Enter your business name", type: "text" },
        { id: "business_email", label: "Email", placeholder: "contact@business.com", type: "email" },
        { id: "business_phone", label: "Phone", placeholder: "+1 555 123 4567", type: "tel", hint: "Public phone number callers can reach you on (used by the AI when asked)." },
        { id: "business_location", label: "City / Area", placeholder: "e.g. Downtown Tunis, Florida, Manhattan", type: "text", hint: "Broad area or city the AI mentions when callers ask where you're located." },
        { id: "business_address", label: "Street Address", placeholder: "e.g. Rue El Mourouj, 123 Main St", type: "textarea", hint: "Exact street address the AI gives for directions or shipping." },
        { id: "timezone", label: "Timezone *", placeholder: "America/New_York", type: "select", hint: "Select your local timezone. AI uses this for current date/time and relative dates (today/tomorrow)." },
    ];

    return (
        <div>
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    <button onClick={() => router.push('/dashboard/settings')} className="p-2 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors">
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Business Profile</h1>
                        <p className="text-[14px] text-gray-500 font-medium">Manage your business information and operating hours.</p>
                    </div>
                </div>
                <button onClick={() => reloadConfig()} disabled={isReloading} className="p-2.5 bg-white border border-gray-200 text-gray-700 rounded-full hover:bg-gray-50 transition-colors shadow-sm">
                    <RefreshCw className={`w-4 h-4 ${isReloading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {/* Error Alert */}
            {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3">
                    <AlertCircle className="h-4 w-4 text-red-600 shrink-0" />
                    <p className="text-sm text-red-700">Failed to load configuration. Please try again.</p>
                </div>
            )}

            {/* Form */}
            <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                {isLoading ? (
                    <div className="space-y-6">
                        {[1, 2, 3, 4].map(i => <div key={i} className="h-20 bg-gray-100 rounded-xl animate-pulse" />)}
                    </div>
                ) : (
                    <div className="space-y-5">
                        {fields.map((field) => (
                            <div key={field.id} className="space-y-2">
                                <label htmlFor={field.id} className="text-sm font-semibold text-gray-700">{field.label}</label>
                                {field.type === "textarea" ? (
                                    <textarea
                                        id={field.id}
                                        value={(formData as any)[field.id]}
                                        onChange={(e) => setFormData({ ...formData, [field.id]: e.target.value })}
                                        placeholder={field.placeholder}
                                        rows={3}
                                        className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all resize-none"
                                    />
                                ) : field.type === "select" ? (
                                    <select
                                        id={field.id}
                                        value={(formData as any)[field.id]}
                                        onChange={(e) => setFormData({ ...formData, [field.id]: e.target.value })}
                                        className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                                    >
                                        {timezoneOptions.map((timezone) => (
                                            <option key={timezone.value} value={timezone.value}>
                                                {timezone.label}
                                            </option>
                                        ))}
                                    </select>
                                ) : (
                                    <input
                                        id={field.id}
                                        type={field.type}
                                        value={(formData as any)[field.id]}
                                        onChange={(e) => setFormData({ ...formData, [field.id]: e.target.value })}
                                        placeholder={field.placeholder}
                                        className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                                    />
                                )}
                                {field.hint && <p className="text-xs text-gray-400">{field.hint}</p>}
                            </div>
                        ))}

                        <div className="flex gap-3 pt-4">
                            <button
                                onClick={handleSave}
                                disabled={isUpdating || !formData.business_name}
                                className="px-5 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-[20px] font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] flex items-center gap-2 relative overflow-hidden disabled:opacity-50"
                            >
                                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                                {isUpdating ? <RefreshCw className="w-4 h-4 animate-spin relative z-10" /> : <Save className="w-4 h-4 relative z-10" />}
                                <span className="relative z-10">{isUpdating ? "Saving..." : "Save Changes"}</span>
                            </button>
                            <button onClick={() => router.push('/dashboard/settings')} disabled={isUpdating} className="px-5 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-[20px] font-semibold hover:bg-gray-50 transition-colors">
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
