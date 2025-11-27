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
} from "lucide-react";
import { NavLink } from "./NavLink";
import { useRouter, usePathname } from "next/navigation";
import { useConfig } from "@/contexts/ConfigContext";

const menuItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
    {
        icon: Bot,
        label: "AI Receptionist",
        path: "/dashboard/ai-receptionist",
        subItems: [
            { icon: BarChart3, label: "Overview", path: "/dashboard/ai-receptionist" },
            { icon: TestTube, label: "Test AI", path: "/dashboard/ai-receptionist/test" },
        ]
    },
    { icon: Calendar, label: "Appointments", path: "/dashboard/appointments" },
    { icon: MessageSquare, label: "Conversations", path: "/dashboard/conversations" },
    { icon: Scissors, label: "Services", path: "/dashboard/services" },
    { icon: CalendarDays, label: "Schedule", path: "/dashboard/schedule" },
    { icon: Smartphone, label: "WhatsApp", path: "/dashboard/whatsapp" },
    {
        icon: Phone,
        label: "Voice Agent",
        path: "/dashboard/voice-agent",
        subItems: [
            { icon: PhoneCall, label: "Control Room", path: "/dashboard/voice-agent" },
            { icon: Mic, label: "Voice Chat", path: "/dashboard/voice-agent/chat" },
            { icon: Waves, label: "WebRTC Test", path: "/dashboard/voice-agent/test" },
            { icon: Settings, label: "Voice Settings", path: "/dashboard/voice-agent/settings" },
        ]
    },
];

const generalItems = [
    {
        icon: Settings,
        label: "Settings",
        path: "/dashboard/settings",
        subItems: [
            { icon: Settings, label: "Settings Hub", path: "/dashboard/settings" },
            { icon: Building2, label: "Business", path: "/dashboard/settings/business" },
            { icon: UserCog, label: "Team", path: "/dashboard/settings/team" },
            { icon: Brain, label: "AI Config", path: "/dashboard/settings/ai" },
            { icon: Plug, label: "Integrations", path: "/dashboard/settings/integrations" },
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
                    {hasSubItems && (
                        expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />
                    )}
                </NavLink>

                {hasSubItems && expanded && (
                    <div className="ml-4 mt-1 space-y-1 border-l-2 border-white/20 pl-2">
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
        <aside className="fixed left-0 top-0 h-screen w-64 glass-strong flex flex-col z-50 overflow-y-auto border-r border-white/20">
            <div className="p-6">
                <div className="flex items-center gap-2">
                    {config?.logo_url ? (
                        <img src={config.logo_url} alt="Logo" className="w-10 h-10 rounded-full object-cover" />
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
