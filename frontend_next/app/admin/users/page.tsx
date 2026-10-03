"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow, format } from "date-fns";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Activity, Building2, Check, Clock, RefreshCw, Search, ShieldAlert, Trash2, Users as UsersIcon, X } from "lucide-react";
import { toast } from "sonner";
import { adminApi } from "@/lib/api/admin";
import { cn } from "@/lib/utils";
import { Avatar, EmptyState, LoadingState, PageHeader, Panel, Pill, StatCard, type Tone } from "@/components/admin/AdminUI";

interface User {
    id: string;
    email: string;
    username: string;
    full_name?: string;
    business_name?: string;
    role: string;
    tenant_id?: string;
    created_at: string;
    last_login?: string;
    active: boolean;
    approval_status?: "pending" | "approved" | "rejected";
    phone?: string;
}

type Filter = "all" | "pending" | "approved" | "rejected";
const FILTERS: Filter[] = ["all", "pending", "approved", "rejected"];

const APPROVAL: Record<string, { tone: Tone; label: string }> = {
    pending: { tone: "amber", label: "Pending" },
    rejected: { tone: "red", label: "Rejected" },
    approved: { tone: "green", label: "Approved" },
};

export default function UsersAdminPage() {
    // useSearchParams needs a Suspense boundary in the app router.
    return (
        <Suspense fallback={<LoadingState label="Loading accounts…" />}>
            <UsersAdmin />
        </Suspense>
    );
}

