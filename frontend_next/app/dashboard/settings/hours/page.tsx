"use client";

import { Save, ArrowLeft, RefreshCw, AlertCircle, Clock } from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useConfig } from "@/hooks/use-config";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";

interface DayHours {
    day_of_week: number;
    open_time: string;
    close_time: string;
    is_open: boolean;
}

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
const DAY_LABELS: Record<string, string> = {
    monday: 'Monday', tuesday: 'Tuesday', wednesday: 'Wednesday',
    thursday: 'Thursday', friday: 'Friday', saturday: 'Saturday', sunday: 'Sunday',
};

export default function HoursSettingsPage() {
    const router = useRouter();
    const { config, isLoading, error, updateConfig, isUpdating, reloadConfig, isReloading } = useConfig();

    const [hours, setHours] = useState<DayHours[]>(
        DAYS.map((_, index) => ({ day_of_week: index, open_time: '09:00', close_time: '18:00', is_open: true }))
    );

    useEffect(() => {
        if (config?.business_hours) {
            setHours(DAYS.map((day, index) => {
                const dayConfig = config.business_hours[day];
                return {
                    day_of_week: index,
                    open_time: dayConfig?.start || '09:00',
                    close_time: dayConfig?.end || '17:00',
                    is_open: dayConfig?.enabled ?? false
                };
            }));
        }
    }, [config]);

    const handleSave = () => {
        const business_hours: any = {};
        hours.forEach(h => {
            const dayName = DAYS[h.day_of_week];
            business_hours[dayName] = { start: h.open_time, end: h.close_time, enabled: h.is_open };
        });
        updateConfig({ business_hours }, {
            onSuccess: () => toast.success("Business hours updated successfully"),
            onError: () => toast.error("Failed to update business hours"),
        });
    };

    const updateDay = (dayOfWeek: number, field: keyof DayHours, value: any) => {
        setHours(hours.map(h => h.day_of_week === dayOfWeek ? { ...h, [field]: value } : h));
    };

    const copyToAll = (sourceDayOfWeek: number) => {
        const source = hours.find(h => h.day_of_week === sourceDayOfWeek);
        if (source) {
            setHours(hours.map(h => ({ ...h, open_time: source.open_time, close_time: source.close_time, is_open: source.is_open })));
        }
    };

    return (
        <div>
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    <button onClick={() => router.push('/dashboard/settings')} className="p-2 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors">
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Business Hours</h1>
                        <p className="text-[14px] text-gray-500 font-medium">Set your operating hours for each day of the week.</p>
                    </div>
                </div>
                <button onClick={() => reloadConfig()} disabled={isReloading} className="p-2.5 bg-white border border-gray-200 text-gray-700 rounded-full hover:bg-gray-50 transition-colors shadow-sm">
                    <RefreshCw className={`w-4 h-4 ${isReloading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {/* Error Alert */}
            {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 max-w-4xl">
                    <AlertCircle className="h-4 w-4 text-red-600 shrink-0" />
                    <p className="text-sm text-red-700">Failed to load business hours configuration. Please try again.</p>
                </div>
            )}

            {/* Hours Configuration */}
            <div className="max-w-4xl space-y-3 mb-6">
                {isLoading ? (
                    DAYS.map(day => <div key={day} className="h-24 bg-gray-100 rounded-[20px] animate-pulse" />)
                ) : (
                    hours.map((dayHours, index) => (
                        <div key={dayHours.day_of_week} className="bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-5">
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="font-bold text-gray-900 flex items-center gap-2">
                                    <Clock className="w-4 h-4 text-gray-400" />
                                    {DAY_LABELS[DAYS[index]]}
                                </h3>
                                <div className="flex items-center gap-4">
                                    <div className="flex items-center gap-2">
                                        <Switch
                                            checked={dayHours.is_open}
                                            onCheckedChange={(checked) => updateDay(dayHours.day_of_week, 'is_open', checked)}
                                            disabled={isUpdating}
                                        />
                                        <span className={`text-sm font-medium min-w-[50px] ${dayHours.is_open ? 'text-green-700' : 'text-gray-400'}`}>
                                            {dayHours.is_open ? 'Open' : 'Closed'}
                                        </span>
                                    </div>
                                    <button
                                        onClick={() => copyToAll(dayHours.day_of_week)}
                                        disabled={isUpdating}
                                        className="text-xs text-gray-500 hover:text-gray-700 font-medium transition-colors"
                                    >
                                        Copy to All
                                    </button>
                                </div>
                            </div>
                            {dayHours.is_open ? (
                                <div className="grid grid-cols-2 gap-4">
                                    {[
                                        { label: "Opening Time", field: "open_time" as const },
                                        { label: "Closing Time", field: "close_time" as const },
                                    ].map((time) => (
                                        <div key={time.field}>
                                            <label className="text-xs text-gray-400 font-medium">{time.label}</label>
                                            <input
                                                type="time"
                                                value={(dayHours as any)[time.field]}
                                                onChange={(e) => updateDay(dayHours.day_of_week, time.field, e.target.value)}
                                                disabled={isUpdating}
                                                className="w-full mt-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                                            />
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-gray-400 italic">Business is closed on this day</p>
                            )}
                        </div>
                    ))
                )}
            </div>

            {/* Quick Actions */}
            <div className="max-w-4xl bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-5 mb-6">
                <h3 className="font-bold text-gray-900 mb-3 text-sm">Quick Actions</h3>
                <div className="flex gap-2 flex-wrap">
                    {[
                        { label: "Standard Hours (9–5)", action: () => setHours(hours.map(h => ({ ...h, open_time: '09:00', close_time: '17:00', is_open: true }))) },
                        { label: "Extended Hours (8–8)", action: () => setHours(hours.map(h => ({ ...h, open_time: '08:00', close_time: '20:00', is_open: true }))) },
                        { label: "Weekdays Only", action: () => setHours(hours.map(h => ({ ...h, is_open: h.day_of_week < 5 }))) },
                        { label: "Open All Week", action: () => setHours(hours.map(h => ({ ...h, is_open: true }))) },
                    ].map((btn) => (
                        <button key={btn.label} onClick={btn.action} disabled={isUpdating} className="px-3 py-1.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-xs">
                            {btn.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Save */}
            <div className="max-w-4xl flex gap-3">
                <button onClick={handleSave} disabled={isUpdating || isLoading} className="px-5 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-[20px] font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] flex items-center gap-2 relative overflow-hidden disabled:opacity-50">
                    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                    {isUpdating ? <RefreshCw className="w-4 h-4 animate-spin relative z-10" /> : <Save className="w-4 h-4 relative z-10" />}
                    <span className="relative z-10">{isUpdating ? "Saving..." : "Save Business Hours"}</span>
                </button>
                <button onClick={() => router.push('/dashboard/settings')} disabled={isUpdating} className="px-5 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-[20px] font-semibold hover:bg-gray-50 transition-colors">
                    Cancel
                </button>
            </div>

            {/* Tip */}
            <div className="max-w-4xl mt-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                <p className="text-sm text-blue-700">
                    💡 <strong>Tip:</strong> The AI receptionist will use these hours to inform customers about availability and prevent bookings outside business hours.
                </p>
            </div>
        </div>
    );
}
