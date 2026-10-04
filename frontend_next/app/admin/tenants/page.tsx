"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/lib/api/admin";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Activity, Building2, Clock3, PhoneCall, Search, Trash2, Wand2 } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";
import { format } from "date-fns";
import { Avatar, EmptyState, LoadingState, PageHeader, Panel, Pill, StatCard } from "@/components/admin/AdminUI";

interface Tenant {
    id: string;
    name: string;
    email?: string;
    plan: string;
    status: string;
    created_at: string;
    total_calls?: number;
    total_minutes?: number;
    settings?: {
        business_name?: string;
        phone?: string;
    };
}

function TemplateDialog({ tenant, onClose }: { tenant: Tenant | null; onClose: () => void }) {
    const [choice, setChoice] = useState<string | null>(null);
    const templates = useQuery({ queryKey: ["admin-templates"], queryFn: () => adminApi.getTemplates(), enabled: !!tenant });

    const apply = useMutation({
        mutationFn: () => adminApi.applyTemplate(tenant!.id, choice!),
        onSuccess: (res) => {
            toast.success(`Assistant set up${res.services_added ? ` · ${res.services_added} services added` : ""}`);
            setChoice(null);
            onClose();
        },
        onError: (error: Error) => toast.error(error.message || "Could not apply the template"),
    });

    return (
        <Dialog open={!!tenant} onOpenChange={(open) => !open && (setChoice(null), onClose())}>
            <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                    <DialogTitle>Set up for a niche</DialogTitle>
                    <DialogDescription>
                        Replaces the AI instructions and greeting of {tenant?.settings?.business_name || tenant?.name} and adds starter services.
                        The owner can still edit everything in their dashboard.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-3">
                    {(templates.data ?? []).map((t) => (
                        <button
                            key={t.id}
                            type="button"
                            onClick={() => setChoice(t.id)}
                            className={`rounded-2xl border p-4 text-left transition-colors ${
                                choice === t.id ? "border-[#8cff2e]/50 bg-[#8cff2e]/10" : "border-border hover:bg-white/[0.03]"
                            }`}
                        >
                            <p className="font-medium text-foreground">{t.label}</p>
                            <p className="mt-1 text-sm text-muted-foreground">{t.description}</p>
                            <p className="mt-2 text-xs text-muted-foreground">Services: {t.services.join(" · ")}</p>
                        </button>
                    ))}
                    {templates.isLoading && <p className="text-sm text-muted-foreground">Loading templates…</p>}
                </div>
                <DialogFooter>
                    <Button variant="ghost" onClick={onClose}>Cancel</Button>
                    <Button disabled={!choice || apply.isPending} onClick={() => apply.mutate()}>
                        {apply.isPending ? "Setting up…" : "Apply template"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

export default function TenantsAdminPage() {
    const [search, setSearch] = useState("");
    const [tenantToDelete, setTenantToDelete] = useState<Tenant | null>(null);
    const [tenantToSetUp, setTenantToSetUp] = useState<Tenant | null>(null);
    const queryClient = useQueryClient();

    // Fetch all tenants
    const { data: tenants = [], isLoading } = useQuery<Tenant[]>({
        queryKey: ["admin-tenants"],
        queryFn: async (): Promise<Tenant[]> => {
            const response = await adminApi.getTenants(0, 100);
            return (Array.isArray(response) ? response : response.items).map((tenant) => tenant as unknown as Tenant);
        },
    });

    // Delete tenant mutation
    const deleteMutation = useMutation({
        mutationFn: async (tenantId: string) => {
            await adminApi.deleteTenant(tenantId);
        },
        onSuccess: () => {
            toast.success("Business deleted");
            queryClient.invalidateQueries({ queryKey: ["admin-tenants"] });
            setTenantToDelete(null);
        },
        onError: (error: any) => {
            toast.error(error.message || "Failed to delete business");
        },
    });

    // Filter by search
    const filteredTenants = tenants.filter((tenant) => {
        const searchLower = search.toLowerCase();
        return (
            tenant.name?.toLowerCase().includes(searchLower) ||
            tenant.email?.toLowerCase().includes(searchLower) ||
            tenant.settings?.business_name?.toLowerCase().includes(searchLower)
        );
    });

    // Calculate stats
    const totalTenants = tenants.length;
    const activeTenants = tenants.filter((t) => t.status === "active").length;
    const totalCalls = tenants.reduce((sum, t) => sum + (t.total_calls || 0), 0);
    const totalMinutes = tenants.reduce((sum, t) => sum + (t.total_minutes || 0), 0);

    if (isLoading) return <LoadingState label="Loading businesses…" />;

    return (
        <>
            <PageHeader
                eyebrow="Clients"
                title="Businesses"
                description="Every business using Calleem: plan, status and usage."
            />

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard label="Businesses" value={totalTenants} hint="All registered" icon={Building2} tone="lime" />
                <StatCard label="Active" value={activeTenants} hint="Currently active" icon={Activity} tone="green" />
                <StatCard label="Calls handled" value={totalCalls.toLocaleString()} hint="Across all businesses" icon={PhoneCall} tone="blue" />
                <StatCard label="Call minutes" value={Math.round(totalMinutes).toLocaleString()} hint="Total talk time" icon={Clock3} tone="slate" />
            </div>

            <Panel
                title={`All businesses (${filteredTenants.length})`}
                bodyClassName="p-0"
                actions={
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            placeholder="Search by name or email…"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="h-9 w-[280px] rounded-xl pl-9"
                        />
                    </div>
                }
            >
                {filteredTenants.length === 0 ? (
                    <EmptyState icon={Building2} title="No businesses found" hint={search ? "Try a different search." : undefined} />
                ) : (
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border text-left text-[11px] uppercase tracking-[0.06em] text-muted-foreground">
                                <th className="px-5 py-3 font-semibold">Business</th>
                                <th className="px-5 py-3 font-semibold">Plan</th>
                                <th className="px-5 py-3 font-semibold">Status</th>
                                <th className="px-5 py-3 text-right font-semibold">Calls</th>
                                <th className="px-5 py-3 text-right font-semibold">Minutes</th>
                                <th className="px-5 py-3 font-semibold">Joined</th>
                                <th className="w-24 px-5 py-3" />
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filteredTenants.map((tenant) => (
                                <tr key={tenant.id} className="group transition-colors hover:bg-white/[0.02]">
                                    <td className="px-5 py-3">
                                        <div className="flex items-center gap-3">
                                            <Avatar name={tenant.settings?.business_name || tenant.name} className="size-8" />
                                            <div className="min-w-0">
                                                <p className="truncate font-medium text-foreground">{tenant.settings?.business_name || tenant.name}</p>
                                                <p className="truncate text-xs text-muted-foreground">{tenant.email || "No email on file"}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-5 py-3">
                                        <Pill tone={tenant.plan === "free" || !tenant.plan ? "slate" : "lime"}>
                                            {(tenant.plan || "free").replace(/^\w/, (c) => c.toUpperCase())}
                                        </Pill>
                                    </td>
                                    <td className="px-5 py-3">
                                        <Pill dot tone={tenant.status === "active" ? "green" : "slate"}>
                                            {tenant.status === "active" ? "Active" : "Inactive"}
                                        </Pill>
                                    </td>
                                    <td className="px-5 py-3 text-right tabular-nums text-foreground">{(tenant.total_calls || 0).toLocaleString()}</td>
                                    <td className="px-5 py-3 text-right tabular-nums text-foreground">{Math.round(tenant.total_minutes || 0).toLocaleString()}</td>
                                    <td className="px-5 py-3 text-muted-foreground">
                                        {tenant.created_at ? format(new Date(tenant.created_at), "MMM d, yyyy") : "—"}
                                    </td>
                                    <td className="whitespace-nowrap px-5 py-3 text-right">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            title="Set up for a niche (plumber, law firm)"
                                            onClick={() => setTenantToSetUp(tenant)}
                                            className="size-8 text-muted-foreground opacity-60 hover:bg-white/5 hover:text-foreground group-hover:opacity-100"
                                        >
                                            <Wand2 className="size-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            title="Delete business"
                                            onClick={() => setTenantToDelete(tenant)}
                                            className="size-8 text-muted-foreground opacity-60 hover:bg-rose-500/10 hover:text-rose-300 group-hover:opacity-100"
                                        >
                                            <Trash2 className="size-4" />
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </Panel>

            <TemplateDialog tenant={tenantToSetUp} onClose={() => setTenantToSetUp(null)} />

            {/* Delete Confirmation Dialog */}
            <AlertDialog open={!!tenantToDelete} onOpenChange={() => setTenantToDelete(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Delete {tenantToDelete?.settings?.business_name || tenantToDelete?.name}?</AlertDialogTitle>
                        <AlertDialogDescription asChild>
                            <div>
                                This permanently deletes the business and everything that belongs to it:
                                <ul className="mt-2 ml-4 list-disc text-sm">
                                    <li>All users under this business</li>
                                    <li>All appointments</li>
                                    <li>All services</li>
                                    <li>All conversations</li>
                                    <li>Business configuration</li>
                                </ul>
                                <p className="mt-3 font-semibold text-rose-300">This cannot be undone.</p>
                            </div>
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel className="border-border bg-transparent text-foreground hover:bg-white/5">Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={() => tenantToDelete && deleteMutation.mutate(tenantToDelete.id)}
                            className="bg-rose-600 text-white hover:bg-rose-700"
                            disabled={deleteMutation.isPending}
                        >
                            {deleteMutation.isPending ? "Deleting…" : "Delete business"}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </>
    );
}
