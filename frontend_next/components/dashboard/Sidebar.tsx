"use client";

import { useEffect, useState } from "react";
import {
    LayoutDashboard,
    Phone,
    PhoneCall,
    Mic,
    Calendar,
    Users,
    Settings,
    HelpCircle,
    LogOut,
    Scissors,
    MessageSquare,
    Bot,
    Smartphone,
    ChevronDown,
    ChevronRight,
    TestTube,
    Building2,
    UserCog,
    Brain,
    Plug,
    CalendarDays,
    Waves,
    Zap,
    MessageCircle,
} from "lucide-react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useConfig } from "@/contexts/ConfigContext";

const menuItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
    { icon: Calendar, label: "Appointments", path: "/dashboard/appointments" },
    { icon: Scissors, label: "Services", path: "/dashboard/services" },
    { icon: MessageSquare, label: "Call History", path: "/dashboard/calls", badge: "5" },
    {
        icon: Mic,
        label: "Voice AI",
        path: "/dashboard/voice-agent",
        subItems: [
            { icon: PhoneCall, label: "Control Center", path: "/dashboard/voice-agent/control-center" },
            { icon: Phone, label: "Phone Numbers", path: "/dashboard/voice-agent/phone-numbers" },
            { icon: Waves, label: "Voice Config", path: "/dashboard/voice-agent/voice" },
            { icon: Brain, label: "Knowledge Base", path: "/dashboard/voice-agent/knowledge-base" },
            { icon: Plug, label: "Tools", path: "/dashboard/voice-agent/tools" },
            { icon: TestTube, label: "Test Call", path: "/dashboard/voice-agent/test" },
            { icon: MessageSquare, label: "Chat Test", path: "/dashboard/voice-agent/chat" },
        ]
    },
    { icon: MessageCircle, label: "WhatsApp", path: "/dashboard/whatsapp" },
    { icon: CalendarDays, label: "Schedule", path: "/dashboard/schedule" },
];

const generalItems = [
    {
        icon: Settings,
        label: "Settings",
        path: "/dashboard/settings",
        subItems: [
            { icon: Settings, label: "Settings Hub", path: "/dashboard/settings" },
            { icon: Building2, label: "Business", path: "/dashboard/settings/business" },
        ]
    },
    { icon: HelpCircle, label: "Help", path: "/dashboard/help" },
];

