"use client";

import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { ArrowUpRight, Building2, Check, CircleDollarSign, Clock, Inbox, PhoneCall, UserCheck, X } from "lucide-react";
import { toast } from "sonner";
import { adminApi } from "@/lib/api/admin";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Avatar, CallsStatusPill, EmptyState, LoadingState, PageHeader, Panel, Pill, PlanPill, StatCard } from "@/components/admin/AdminUI";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Lead {
    id: string;
    full_name: string;
    business_name: string;
    business_type: string;
    monthly_calls: string;
    status: string;
    created_at: string;
}

const money = (n: number) => n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

function greeting() {
    const h = new Date().getHours();
    return h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
}

export default function AdminOverview() {
    const { user } = useAuth();
    const queryClient = useQueryClient();

    const billing = useQuery({ queryKey: ["admin-billing"], queryFn: () => adminApi.getBillingOverview() });
    const pending = useQuery({ queryKey: ["admin-pending-users"], queryFn: () => adminApi.getPendingUsers() });
    const leads = useQuery({
        queryKey: ["admin-leads", "latest"],
        queryFn: async (): Promise<Lead[]> => {
            const token = localStorage.getItem("access_token");
            const res = await fetch(`${API_BASE}/api/v1/contacts?limit=5`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
            if (!res.ok) throw new Error("Failed to load leads");
            return res.json();
        },
    });

    const decide = useMutation({
        mutationFn: ({ id, approve }: { id: string; approve: boolean }) => (approve ? adminApi.approveUser(id) : adminApi.rejectUser(id)),
        onSuccess: (_, { approve }) => {
            toast.success(approve ? "Account approved" : "Account rejected");
            queryClient.invalidateQueries({ queryKey: ["admin-pending-users"] });
            queryClient.invalidateQueries({ queryKey: ["admin-billing"] });
        },
        onError: () => toast.error("Could not update the account"),
    });

    if (billing.isLoading) return <LoadingState label="Loading your console…" />;

    const summary = billing.data?.platform_summary;
    const businesses = [...(billing.data?.tenants ?? [])].sort((a, b) => b.calls_30d - a.calls_30d);
    const totalCalls = businesses.reduce((sum, t) => sum + t.calls_30d, 0);
    const pendingUsers = pending.data ?? [];
    const firstName = (user?.full_name || "").split(" ")[0];

    return (
        <>
            <PageHeader
                eyebrow="Super admin"
                title={`${greeting()}${firstName ? `, ${firstName}` : ""}`}
                description="Your clients, revenue and approvals at a glance."
                actions={
                    <Button asChild variant="outline" className="border-border bg-transparent text-foreground hover:bg-white/5">
                        <Link href="/admin/billing">
                            Billing <ArrowUpRight className="size-4" />
                        </Link>
                    </Button>
                }
            />

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard
                    label="Paying businesses"
                    value={summary?.paying_tenants ?? 0}
                    hint={`${summary?.total_tenants ?? 0} registered in total`}
                    icon={Building2}
                    tone="lime"
                />
                <StatCard
                    label="Revenue · 30 days"
                    value={money(summary?.revenue_30d_usd ?? 0)}
                    hint={`Margin ${money(summary?.margin_30d_usd ?? 0)} after voice costs`}
                    icon={CircleDollarSign}
                    tone="green"
                />
                <StatCard
                    label="Pending approvals"
                    value={pendingUsers.length}
                    hint={pendingUsers.length ? "Waiting for your review" : "You're all caught up"}
                    icon={Clock}
                    tone={pendingUsers.length ? "amber" : "slate"}
                />
                <StatCard label="Calls · 30 days" value={totalCalls.toLocaleString()} hint="Across all clients" icon={PhoneCall} tone="blue" />
            </div>

            <div className="grid gap-6 xl:grid-cols-5">
                <Panel
                    className="xl:col-span-3"
                    title="Pending approvals"
                    description="New businesses that signed up and are waiting for access"
                    bodyClassName="p-0"
                    actions={
                        <Link href="/admin/users?filter=pending" className="text-xs font-medium text-[#a8ff5c] hover:underline">
                            View all
                        </Link>
                    }
                >
                    {pendingUsers.length === 0 ? (
                        <EmptyState icon={UserCheck} title="No one is waiting" hint="New sign-ups will appear here." />
                    ) : (
                        <ul className="divide-y divide-border">
                            {pendingUsers.slice(0, 5).map((u) => (
                                <li key={u.id} className="flex items-center gap-3 px-5 py-3.5">
                                    <Avatar name={u.full_name} />
                                    <div className="min-w-0 flex-1">
                                        <p className="truncate text-sm font-medium text-foreground">{u.full_name}</p>
                                        <p className="truncate text-xs text-muted-foreground">
                                            {u.email}
                                            {u.created_at && ` · signed up ${formatDistanceToNow(new Date(u.created_at), { addSuffix: true })}`}
                                        </p>
                                    </div>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        className="text-muted-foreground hover:bg-rose-500/10 hover:text-rose-300"
                                        disabled={decide.isPending}
                                        onClick={() => decide.mutate({ id: u.id, approve: false })}
                                    >
                                        <X className="size-4" /> Reject
                                    </Button>
                                    <Button size="sm" disabled={decide.isPending} onClick={() => decide.mutate({ id: u.id, approve: true })}>
                                        <Check className="size-4" /> Approve
                                    </Button>
                                </li>
                            ))}
                        </ul>
                    )}
                </Panel>

                <Panel
                    className="xl:col-span-2"
                    title="Newest leads"
                    description="From the contact form on calleem.tech"
                    bodyClassName="p-0"
                    actions={
                        <Link href="/admin/contacts" className="text-xs font-medium text-[#a8ff5c] hover:underline">
                            View all
                        </Link>
                    }
                >
                    {(leads.data ?? []).length === 0 ? (
                        <EmptyState icon={Inbox} title="No leads yet" hint="Contact-form submissions will show up here." />
                    ) : (
                        <ul className="divide-y divide-border">
                            {(leads.data ?? []).map((lead) => (
                                <li key={lead.id} className="flex items-center gap-3 px-5 py-3.5">
                                    <Avatar name={lead.business_name} className="from-sky-600 to-slate-800" />
                                    <div className="min-w-0 flex-1">
                                        <p className="truncate text-sm font-medium text-foreground">{lead.business_name}</p>
                                        <p className="truncate text-xs text-muted-foreground">
                                            {lead.full_name} · {lead.business_type} · {lead.monthly_calls} calls/mo
                                        </p>
                                    </div>
                                    {lead.status === "new" && <Pill tone="lime" dot>New</Pill>}
                                </li>
                            ))}
                        </ul>
                    )}
                </Panel>
            </div>

            <Panel
                title="Businesses"
                description="Plan, usage and minutes left per client"
                bodyClassName="p-0"
                actions={
                    <Link href="/admin/tenants" className="text-xs font-medium text-[#a8ff5c] hover:underline">
                        Manage businesses
                    </Link>
                }
            >
                {businesses.length === 0 ? (
                    <EmptyState icon={Building2} title="No businesses yet" />
                ) : (
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border text-left text-[11px] font-semibold uppercase tracking-[0.06em] text-muted-foreground">
                                <th className="px-5 py-3 font-semibold">Business</th>
                                <th className="px-5 py-3 font-semibold">Plan</th>
                                <th className="px-5 py-3 font-semibold">Status</th>
                                <th className="px-5 py-3 text-right font-semibold">Calls · 30d</th>
                                <th className="px-5 py-3 text-right font-semibold">Revenue · 30d</th>
                                <th className="px-5 py-3 text-right font-semibold">Minutes left</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {businesses.map((t) => (
                                <tr key={t.tenant_id} className="transition-colors hover:bg-white/[0.02]">
                                    <td className="px-5 py-3">
                                        <div className="flex items-center gap-3">
                                            <Avatar name={t.name} className="size-8" />
                                            <div className="min-w-0">
                                                <p className="truncate font-medium text-foreground">{t.name}</p>
                                                <p className="truncate text-xs text-muted-foreground">{t.email}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-5 py-3"><PlanPill plan={t.billing_plan} /></td>
                                    <td className="px-5 py-3">
                                        <CallsStatusPill paused={t.calls_paused} exempt={t.billing_exempt} minutes={t.minutes_balance} />
                                    </td>
                                    <td className="px-5 py-3 text-right tabular-nums text-foreground">{t.calls_30d.toLocaleString()}</td>
                                    <td className="px-5 py-3 text-right tabular-nums text-foreground">{money(t.revenue_30d_usd)}</td>
                                    <td className="px-5 py-3 text-right tabular-nums">
                                        <span className={t.minutes_balance <= 30 ? "text-amber-300" : "text-foreground"}>
                                            {Math.round(t.minutes_balance).toLocaleString()} min
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </Panel>
        </>
    );
}
