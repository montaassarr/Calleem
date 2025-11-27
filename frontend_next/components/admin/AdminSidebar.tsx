"use client";

import { useState } from "react";
import {
    LayoutDashboard,
    Users,
    Building2,
    BarChart3,
    Settings,
    LogOut,
    Shield,
    Database,
    CreditCard,
    Activity,
    Server,
    ChevronDown,
    ChevronRight,
    Calendar,
    MessageSquare,
    Scissors,
    Phone,
    Globe,
    Terminal,
    Lock,
} from "lucide-react";
import { NavLink } from "../dashboard/NavLink";
import { useRouter, usePathname } from "next/navigation";

const menuItems = [
    // 1. Client Management
    {
        label: "Client Management",
        items: [
            { icon: Building2, label: "Tenants", path: "/admin/tenants" },
            { icon: Users, label: "Users", path: "/admin/users" },
        ]
    },
    // 2. Subscription & Billing
    {
        label: "Billing & Finance",
        items: [
            { icon: CreditCard, label: "Subscriptions", path: "/admin/billing" },
            { icon: BarChart3, label: "Revenue", path: "/admin/revenue" },
        ]
    },
    // 3. AI Agent Operations
    {
        label: "AI Operations",
        items: [
            { icon: Activity, label: "Global Monitoring", path: "/admin/ai-monitor" },
            { icon: MessageSquare, label: "Conversations", path: "/admin/conversations" },
            { icon: Phone, label: "Voice Agents", path: "/admin/voice-agents" },
        ]
    },
    // 4. Technical System
    {
        label: "System Health",
        items: [
            { icon: Server, label: "Infrastructure", path: "/admin/system" },
            { icon: Globe, label: "Webhooks & API", path: "/admin/webhooks" },
            { icon: Terminal, label: "DevOps Tools", path: "/admin/devops" },
        ]
    },
    // 5. Database
    {
        label: "Database",
        items: [
            { icon: Database, label: "Explorer", path: "/admin/db-explorer" },
            { icon: Settings, label: "Config", path: "/admin/config" },
        ]
    },
    // 6. Security
    {
        label: "Security",
        items: [
            { icon: Shield, label: "Access Control", path: "/admin/security" },
            { icon: Lock, label: "Audit Logs", path: "/admin/logs" },
        ]
    }
];

export const AdminSidebar = () => {
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

    const renderMenuItem = (item: any) => {
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
        <aside className="fixed left-0 top-0 h-screen w-64 glass-strong flex flex-col z-50 overflow-y-auto border-r border-white/20 bg-slate-900 text-white">
            <div className="p-6">
                <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-full bg-red-600 flex items-center justify-center shadow-lg shadow-red-500/30">
                        <Shield className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-xl font-bold text-white truncate">
                        Admin Panel
                    </span>
                </div>
            </div>

            <nav className="flex-1 px-3">
                <div className="mb-6 space-y-6">
                    <NavLink
                        href="/admin"
                        className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all hover:bg-white/50 hover:text-primary hover:shadow-md mx-3"
                        activeClassName="bg-primary text-white shadow-lg shadow-primary/30"
                    >
                        <LayoutDashboard className="w-5 h-5" />
                        <span>Overview</span>
                    </NavLink>

                    {menuItems.map((section, idx) => (
                        <div key={idx}>
                            <p className="px-6 text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
                                {section.label}
                            </p>
                            <div className="space-y-1 px-3">
                                {section.items.map((item) => (
                                    <NavLink
                                        key={item.path}
                                        href={item.path}
                                        className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all hover:bg-white/50 hover:text-primary hover:shadow-md"
                                        activeClassName="bg-primary/80 text-white shadow-lg shadow-primary/20"
                                    >
                                        <item.icon className="w-4 h-4" />
                                        <span>{item.label}</span>
                                    </NavLink>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <div>
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all hover:bg-red-500/20 hover:text-red-400 w-full text-left mt-auto"
                    >
                        <LogOut className="w-5 h-5" />
                        <span>Logout</span>
                    </button>
                </div>
            </nav>

            <div className="p-4 m-4 bg-slate-800 rounded-2xl text-slate-300 text-xs border border-slate-700">
                <p className="font-semibold mb-1">System Status</p>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span>Operational</span>
                </div>
            </div>
        </aside>
    );
};
