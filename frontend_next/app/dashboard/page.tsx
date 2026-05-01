"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTenant } from "@/contexts/TenantContext";
import { useDashboardStats } from "@/hooks/domain/useDashboardStats";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/contexts/AuthContext";
import { conversationsApi, phoneApi } from "@/lib/api-endpoints";
import {
    ArrowUpRight,
    ChevronDown,
    User,
    Sparkles,
    Scissors,
    SprayCan,
    Phone,
    Pause,
    Square,
    Mic,
} from "lucide-react";

/* ─────────────── KPI Cards ─────────────── */
function KPICards({ metrics, conversations, isLoading }: any) {
    const cards = [
        {
            title: "Revenue",
            value: "$24.5k",
            subtext: "+15% from last month",
            isActive: true,
            badgeText: "15%+",
        },
        {
            title: "Total Appointments",
            value: isLoading ? "..." : (metrics?.totalAppointments ?? 0).toString(),
            subtext: "All time bookings",
            isActive: false,
            hideBadge: true,
        },
        {
            title: "Upcoming",
            value: isLoading ? "..." : (metrics?.upcomingAppointments ?? 0).toString(),
            subtext: "Scheduled ahead",
            isActive: false,
            hideBadge: true,
        },
        {
            title: "Conversations",
            value: isLoading ? "..." : (conversations?.length ?? 0).toString(),
            subtext: "Active dialogues",
            isActive: false,
            hideBadge: true,
        },
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-2 xl:grid-cols-4 gap-3 md:gap-5">
            {cards.map((card, i) => (
                <div
                    key={i}
                    className={`p-4 md:p-6 rounded-[20px] md:rounded-[24px] relative flex flex-col justify-between h-full min-h-[140px] md:min-h-[180px] overflow-hidden ${card.isActive
                        ? "bg-gradient-to-br from-[#187848] via-[#0a4c2f] to-[#052b19] border border-[#1b8550]/20 text-white shadow-xl shadow-[#0a4c2f]/30"
                        : "bg-white text-gray-900 shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100"
                        }`}
                >
                    {card.isActive && (
                        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-white/10 via-transparent to-transparent pointer-events-none"></div>
                    )}
                    <div className="flex justify-between items-start mb-2 md:mb-4 relative z-10 gap-2">
                        <h3
                            className={`font-semibold text-[13px] md:text-base leading-tight ${card.isActive ? "text-white/95" : "text-gray-900"
                                }`}
                        >
                            {card.title}
                        </h3>
                        <div
                            className={`w-7 h-7 md:w-8 md:h-8 rounded-full flex items-center justify-center border shrink-0 ${card.isActive
                                ? "border-white bg-white text-[#0a4c2f]"
                                : "border-gray-300 text-gray-900 bg-white"
                                }`}
                        >
                            <ArrowUpRight className="w-3 h-3 md:w-4 md:h-4 stroke-[2.5px]" />
                        </div>
                    </div>

                    <div className="flex flex-col gap-1 md:gap-2 mt-auto">
                        <div
                            className={`text-[28px] md:text-[42px] font-bold leading-none tracking-tight ${card.isActive ? "text-white" : "text-gray-900"
                                }`}
                        >
                            {card.value}
                        </div>
                        <div className="flex flex-wrap items-center gap-1 md:gap-2 mt-1 md:mt-0">
                            {!card.hideBadge && (
                                <span
                                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold flex items-center justify-center min-w-[24px] ${card.isActive
                                        ? "bg-white text-[#0a4c2f]"
                                        : "bg-transparent text-gray-500 border border-gray-300"
                                        }`}
                                >
                                    {card.badgeText}
                                </span>
                            )}
                            <span
                                className={`text-[10px] md:text-[11px] font-semibold leading-none md:leading-normal opacity-80 md:opacity-100 ${card.isActive ? "text-[#8abfa7]" : "text-gray-500"
                                    }`}
                            >
                                {card.subtext}
                            </span>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}

/* ─────────────── Project Analytics ─────────────── */
function ProjectAnalytics() {
    const [timeRange, setTimeRange] = useState<"7days" | "1month" | "all">("1month");

    const datasets: Record<string, { label: string; type: string; height: number; hasTooltip?: boolean }[]> = {
        "7days": [
            { label: "S", type: "striped", height: 45 },
            { label: "M", type: "solid-dark", height: 85 },
            { label: "T", type: "solid-light", height: 74, hasTooltip: true },
            { label: "W", type: "solid-dark", height: 95 },
            { label: "T", type: "striped", height: 50 },
            { label: "F", type: "striped", height: 45 },
            { label: "S", type: "striped", height: 35 },
        ],
        "1month": [
            { label: "W1", type: "striped", height: 50 },
            { label: "W2", type: "solid-dark", height: 88, hasTooltip: true },
            { label: "W3", type: "solid-light", height: 65 },
            { label: "W4", type: "solid-dark", height: 92 },
        ],
        all: [
            { label: "Q1", type: "striped", height: 40 },
            { label: "Q2", type: "solid-light", height: 62 },
            { label: "Q3", type: "solid-dark", height: 85 },
            { label: "Q4", type: "solid-dark", height: 95, hasTooltip: true },
        ],
    };

    const data = datasets[timeRange];

    return (
        <div className="bg-white p-6 rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 flex flex-col justify-between h-full min-h-[320px]">
            <div className="flex justify-between items-center relative">
                <h3 className="font-semibold text-lg text-gray-900">Project Analytics</h3>
                <div className="relative">
                    <select
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value as any)}
                        className="appearance-none bg-transparent border border-gray-200 text-gray-700 text-[11px] font-bold tracking-wide rounded-full pl-3 pr-7 py-1.5 focus:outline-none focus:bg-gray-50 focus:ring-1 focus:ring-gray-200 cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                        <option value="7days">Last 7 days</option>
                        <option value="1month">Last month</option>
                        <option value="all">All time</option>
                    </select>
                    <ChevronDown className="w-3.5 h-3.5 text-gray-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                </div>
            </div>

            <div className="flex-1 flex items-end justify-between px-2 pb-2 mt-4 relative min-h-[150px]">
                {data.map((item, i) => (
                    <div key={i} className="flex flex-col items-center gap-3 cursor-pointer group h-full justify-end flex-1">
                        <div className="relative w-full max-w-[48px] flex items-end justify-center h-full">
                            {item.hasTooltip && (
                                <div className="absolute -top-9 bg-white border border-gray-100 shadow-md text-[10px] font-bold text-gray-700 px-2.5 py-1 rounded-md tracking-wide z-10 whitespace-nowrap">
                                    {item.height}%
                                    <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-white border-b border-r border-gray-100 rotate-45 rounded-sm"></div>
                                </div>
                            )}
                            <div
                                style={{ height: `${item.height}%` }}
                                className={`w-full rounded-full transition-all duration-300 group-hover:opacity-90 ${item.type === "solid-dark"
                                    ? "bg-[#0a4c2f]"
                                    : item.type === "solid-light"
                                        ? "bg-[#48a074]"
                                        : "bg-striped border border-gray-200"
                                    }`}
                            ></div>
                        </div>
                        <span className="text-[13px] font-semibold text-gray-400">{item.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

/* ─────────────── Appointments Timeline ─────────────── */
function AppointmentsTimeline({ appointments }: { appointments: any[] }) {
    const startHour = 8;
    const endHour = 18;
    const times = Array.from({ length: endHour - startHour + 1 }, (_, i) => `${(startHour + i).toString().padStart(2, '0')}:00`);

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const todaysAppointments = (appointments || []).filter(app => {
        const d = new Date(app.datetime);
        return d >= today && d < tomorrow;
    });

    const PALETTE = [
        { bg: "bg-[#b6f09c]/40", text: "text-[#0a4c2f]", iconBg: "bg-[#0a4c2f] text-white", border: "border-[#0a4c2f]" },
        { bg: "bg-blue-100", text: "text-blue-800", iconBg: "bg-blue-600 text-white", border: "border-blue-600" },
        { bg: "bg-orange-100", text: "text-orange-800", iconBg: "bg-orange-600 text-white", border: "border-orange-600" },
        { bg: "bg-purple-100", text: "text-purple-800", iconBg: "bg-purple-600 text-white", border: "border-purple-600" },
        { bg: "bg-rose-100", text: "text-rose-800", iconBg: "bg-rose-600 text-white", border: "border-rose-600" },
        { bg: "bg-amber-100", text: "text-amber-800", iconBg: "bg-amber-600 text-white", border: "border-amber-600" },
    ];

    const uniqueServices = Array.from(new Set(todaysAppointments.map(a => a.service || "Standard Service")));
    if (uniqueServices.length === 0) uniqueServices.push("Standard Service");

    const serviceColors = Object.fromEntries(
        uniqueServices.map((service, index) => [service, PALETTE[index % PALETTE.length]])
    );

    const mappedAppointments = todaysAppointments.map(app => {
        const date = new Date(app.datetime);
        const hour = date.getHours();
        const minute = date.getMinutes();

        let timeIndex = hour - startHour;
        if (timeIndex < 0) timeIndex = 0;

        const serviceName = app.service || "Standard Service";
        const palette = serviceColors[serviceName];

        let icon = <Scissors className="w-3.5 h-3.5" />;
        if (serviceName.toLowerCase().includes("consult")) icon = <User className="w-3.5 h-3.5" />;
        else if (serviceName.toLowerCase().includes("color") || serviceName.toLowerCase().includes("treatment")) icon = <Sparkles className="w-3.5 h-3.5" />;

        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        const displayMin = minute.toString().padStart(2, '0');
        const timeStr = `${displayHour}:${displayMin} ${ampm}`;
        const clientName = app.client_name?.split(' ')[0] || 'Client';

        return {
            timeIndex,
            startOffset: minute,
            duration: app.duration_minutes || 30,
            color: palette.bg,
            textColor: palette.text,
            border: palette.border,
            icon,
            clientName,
            serviceName,
            timeStr,
            label: `${timeStr} | ${clientName} (${serviceName})`,
            iconBg: palette.iconBg,
            status: app.status
        };
    }).filter(app => app.timeIndex >= 0 && app.timeIndex < times.length);

    const PIXELS_PER_HOUR = 60; // 1 min = 1px representation for the Y-Axis

    return (
        <div className="bg-white p-6 rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 flex flex-col h-full min-h-[420px]">
            <div className="flex justify-between items-center mb-4 shrink-0 relative z-10 w-full">
                <h3 className="font-semibold text-lg text-gray-900 uppercase tracking-tight">Today's Appointments</h3>
                <button
                    onClick={() => window.location.href = "/dashboard/schedule"}
                    className="text-[11px] font-bold border border-gray-200 px-3 py-1.5 rounded-full hover:bg-gray-50 text-gray-700 transition-colors flex items-center gap-1 cursor-pointer"
                >
                    Full Calendar
                </button>
            </div>

            <div className="relative flex-1 overflow-y-auto pr-2 min-h-[300px] max-h-[400px] border-t border-b border-gray-50 my-2">
                <div className="relative" style={{ height: `${times.length * PIXELS_PER_HOUR}px` }}>
                    {/* Y-Axis Time Markers & Horizontal Grid Lines */}
                    {times.map((time, idx) => (
                        <div key={idx} className="absolute w-full flex items-start" style={{ top: `${idx * PIXELS_PER_HOUR}px`, height: `${PIXELS_PER_HOUR}px` }}>
                            <span className="w-12 text-[10px] font-bold text-gray-400 text-right pr-3 -mt-2">{time}</span>
                            <div className="flex-1 border-t border-gray-100"></div>
                        </div>
                    ))}

                    {/* Appointment Vertical Blocks */}
                    <div className="absolute top-0 bottom-0 left-14 right-2">
                        {mappedAppointments.map((app, appIdx) => {
                            const topPos = (app.timeIndex * PIXELS_PER_HOUR) + app.startOffset;
                            const height = Math.max(app.duration, 24); // Ensure blocks are tall enough to click/read
                            
                            return (
                                <div
                                    key={appIdx}
                                    className={`absolute left-0 right-0 rounded-lg p-2 shadow-sm transition-transform hover:scale-[1.01] cursor-pointer overflow-hidden border-l-4 ${app.color} ${app.border} ${app.status === 'cancelled' ? 'opacity-50 grayscale' : ''}`}
                                    style={{ 
                                        top: `${topPos}px`, 
                                        height: `${height}px`, 
                                        zIndex: 10 + appIdx 
                                    }}
                                    title={app.label}
                                >
                                    <div className="flex items-start gap-2 h-full">
                                        <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 shadow-sm ${app.iconBg}`}>
                                            {app.icon}
                                        </div>
                                        <div className="flex flex-col overflow-hidden leading-tight justify-center">
                                            <span className={`text-[12px] font-bold truncate ${app.textColor}`}>
                                                {app.timeStr} - {app.clientName}
                                            </span>
                                            {height >= 40 && (
                                                <span className={`text-[10px] font-medium truncate opacity-90 ${app.textColor} mt-0.5`}>
                                                    {app.serviceName}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Dynamic Legend Footer synchronized with Services */}
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 md:gap-6 mt-2 pt-2 shrink-0">
                {uniqueServices.map(srv => (
                    <div key={srv} className="flex items-center gap-1.5 md:gap-2">
                        <div className={`w-2.5 h-2.5 md:w-3 md:h-3 rounded-full border-2 ${serviceColors[srv].border} ${serviceColors[srv].bg.split('/')[0]}`}></div>
                        <span className="text-[10px] md:text-[12px] font-bold text-gray-500 truncate max-w-[120px] capitalize">{srv}</span>
                    </div>
                ))}
                <div className="ml-auto text-[10px] md:text-[12px] font-bold text-[#0a4c2f] w-full sm:w-auto text-right sm:text-left mt-1 sm:mt-0 bg-[#0a4c2f]/5 px-2 py-1 rounded-md">
                    {todaysAppointments.length} Today
                </div>
            </div>
        </div>
    );
}

/* ─────────────── Recent AI Calls ─────────────── */
function RecentVoiceCalls() {
    const { data: callsData, isLoading } = useQuery({
        queryKey: ["recent-calls"],
        queryFn: () => conversationsApi.list({ limit: 4 }),
    });

    const calls = Array.isArray(callsData) ? callsData : (callsData as any)?.items || [];

    const getStatusCol = (status: string) => {
        switch (status) {
            case "completed": return "text-emerald-700 bg-emerald-100";
            case "in-progress": return "text-amber-700 bg-amber-100";
            case "failed": return "text-red-700 bg-red-100";
            default: return "text-gray-700 bg-gray-100";
        }
    };

    return (
        <div className="bg-white p-6 rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 flex flex-col h-full min-h-[320px]">
            <div className="flex justify-between items-center mb-6 shrink-0">
                <h3 className="font-semibold text-lg text-gray-900">Recent AI Calls</h3>
                <button
                    onClick={() => window.location.href = "/dashboard/calls"}
                    className="text-[11px] font-bold border border-gray-200 px-3 py-1.5 rounded-full hover:bg-gray-50 text-gray-700 transition-colors flex items-center gap-1 cursor-pointer"
                >
                    View All Logs
                </button>
            </div>

            <div className="flex flex-col gap-5 overflow-y-auto pr-2">
                {isLoading ? (
                    <div className="flex justify-center items-center h-full pt-10">
                        <div className="w-8 h-8 border-2 border-[#0a4c2f] border-t-transparent rounded-full animate-spin"></div>
                    </div>
                ) : calls.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">No recent calls found</div>
                ) : (
                    calls.slice(0, 4).map((call: any, i: number) => (
                        <div key={i} className="flex justify-between items-center group cursor-pointer" onClick={() => window.location.href = `/dashboard/calls/${call.id}`}>
                            <div className="flex items-center gap-3 min-w-0 flex-1">
                                <div className="w-10 h-10 rounded-full bg-[#f3f5f4] flex items-center justify-center shrink-0">
                                    <Phone className="w-4 h-4 text-gray-500" />
                                </div>
                                <div className="min-w-0 pr-2">
                                    <h4 className="text-[14px] font-bold text-gray-900 mb-1 truncate">{call.customer_number || "Unknown Caller"}</h4>
                                    <p className="text-[12px] text-gray-500 font-medium truncate">
                                        {call.summary ? call.summary : (call.duration_seconds ? `Duration: ${Math.floor(call.duration_seconds / 60)}m ${call.duration_seconds % 60}s` : "AI conversation")}
                                    </p>
                                </div>
                            </div>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wide shrink-0 ${getStatusCol(call.status)}`}>
                                {call.status.charAt(0).toUpperCase() + call.status.slice(1)}
                            </span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

function LiveAIAgent({ config }: { config: any }) {
    const { user } = useAuth();
    const { data: phoneStatus } = useQuery({
        queryKey: ["phoneStatus", user?.tenant_id],
        queryFn: () => phoneApi.getStatus(user?.tenant_id!),
        enabled: !!user?.tenant_id,
    });

    const phoneNumber = (phoneStatus?.has_phone && phoneStatus?.phone_number)
        ? phoneStatus.phone_number
        : (config?.vapi_phone_number || "+1 (000) 000-0000");
    const agentName = config?.assistant_name || "Receptionist";

    return (
        <div className="bg-gradient-to-br from-[#124d30] via-[#0b2818] to-[#041a0d] p-7 rounded-[24px] shadow-xl flex flex-col justify-between h-full min-h-[320px] relative overflow-hidden text-white border border-[#1b8550]/20">
            {/* Wavy Background */}
            <svg className="absolute inset-0 w-full h-[500px] -top-20 opacity-30 object-cover mix-blend-screen pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                <path d="M0,30 C30,10 70,60 100,20 L100,100 L0,100 Z" fill="#0C4A2A" />
                <path d="M0,50 C30,30 70,80 100,40 L100,100 L0,100 Z" fill="#48a074" opacity="0.6" />
                <path d="M0,70 C40,50 60,90 100,60 L100,100 L0,100 Z" fill="#2f7351" opacity="0.4" />
            </svg>

            <div className="relative z-10 flex flex-col h-full">
                <div className="flex justify-between items-start">
                    <h3 className="font-semibold text-white/90 text-lg">AI Agent Information</h3>
                    <span className="flex h-3 w-3 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                    </span>
                </div>

                <div className="flex-1 flex flex-col items-center justify-center -mt-2">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 bg-[#48a074] rounded-full blur-[60px] opacity-20"></div>
                    <span className="text-[13px] text-emerald-200/80 font-semibold tracking-wider uppercase mb-1.5">Assistant Line</span>
                    <div className="text-[28px] lg:text-[24px] xl:text-[28px] font-bold tracking-tight text-white mb-4 whitespace-nowrap" style={{ fontVariantNumeric: "tabular-nums" }}>
                        {phoneNumber}
                    </div>
                    <div className="inline-flex items-center gap-2 bg-black/20 rounded-full px-3.5 py-1.5 border border-white/10 backdrop-blur-sm">
                        <Mic className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-[12px] text-white/90 font-bold tracking-wide">Name: {agentName}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ─────────────── Dashboard Page ─────────────── */
export default function DashboardPage() {
    const { config } = useTenant();
    const router = useRouter();
    const { data, isLoading } = useDashboardStats();

    const {
        appointments = [],
        conversations = [],
        metrics = {
            totalAppointments: 0,
            upcomingAppointments: 0,
            completedToday: 0,
            activeServices: 0,
        },
    } = data || {};

    return (
        <>
            {/* Page Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-6 md:mb-8 gap-4">
                <div>
                    <h1 className="text-[28px] md:text-[32px] font-bold tracking-tight text-gray-900 mb-1.5 leading-none">Dashboard</h1>
                    <p className="text-[13px] md:text-[14px] text-gray-500 font-medium">Plan, prioritize, and accomplish your tasks with ease.</p>
                </div>
                <div className="flex gap-2 w-full md:w-auto">
                    <button
                        onClick={() => router.push("/dashboard/appointments")}
                        className="flex-1 md:flex-none px-4 md:px-6 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] border border-[#1b8550]/40 text-white rounded-[20px] font-semibold hover:from-[#1b8550] hover:via-[#0c5c39] hover:to-[#073922] transition-all flex items-center justify-center gap-2 shadow-[0_4px_16px_rgba(10,76,47,0.3)] relative overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                        <span className="text-lg leading-none mb-0.5 relative z-10">+</span>
                        <span className="relative z-10 whitespace-nowrap">Appointment</span>
                    </button>
                    <button className="flex-1 md:flex-none px-4 md:px-6 py-2.5 bg-white border border-[#0a4c2f] text-[#0a4c2f] rounded-[20px] font-semibold hover:bg-[#0a4c2f]/5 transition-colors shadow-sm whitespace-nowrap">
                        Export Data
                    </button>
                </div>
            </div>

            {/* All Dashboard Widgets */}
            <div className="flex flex-col gap-6">
                <KPICards metrics={metrics} conversations={conversations} isLoading={isLoading} />

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <ProjectAnalytics />
                    <div className="relative">
                        <AppointmentsTimeline appointments={appointments} />
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="relative">
                        <RecentVoiceCalls />
                    </div>
                    <LiveAIAgent config={config} />
                </div>
            </div>
        </>
    );
}