export const Sidebar = () => {
    const { config } = useConfig();
    const router = useRouter();
    const pathname = usePathname();
    const [expandedItems, setExpandedItems] = useState<string[]>([]);

    const toggleExpand = (path: string) => {
        setExpandedItems(prev =>
            prev.includes(path)
                ? prev.filter(p => p !== path)
                : [...prev, path]
        );
    };

    const isExpanded = (path: string) => {
        return expandedItems.includes(path) || pathname.startsWith(path);
    };

    const isActive = (path: string) => {
        return pathname === path;
    };

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("username");
        router.push("/login");
    };

    const renderMenuItem = (item: any, isGeneral = false) => {
        const hasSubItems = item.subItems && item.subItems.length > 0;
        const expanded = hasSubItems && isExpanded(item.path);
        const active = !hasSubItems && isActive(item.path);

        return (
            <div key={item.path}>
                {hasSubItems ? (
                    <button
                        onClick={() => toggleExpand(item.path)}
                        className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors relative w-full text-left ${active
                            ? 'text-[#0a4c2f] font-semibold bg-white shadow-sm'
                            : 'text-gray-500 font-medium hover:text-gray-900 hover:bg-gray-50'
                            }`}
                    >
                        <item.icon className={`w-[22px] h-[22px] ${active ? 'stroke-[2.5px]' : 'stroke-2'}`} />
                        <span className="flex-1">{item.label}</span>
                        {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </button>
                ) : (
                    <Link
                        href={item.path}
                        className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors relative ${active
                            ? 'text-[#0a4c2f] font-semibold bg-white shadow-sm'
                            : 'text-gray-500 font-medium hover:text-gray-900 hover:bg-gray-50'
                            }`}
                    >
                        {active && (
                            <div className="absolute -left-6 top-1/2 -translate-y-1/2 w-[5px] h-8 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] rounded-r-md shadow-[2px_0_12px_rgba(24,120,72,0.4)]"></div>
                        )}
                        <item.icon className={`w-[22px] h-[22px] ${active ? 'stroke-[2.5px]' : 'stroke-2'}`} />
                        <span>{item.label}</span>
                        {item.badge && (
                            <span className="ml-auto bg-[#0a4c2f] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-md">{item.badge}</span>
                        )}
                    </Link>
                )}

                {hasSubItems && expanded && (
                    <div className="ml-4 mt-1 space-y-1 pl-2 border-l-2 border-gray-200">
                        {item.subItems.map((subItem: any) => {
                            const subActive = isActive(subItem.path);
                            return (
                                <Link
                                    key={subItem.path}
                                    href={subItem.path}
                                    className={`flex items-center gap-3 px-3 py-2 rounded-xl transition-colors text-sm ${subActive
                                        ? 'text-[#0a4c2f] font-semibold bg-white shadow-sm'
                                        : 'text-gray-500 font-medium hover:text-gray-900 hover:bg-gray-50'
                                        }`}
                                >
                                    <subItem.icon className="w-4 h-4" />
                                    <span className="text-xs">{subItem.label}</span>
                                </Link>
                            );
                        })}
                    </div>
                )}
            </div>
        );
    };

    return (
        <aside className="w-[260px] flex flex-col h-full overflow-y-auto scrollbar-hide shrink-0">
            {/* Calleem Logo */}
            <Link href="/dashboard" className="px-6 py-8 flex items-center gap-2 group">
                <svg
                    className="w-8 h-6 text-[#0a4c2f]"
                    viewBox="0 0 41 24"
                    fill="currentColor"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <g transform="translate(0 0.5)">
                        <path d="M 21.821 0.929 C 22.354 0.38 23.092 0.068 23.865 0.065 L 33.762 0.065 C 40.198 0.065 43.42 8.011 38.869 12.659 L 28.958 22.783 C 28.503 23.247 27.725 22.918 27.725 22.26 L 27.725 13.345 L 28.87 12.174 C 29.78 11.245 29.136 9.656 27.848 9.656 L 13.276 9.656 L 21.821 0.929 Z" fill="currentColor"></path>
                        <path d="M 19.179 22.071 C 18.646 22.62 17.908 22.932 17.135 22.935 L 7.238 22.935 C 0.802 22.935 -2.42 14.988 2.131 10.341 L 12.042 0.217 C 12.497 -0.247 13.276 0.082 13.276 0.739 L 13.276 9.655 L 12.13 10.825 C 11.22 11.755 11.864 13.344 13.152 13.344 L 27.724 13.344 L 19.178 22.071 Z" fill="currentColor"></path>
                    </g>
                </svg>
                 <span className="text-[22px] font-black text-gray-900 tracking-tight ml-1 leading-none" style={{ fontStyle: 'italic', transform: 'skewX(-10deg)', letterSpacing: '-0.5px' }}>CALLEEM</span>
            </Link>

            {/* Menu */}
            <div className="px-6 py-2">
                <p className="text-[11px] font-semibold text-gray-400 mb-4 tracking-wider uppercase">Menu</p>
                <nav className="flex flex-col gap-1.5">
                    {menuItems.map((item) => renderMenuItem(item))}
                </nav>
            </div>

            {/* General */}
            <div className="px-6 py-4 mt-2">
                <p className="text-[11px] font-semibold text-gray-400 mb-4 tracking-wider uppercase">General</p>
                <nav className="flex flex-col gap-1.5">
                    {generalItems.map((item) => renderMenuItem(item, true))}
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-500 font-medium hover:text-gray-900 hover:bg-gray-50 transition-colors w-full text-left"
                    >
                        <LogOut className="w-[22px] h-[22px] stroke-2" />
                        <span>Logout</span>
                    </button>
                </nav>
            </div>

            {/* Bottom CTA card */}
            <div className="mt-auto p-6 mb-2">
                <div className="bg-gradient-to-b from-[#156e40] via-[#0a4c2f] to-[#052b19] rounded-[20px] p-5 relative overflow-hidden text-white shadow-xl shadow-green-900/20 border border-[#1b8550]/20">
                    <div className="absolute -top-10 -left-10 w-32 h-32 bg-[#21a05e] rounded-full blur-3xl opacity-30 pointer-events-none"></div>
                    <svg className="absolute inset-0 w-full h-full opacity-20 pointer-events-none" preserveAspectRatio="none" viewBox="0 0 100 100">
                        <path d="M0,50 Q25,20 50,50 T100,50 L100,100 L0,100 Z" fill="#48a074" />
                        <path d="M0,70 Q25,40 50,70 T100,70 L100,100 L0,100 Z" fill="#2f7351" />
                    </svg>
                    <div className="relative z-10">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center mb-4 text-white">
                            <svg viewBox="0 0 24 24" fill="none" className="w-8 h-8">
                                <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                                <path d="M12 18C15.3137 18 18 15.3137 18 12C18 8.68629 15.3137 6 12 6C8.68629 6 6 8.68629 6 12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                                <circle cx="12" cy="12" r="2.5" fill="currentColor" />
                            </svg>
                        </div>
                        <h4 className="font-semibold text-[15px] mb-1 leading-tight text-white">AI Voice<br />Assistant</h4>
                        <p className="text-[11px] text-white/60 mb-5 font-medium">Always on, always booking</p>
                        <Link href="/dashboard/voice-agent/control-center" className="block w-full bg-[#073922] hover:bg-[#052817] text-white text-sm font-medium py-2.5 rounded-xl transition-colors text-center">
                            Configure
                        </Link>
                    </div>
                </div>
            </div>
        </aside>
    );
};
