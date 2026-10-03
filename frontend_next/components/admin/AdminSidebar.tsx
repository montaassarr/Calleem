"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
    Building2,
    Clock,
    CreditCard,
    LayoutDashboard,
    Lock,
    LogOut,
    Mail,
    Users,
    type LucideIcon,
} from "lucide-react";
import { adminApi } from "@/lib/api/admin";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";
import { Avatar } from "./AdminUI";

type NavItem = { icon: LucideIcon; label: string; href: string; badge?: "pending" };

const NAV: { label?: string; items: NavItem[] }[] = [
    { items: [{ icon: LayoutDashboard, label: "Overview", href: "/admin" }] },
    {
        label: "Clients",
        items: [
            { icon: Building2, label: "Businesses", href: "/admin/tenants" },
            { icon: Users, label: "Accounts", href: "/admin/users" },
            { icon: Clock, label: "Pending approvals", href: "/admin/users?filter=pending", badge: "pending" },
            { icon: Mail, label: "Leads", href: "/admin/contacts" },
        ],
    },
    { label: "Revenue", items: [{ icon: CreditCard, label: "Billing", href: "/admin/billing" }] },
];

function isActive(pathname: string, href: string) {
    if (href.includes("?")) return false; // query links share a page with their parent item
    return href === "/admin" ? pathname === "/admin" : pathname === href || pathname.startsWith(`${href}/`);
}

export const AdminSidebar = () => {
    const pathname = usePathname();
    const { user, logout } = useAuth();
    const { data: pending = [] } = useQuery({
        queryKey: ["admin-pending-users"],
        queryFn: () => adminApi.getPendingUsers(),
        refetchInterval: 60_000,
    });

    return (
        <aside className="fixed inset-y-0 left-0 z-50 flex w-[264px] flex-col border-r border-border bg-[#070d0a]">
            <div className="flex items-center gap-2.5 px-6 pb-6 pt-7">
                <svg viewBox="0 0 41 24" className="h-[22px] w-[38px] text-[#8cff2e]" fill="currentColor" aria-hidden>
                    <g transform="translate(0 0.5)">
                        <path d="M 21.821 0.929 C 22.354 0.38 23.092 0.068 23.865 0.065 L 33.762 0.065 C 40.198 0.065 43.42 8.011 38.869 12.659 L 28.958 22.783 C 28.503 23.247 27.725 22.918 27.725 22.26 L 27.725 13.345 L 28.87 12.174 C 29.78 11.245 29.136 9.656 27.848 9.656 L 13.276 9.656 L 21.821 0.929 Z" />
                        <path d="M 19.179 22.071 C 18.646 22.62 17.908 22.932 17.135 22.935 L 7.238 22.935 C 0.802 22.935 -2.42 14.988 2.131 10.341 L 12.042 0.217 C 12.497 -0.247 13.276 0.082 13.276 0.739 L 13.276 9.655 L 12.13 10.825 C 11.22 11.755 11.864 13.344 13.152 13.344 L 27.724 13.344 L 19.178 22.071 Z" />
                    </g>
                </svg>
                <span className="font-host text-[19px] font-bold tracking-tight text-white">Calleem</span>
                <span className="ml-1 rounded-md bg-[#8cff2e]/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-[#a8ff5c] ring-1 ring-inset ring-[#8cff2e]/25">
                    Admin
                </span>
            </div>

            <nav className="flex-1 space-y-6 overflow-y-auto px-3 pb-4">
                {NAV.map((section, i) => (
                    <div key={i}>
                        {section.label && (
                            <p className="mb-1.5 px-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-[#5f7368]">
                                {section.label}
                            </p>
                        )}
                        <div className="space-y-0.5">
                            {section.items.map((item) => {
                                const active = isActive(pathname, item.href);
                                const count = item.badge === "pending" ? pending.length : 0;
                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        className={cn(
                                            "group relative flex items-center gap-3 rounded-xl px-3 py-2 text-[13.5px] font-medium transition-colors",
                                            active ? "bg-white/[0.06] text-white" : "text-[#9aaba1] hover:bg-white/[0.03] hover:text-white",
                                        )}
                                    >
                                        {active && <span className="absolute inset-y-2 left-0 w-[3px] rounded-full bg-[#8cff2e]" />}
                                        <item.icon
                                            className={cn("size-[17px]", active ? "text-[#8cff2e]" : "text-[#6d8076] group-hover:text-[#b6c6bd]")}
                                        />
                                        <span className="flex-1">{item.label}</span>
                                        {count > 0 && (
                                            <span className="rounded-full bg-amber-400/15 px-2 py-0.5 text-[11px] font-semibold text-amber-300 ring-1 ring-inset ring-amber-400/30">
                                                {count}
                                            </span>
                                        )}
                                    </Link>
                                );
                            })}
                        </div>
                    </div>
                ))}
            </nav>

            <div className="border-t border-border p-3">
                <div className="mb-2 flex items-center gap-2 rounded-xl bg-[#8cff2e]/[0.06] px-3 py-2 text-[11.5px] text-[#a8ff5c] ring-1 ring-inset ring-[#8cff2e]/15">
                    <Lock className="size-3.5" />
                    Private console · this PC only
                </div>
                <div className="flex items-center gap-3 rounded-xl px-2 py-2">
                    <Avatar name={user?.full_name || user?.email} />
                    <div className="min-w-0 flex-1">
                        <p className="truncate text-[13px] font-semibold text-white">{user?.full_name || "Super admin"}</p>
                        <p className="truncate text-[11.5px] text-[#7d8f85]">{user?.email}</p>
                    </div>
                    <button
                        onClick={logout}
                        title="Sign out"
                        className="grid size-8 place-items-center rounded-lg text-[#7d8f85] transition-colors hover:bg-rose-500/10 hover:text-rose-300"
                    >
                        <LogOut className="size-4" />
                    </button>
                </div>
            </div>
        </aside>
    );
};
