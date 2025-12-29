"use client";

import { useState } from "react";
import {
    LayoutDashboard,
    Phone,
    PhoneCall,
    Mic,
    Calendar,
    BarChart3,
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
    Key,
    Activity,
} from "lucide-react";
import { NavLink } from "./NavLink";
import { useRouter, usePathname } from "next/navigation";
import { useConfig } from "@/contexts/ConfigContext";

const menuItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
    { icon: Calendar, label: "Appointments", path: "/dashboard/appointments" },
    { icon: Scissors, label: "Services", path: "/dashboard/services" },
    { icon: MessageSquare, label: "Conversations", path: "/dashboard/conversations" },
    {
        icon: Mic,
        label: "Voice AI",
        path: "/dashboard/voice-agent",
        subItems: [
            { icon: PhoneCall, label: "Control Center", path: "/dashboard/voice-agent/control-center" },
            { icon: Phone, label: "Phone Numbers", path: "/dashboard/voice-agent/phone-numbers" },
            { icon: Activity, label: "Live Monitor", path: "/dashboard/voice-agent/live-monitor" },
            { icon: Waves, label: "Voice Config", path: "/dashboard/voice-agent/voice" },
            { icon: Brain, label: "Knowledge Base", path: "/dashboard/voice-agent/knowledge-base" },
            { icon: Plug, label: "Tools", path: "/dashboard/voice-agent/tools" },
            { icon: BarChart3, label: "Analytics", path: "/dashboard/voice-agent/analytics" },
            { icon: TestTube, label: "Test Call", path: "/dashboard/voice-agent/test" },
            { icon: MessageSquare, label: "Chat Test", path: "/dashboard/voice-agent/chat" },
        ]
    },
    { icon: MessageCircle, label: "WhatsApp", path: "/dashboard/whatsapp" },
    { icon: Settings, label: "Billing", path: "/dashboard/settings/billing" },
];

const generalItems = [
    {
        icon: Settings,
        label: "Settings",
        path: "/dashboard/settings",
        subItems: [
            { icon: Settings, label: "Settings Hub", path: "/dashboard/settings" },
            { icon: Building2, label: "Business", path: "/dashboard/settings/business" },

            { icon: Key, label: "API Keys", path: "/dashboard/settings/api-keys" },
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

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("username");
        router.push("/login");
    };

    const renderMenuItem = (item: any, isGeneral = false) => {
        const hasSubItems = item.subItems && item.subItems.length > 0;
        const expanded = hasSubItems && isExpanded(item.path);
        // Check if user is on Pro plan (fallback to false if plan field doesn't exist)
        const isPro = (config as any)?.plan === "pro" || (config as any)?.plan === "enterprise";
        const needsProPlan = item.proPlan && !isPro;

        return (
            <div key={item.path}>
                <NavLink
                    href={!hasSubItems ? item.path : "#"}
                    onClick={(e: any) => {
                        if (hasSubItems) {
                            e.preventDefault();
                            toggleExpand(item.path);
                        }
                    }}
                    className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all hover:bg-white/50 hover:text-primary hover:shadow-md group"
                    activeClassName={!hasSubItems ? "bg-primary text-white shadow-lg shadow-primary/30" : ""}
                >
                    <item.icon className="w-5 h-5" />
                    <span className="flex-1">{item.label}</span>
                    {needsProPlan && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-bold">
                            PRO
                        </span>
                    )}
                    {hasSubItems && (
                        expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />
                    )}
                </NavLink>

                {hasSubItems && expanded && (
                    <div className="ml-4 mt-1 space-y-1 border-l-2 border-slate-200 pl-2">
                        {item.subItems.map((subItem: any) => (
                            <NavLink
                                key={subItem.path}
                                href={subItem.path}
                                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all hover:bg-white/50 hover:text-primary hover:shadow-md"
                                activeClassName="bg-primary/80 text-white shadow-lg shadow-primary/20"
                            >
                                <subItem.icon className="w-4 h-4" />
                                <span className="text-xs">{subItem.label}</span>
                            </NavLink>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 bg-white flex flex-col z-50 overflow-y-auto border-r border-slate-200">
            <div className="p-6">
                <div className="flex items-center gap-2">
                    {config?.logo_url ? (
                        <>
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img src={config.logo_url} alt="Logo" className="w-10 h-10 rounded-full object-cover" />
                        </>
                    ) : (
                        <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
                            <Scissors className="w-5 h-5 text-white" />
                        </div>
                    )}
                    <span className="text-xl font-bold text-primary truncate">
                        {config?.business_name || 'Donezo'}
                    </span>
                </div>
            </div>

            <nav className="flex-1 px-3">
                <div className="mb-6">
                    <p className="px-3 text-xs font-semibold text-muted-foreground mb-2">MENU</p>
                    <div className="space-y-1">
                        {menuItems.map((item) => renderMenuItem(item))}
                    </div>
                </div>

                <div>
                    <p className="px-3 text-xs font-semibold text-muted-foreground mb-2">GENERAL</p>
                    <div className="space-y-1">
                        {generalItems.map((item) => renderMenuItem(item, true))}
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all hover:bg-white/50 hover:text-primary hover:shadow-md w-full text-left"
                        >
                            <LogOut className="w-5 h-5" />
                            <span>Logout</span>
                        </button>
                    </div>
                </div>
            </nav>

            <div className="p-4 m-4 bg-primary rounded-2xl text-white shadow-xl shadow-primary/20 shine">
                <div className="flex items-center gap-2 mb-2">
                    <Phone className="w-5 h-5" />
                    <p className="font-semibold text-sm">AI Receptionist</p>
                </div>
                <p className="text-xs text-white/90 mb-4">Ava is taking calls 24/7</p>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-300 rounded-full animate-pulse" />
                    <span className="text-xs">Active</span>
                </div>
            </div>
        </aside>
    );
};