function UsersAdmin() {
    const searchParams = useSearchParams();
    const [search, setSearch] = useState("");
    const [filter, setFilter] = useState<Filter>("all");

    // The sidebar links to ?filter=pending; follow the URL whenever it changes.
    useEffect(() => {
        const requested = searchParams.get("filter") as Filter | null;
        setFilter(requested && FILTERS.includes(requested) ? requested : "all");
    }, [searchParams]);

    // Fetch all users
    const { data: users = [], isLoading, refetch, isFetching } = useQuery({
        queryKey: ["admin-users"],
        queryFn: async () => {
            const response = await api.get("/admin/users");
            return response as User[];
        },
    });

    // Business names come from the tenants list.
    const { data: tenantNames = {} } = useQuery({
        queryKey: ["admin-tenants", "names"],
        queryFn: async () => {
            const response = await adminApi.getTenants(0, 500);
            const list = Array.isArray(response) ? response : response.items;
            return Object.fromEntries(list.map((t: any) => [t.id, t.settings?.business_name || t.name])) as Record<string, string>;
        },
    });

    const statusOf = (u: User) => u.approval_status || "approved";
    const counts = Object.fromEntries(FILTERS.map((f) => [f, f === "all" ? users.length : users.filter((u) => statusOf(u) === f).length]));

    const filteredUsers = users.filter((user) => {
        if (filter !== "all" && statusOf(user) !== filter) return false;
        const searchLower = search.toLowerCase();
        const business = (user.tenant_id && tenantNames[user.tenant_id]) || user.business_name || "";
        return (
            user.email?.toLowerCase().includes(searchLower) ||
            user.username?.toLowerCase().includes(searchLower) ||
            user.full_name?.toLowerCase().includes(searchLower) ||
            business.toLowerCase().includes(searchLower)
        );
    });

    const decide = async (user: User, approve: boolean) => {
        try {
            await (approve ? adminApi.approveUser(user.id) : adminApi.rejectUser(user.id));
            toast.success(approve ? "Account approved" : "Account rejected");
            refetch();
        } catch (error: any) {
            toast.error(error?.message || "Failed to update the account");
        }
    };

    if (isLoading) return <LoadingState label="Loading accounts…" />;

    return (
        <>
            <PageHeader
                eyebrow="Clients"
                title="Accounts"
                description="People who can log in to a Calleem dashboard. Approve new sign-ups here."
                actions={
                    <Button variant="outline" className="border-border bg-transparent text-foreground hover:bg-white/5" onClick={() => refetch()}>
                        <RefreshCw className={cn("size-4", isFetching && "animate-spin")} /> Refresh
                    </Button>
                }
            />

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard label="Accounts" value={users.length} hint="All registered" icon={UsersIcon} tone="lime" />
                <StatCard label="Active" value={users.filter((u) => u.active).length} hint="Allowed to log in" icon={Activity} tone="green" />
                <StatCard label="Business owners" value={users.filter((u) => u.role === "owner").length} hint="Your customers" icon={Building2} tone="blue" />
                <StatCard
                    label="Pending approval"
                    value={counts.pending}
                    hint={counts.pending ? "Waiting for your review" : "Nothing to review"}
                    icon={Clock}
                    tone={counts.pending ? "amber" : "slate"}
                />
            </div>

            <Panel
                bodyClassName="p-0"
                title={
                    <div className="flex items-center gap-1 rounded-xl bg-white/[0.03] p-1 ring-1 ring-inset ring-border">
                        {FILTERS.map((f) => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={cn(
                                    "rounded-lg px-3 py-1.5 text-[13px] font-medium capitalize transition-colors",
                                    filter === f ? "bg-white/[0.08] text-white" : "text-muted-foreground hover:text-foreground",
                                )}
                            >
                                {f}
                                <span className={cn("ml-1.5 text-xs", f === "pending" && counts.pending ? "text-amber-300" : "text-[#5f7368]")}>
                                    {counts[f]}
                                </span>
                            </button>
                        ))}
                    </div>
                }
                actions={
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            placeholder="Search name, email or business…"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="h-9 w-[300px] rounded-xl pl-9"
                        />
                    </div>
                }
            >
                {filteredUsers.length === 0 ? (
                    <EmptyState icon={UsersIcon} title="No accounts here" hint={filter === "pending" ? "Nobody is waiting for approval." : undefined} />
                ) : (
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border text-left text-[11px] uppercase tracking-[0.06em] text-muted-foreground">
                                <th className="px-5 py-3 font-semibold">Account</th>
                                <th className="px-5 py-3 font-semibold">Business</th>
                                <th className="px-5 py-3 font-semibold">Role</th>
                                <th className="px-5 py-3 font-semibold">Approval</th>
                                <th className="px-5 py-3 font-semibold">Joined</th>
                                <th className="px-5 py-3 font-semibold">Last active</th>
                                <th className="px-5 py-3 text-right font-semibold">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filteredUsers.map((user) => {
                                const approval = APPROVAL[statusOf(user)];
                                const business = (user.tenant_id && tenantNames[user.tenant_id]) || user.business_name;
                                return (
                                    <tr key={user.id} className="group transition-colors hover:bg-white/[0.02]">
                                        <td className="px-5 py-3">
                                            <div className="flex items-center gap-3">
                                                <Avatar name={user.full_name || user.username} className="size-8" />
                                                <div className="min-w-0">
                                                    <p className="truncate font-medium text-foreground">{user.full_name || user.username}</p>
                                                    <p className="truncate text-xs text-muted-foreground">{user.email}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-5 py-3 text-foreground">{business || <span className="text-muted-foreground">—</span>}</td>
                                        <td className="px-5 py-3">
                                            <Pill tone={user.role === "super_admin" ? "lime" : "slate"}>
                                                {user.role === "super_admin" ? "Super admin" : user.role.replace(/^\w/, (c) => c.toUpperCase())}
                                            </Pill>
                                        </td>
                                        <td className="px-5 py-3">
                                            <Pill dot tone={approval.tone}>
                                                {approval.label}
                                            </Pill>
                                        </td>
                                        <td className="px-5 py-3 text-muted-foreground">{format(new Date(user.created_at), "MMM d, yyyy")}</td>
                                        <td className="px-5 py-3 text-muted-foreground">
                                            {user.last_login ? formatDistanceToNow(new Date(user.last_login), { addSuffix: true }) : "Never"}
                                        </td>
                                        <td className="px-5 py-3">
                                            <div className="flex items-center justify-end gap-1.5">
                                                {user.approval_status === "pending" && (
                                                    <>
                                                        <Button
                                                            size="sm"
                                                            variant="ghost"
                                                            className="text-muted-foreground hover:bg-rose-500/10 hover:text-rose-300"
                                                            onClick={() => decide(user, false)}
                                                        >
                                                            <X className="size-4" /> Reject
                                                        </Button>
                                                        <Button size="sm" onClick={() => decide(user, true)}>
                                                            <Check className="size-4" /> Approve
                                                        </Button>
                                                    </>
                                                )}
                                                <AlertDialog>
                                                    <AlertDialogTrigger asChild>
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            title={user.role === "super_admin" ? "The super admin can't be deleted" : "Delete account"}
                                                            className="size-8 text-muted-foreground opacity-60 hover:bg-rose-500/10 hover:text-rose-300 group-hover:opacity-100"
                                                            disabled={user.role === "super_admin"}
                                                        >
                                                            <Trash2 className="size-4" />
                                                        </Button>
                                                    </AlertDialogTrigger>
                                                    <AlertDialogContent>
                                                        <AlertDialogHeader>
                                                            <AlertDialogTitle className="flex items-center gap-2">
                                                                <ShieldAlert className="size-5 text-rose-400" />
                                                                Delete this account and its data?
                                                            </AlertDialogTitle>
                                                            <AlertDialogDescription>
                                                                This permanently deletes <strong className="text-foreground">{user.email}</strong> and wipes their
                                                                business data (appointments, logs, settings). It cannot be undone.
                                                            </AlertDialogDescription>
                                                        </AlertDialogHeader>
                                                        <AlertDialogFooter>
                                                            <AlertDialogCancel className="border-border bg-transparent text-foreground hover:bg-white/5">Cancel</AlertDialogCancel>
                                                            <AlertDialogAction
                                                                className="bg-rose-600 text-white hover:bg-rose-700"
                                                                onClick={async () => {
                                                                    try {
                                                                        await api.delete(`/admin/users/${user.id}`);
                                                                        toast.success("Account deleted");
                                                                        refetch();
                                                                    } catch (error: any) {
                                                                        toast.error(error?.message || "Failed to delete account");
                                                                    }
                                                                }}
                                                            >
                                                                Delete permanently
                                                            </AlertDialogAction>
                                                        </AlertDialogFooter>
                                                    </AlertDialogContent>
                                                </AlertDialog>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </Panel>
        </>
    );
}
