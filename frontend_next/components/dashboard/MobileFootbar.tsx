"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, CalendarCheck, Layers, PhoneCall, Bot, Calendar, Settings, HelpCircle, LogOut, Plus, ChevronUp } from "lucide-react";

const scheduleLinks = [
    { href: "/dashboard/appointments", label: "Appointments", icon: CalendarCheck },
    { href: "/dashboard/schedule", label: "Calendar", icon: Calendar },
    { href: "/dashboard/services", label: "Services", icon: Layers },
];

const moreLinks = [
    { href: "/dashboard/settings", label: "Settings", icon: Settings },
    { href: "/dashboard/help", label: "Help", icon: HelpCircle },
];

export function MobileFootbar() {
    const pathname = usePathname();
    const router = useRouter();
    const [isScheduleOpen, setIsScheduleOpen] = useState(false);
    const [isMoreOpen, setIsMoreOpen] = useState(false);

    const scheduleRef = useRef<HTMLDivElement>(null);
    const moreRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (scheduleRef.current && !scheduleRef.current.contains(event.target as Node)) {
                setIsScheduleOpen(false);
            }
            if (moreRef.current && !moreRef.current.contains(event.target as Node)) {
                setIsMoreOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const isHomeActive = pathname === "/dashboard" || pathname.startsWith("/dashboard/");
    const isCallsActive = pathname.startsWith("/dashboard/calls");
    const isVoiceActive = pathname.startsWith("/dashboard/voice-agent");

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("username");
        localStorage.removeItem("tenant_id");
        localStorage.removeItem("user");
        router.push("/login");
    };

    return (
        <div className="md:hidden fixed bottom-4 left-4 right-4 z-50">
            <div
                className={`absolute bottom-[80px] left-1/2 -translate-x-1/2 transition-all duration-300 origin-bottom ${
                    isScheduleOpen ? "opacity-100 scale-100 translate-y-0 pointer-events-auto" : "opacity-0 scale-95 translate-y-4 pointer-events-none"
                }`}
            >
                <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.12)] border border-gray-100 p-2 w-[200px] flex flex-col gap-1 relative">
                    <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-white border-b border-r border-gray-100 transform rotate-45"></div>

                    {scheduleLinks.map((item) => {
                        const Icon = item.icon;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                onClick={() => setIsScheduleOpen(false)}
                                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-700 font-medium hover:bg-gray-50 active:bg-gray-100 transition-colors w-full text-left"
                            >
                                <Icon className="w-5 h-5 text-[#0a4c2f]" />
                                <span className="text-[14px]">{item.label}</span>
                            </Link>
                        );
                    })}
                </div>
            </div>

            <div
                className={`absolute bottom-[80px] right-2 transition-all duration-300 origin-bottom-right ${
                    isMoreOpen ? "opacity-100 scale-100 translate-y-0 pointer-events-auto" : "opacity-0 scale-95 translate-y-4 pointer-events-none"
                }`}
            >
                <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.12)] border border-gray-100 p-2 w-[160px] flex flex-col gap-1 relative">
                    <div className="absolute -bottom-2 right-6 w-4 h-4 bg-white border-b border-r border-gray-100 transform rotate-45"></div>

                    {moreLinks.map((item) => {
                        const Icon = item.icon;
                        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                onClick={() => setIsMoreOpen(false)}
                                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-700 font-medium hover:bg-gray-50 active:bg-gray-100 transition-colors w-full text-left ${
                                    active ? "text-[#0a4c2f]" : ""
                                }`}
                            >
                                <Icon className="w-5 h-5" />
                                <span className="text-[14px]">{item.label}</span>
                            </Link>
                        );
                    })}
                    <div className="h-[1px] bg-gray-100 my-1"></div>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-red-600 font-medium hover:bg-red-50 active:bg-red-100 transition-colors w-full text-left"
                    >
                        <LogOut className="w-5 h-5" />
                        <span className="text-[14px]">Logout</span>
                    </button>
                </div>
            </div>

            <div className="bg-[#f3f5f4] rounded-[24px] shadow-lg shadow-black/5 p-2 px-4 border border-white flex justify-between items-center relative">
                <Link
                    href="/dashboard"
                    className="flex flex-col items-center gap-1 p-2 w-16 group relative"
                >
                    <LayoutDashboard className={`w-[22px] h-[22px] stroke-[2.5px] ${isHomeActive ? "text-[#0a4c2f]" : "text-gray-500"}`} />
                    <span className={`text-[10px] font-bold ${isHomeActive ? "text-[#0a4c2f]" : "text-gray-500"}`}>Home</span>
                    <div className="absolute -bottom-[2px] w-8 h-[3px] bg-gradient-to-r from-[#187848] via-[#0a4c2f] to-[#052b19] rounded-t-md shadow-[0_-2px_8px_rgba(24,120,72,0.6)]"></div>
                </Link>

                <Link
                    href="/dashboard/calls"
                    className="flex flex-col items-center gap-1 p-2 w-16 group text-gray-500 hover:text-gray-900 transition-colors relative"
                >
                    <PhoneCall className="w-[22px] h-[22px] group-active:scale-95 transition-transform" />
                    <span className="text-[10px] font-semibold">Calls</span>
                    {isCallsActive && <span className="absolute top-1 right-3.5 w-2 h-2 bg-[#0a4c2f] rounded-full border border-[#f3f5f4]" />}
                </Link>

                <div ref={scheduleRef} className="relative -mt-8 flex flex-col items-center">
                    <button
                        onClick={() => {
                            setIsScheduleOpen(!isScheduleOpen);
                            setIsMoreOpen(false);
                        }}
                        className={`w-[52px] h-[52px] rounded-full bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white flex items-center justify-center shadow-[0_8px_20px_rgba(10,76,47,0.35)] transition-transform duration-300 ring-4 ring-[#f3f5f4] ${isScheduleOpen ? "rotate-45" : "hover:scale-105 active:scale-95"}`}
                    >
                        <Plus className="w-6 h-6" />
                    </button>
                    <span className="text-[10px] text-gray-600 font-bold mt-1">Schedule</span>
                </div>

                <Link
                    href="/dashboard/voice-agent"
                    className="flex flex-col items-center gap-1 p-2 w-16 group text-gray-500 hover:text-gray-900 transition-colors"
                >
                    <Bot className={`w-[22px] h-[22px] group-active:scale-95 transition-transform ${isVoiceActive ? "text-[#0a4c2f]" : ""}`} />
                    <span className="text-[10px] font-semibold">Voice AI</span>
                </Link>

                <div ref={moreRef}>
                    <button
                        onClick={() => {
                            setIsMoreOpen(!isMoreOpen);
                            setIsScheduleOpen(false);
                        }}
                        className="flex flex-col items-center gap-1 p-2 w-16 group text-gray-500 hover:text-gray-900 transition-colors"
                    >
                        <ChevronUp className={`w-[22px] h-[22px] transition-transform duration-300 ${isMoreOpen ? "rotate-180" : ""}`} />
                        <span className="text-[10px] font-semibold">More</span>
                    </button>
                </div>
            </div>
        </div>
    );
}