"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { toast } from "sonner";
import { CircleDollarSign, Clock3, PlusCircle, RefreshCw, Settings2, ShieldAlert, ShieldCheck, TrendingDown, TrendingUp, Wallet } from "lucide-react";
import { adminApi, TenantBillingSummary } from "@/lib/api/admin";
import { PRICING, quotePrice } from "@/lib/pricing";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Avatar, CallsStatusPill, EmptyState, LoadingState, PageHeader, Panel, PlanPill, StatCard } from "@/components/admin/AdminUI";

// Stripe Malaysia on a US card in USD: 3% + 1% international + 2% conversion (+ RM1, ignored here).
const STRIPE_FEE_RATE = 0.06;
// Usage levels shown in the pricing check panel.
const EXAMPLE_USAGE: [number, number][] = [
    [100, 3],
    [300, 3],
    [500, 3],
    [1000, 4],
    [2500, 5],
];

const usd = (n: number, digits = 0) =>
    n.toLocaleString("en-US", { style: "currency", currency: "USD", minimumFractionDigits: digits, maximumFractionDigits: digits });

const PAYMENT_TYPES = [
    { id: "monthly", label: "Monthly plan" },
    { id: "minutes", label: "Extra minutes" },
    { id: "custom", label: "Custom deal" },
] as const;

type PaymentType = (typeof PAYMENT_TYPES)[number]["id"];

function RecordPaymentDialog({
    tenant,
    topupRate,
    onClose,
}: {
    tenant: TenantBillingSummary | null;
    topupRate: number;
    onClose: () => void;
}) {
    const queryClient = useQueryClient();
    const [type, setType] = useState<PaymentType>("monthly");
    const [calls, setCalls] = useState("300");
    const [avgMinutes, setAvgMinutes] = useState("3");
    const [minutes, setMinutes] = useState("");
    const [amount, setAmount] = useState("");
    const [currency, setCurrency] = useState("USD");
    const [reference, setReference] = useState("");
    const [note, setNote] = useState("");

    // Monthly plans are priced by the same usage model clients see (lib/pricing.ts).
    const fillFromUsage = (nextCalls: string, nextAvg: string) => {
        const quote = quotePrice(Number(nextCalls) || 0, Number(nextAvg) || 0);
        setMinutes(String(quote.minutes));
        setAmount(String(quote.price));
    };

    const choose = (next: PaymentType) => {
        setType(next);
        if (next === "monthly") fillFromUsage(calls, avgMinutes);
        else if (next === "minutes") {
            setMinutes("100");
            setAmount(String(100 * topupRate));
        } else {
            setMinutes("");
            setAmount("");
        }
    };

    useEffect(() => {
        if (!tenant) return;
        setCalls("300");
        setAvgMinutes("3");
        setType("monthly");
        fillFromUsage("300", "3");
        setCurrency("USD");
        setReference("");
        setNote("");
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [tenant]);

    const save = useMutation({
        mutationFn: () =>
            adminApi.addMinutes(tenant!.tenant_id, {
                plan: type === "minutes" ? undefined : type,
                ...(type === "monthly" ? { calls: Number(calls), avg_minutes: Number(avgMinutes) } : {}),
                minutes: Number(minutes),
                amount_paid: amount ? Number(amount) : undefined,
                currency: currency || "USD",
                reference: reference || undefined,
                note: note || undefined,
            }),
        onSuccess: () => {
            toast.success(`Added ${Number(minutes).toLocaleString()} minutes to ${tenant?.name}`);
            queryClient.invalidateQueries({ queryKey: ["admin-billing"] });
            onClose();
        },
        onError: (error: Error) => toast.error(error.message || "Could not record the payment"),
    });

    const valid = Number(minutes) > 0;

    return (
        <Dialog open={!!tenant} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Record a payment</DialogTitle>
                    <DialogDescription>
                        {tenant?.name} has {Math.round(tenant?.minutes_balance ?? 0).toLocaleString()} minutes left. Use this for payments
                        received outside Stripe, such as a bank transfer for an invoice.
                    </DialogDescription>
                </DialogHeader>

                <div className="grid gap-4">
                    <div className="grid grid-cols-3 gap-2">
                        {PAYMENT_TYPES.map((option) => (
                            <button
                                key={option.id}
                                type="button"
                                onClick={() => choose(option.id)}
                                className={`rounded-xl border px-3 py-2 text-left text-sm transition-colors ${
                                    type === option.id
                                        ? "border-[#8cff2e]/50 bg-[#8cff2e]/10 text-foreground"
                                        : "border-border text-muted-foreground hover:bg-white/[0.03]"
                                }`}
                            >
                                {option.label}
                            </button>
                        ))}
                    </div>

                    {type === "monthly" && (
                        <div className="grid grid-cols-2 gap-3">
                            <div className="grid gap-1.5">
                                <Label htmlFor="calls">Calls per month</Label>
                                <Input
                                    id="calls"
                                    type="number"
                                    min="100"
                                    step="100"
                                    value={calls}
                                    onChange={(e) => {
                                        setCalls(e.target.value);
                                        fillFromUsage(e.target.value, avgMinutes);
                                    }}
                                />
                            </div>
                            <div className="grid gap-1.5">
                                <Label htmlFor="avg">Average call (min)</Label>
                                <Input
                                    id="avg"
                                    type="number"
                                    min="1"
                                    step="0.5"
                                    value={avgMinutes}
                                    onChange={(e) => {
                                        setAvgMinutes(e.target.value);
                                        fillFromUsage(calls, e.target.value);
                                    }}
                                />
                            </div>
                        </div>
                    )}

                    <div className="grid grid-cols-2 gap-3">
                        <div className="grid gap-1.5">
                            <Label htmlFor="minutes">Minutes to add</Label>
                            <Input id="minutes" type="number" min="1" value={minutes} onChange={(e) => setMinutes(e.target.value)} />
                        </div>
                        <div className="grid gap-1.5">
                            <Label htmlFor="amount">Amount received</Label>
                            <div className="flex gap-2">
                                <Input id="amount" type="number" min="0" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} />
                                <Input
                                    aria-label="Currency"
                                    value={currency}
                                    maxLength={3}
                                    onChange={(e) => setCurrency(e.target.value.toUpperCase())}
                                    className="w-[70px] uppercase"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="grid gap-1.5">
                        <Label htmlFor="reference">Invoice or payment reference</Label>
                        <Input id="reference" placeholder="e.g. INV-0012 or bank transfer ref" value={reference} onChange={(e) => setReference(e.target.value)} />
                        <p className="text-xs text-muted-foreground">The same reference can't be recorded twice, so a payment is never counted double.</p>
                    </div>

                    <div className="grid gap-1.5">
                        <Label htmlFor="note">Note (optional)</Label>
                        <Input id="note" value={note} onChange={(e) => setNote(e.target.value)} />
                    </div>

                    {type !== "minutes" && (
                        <p className="text-xs text-muted-foreground">Starts a new 30-day period for this business.</p>
                    )}
                </div>

                <DialogFooter>
                    <Button variant="ghost" onClick={onClose}>Cancel</Button>
                    <Button disabled={!valid || save.isPending} onClick={() => save.mutate()}>
                        {save.isPending ? "Saving…" : `Add ${valid ? Number(minutes).toLocaleString() : ""} minutes`}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

function BillingSettingsDialog({ tenant, onClose }: { tenant: TenantBillingSummary | null; onClose: () => void }) {
    const queryClient = useQueryClient();
    const [fallback, setFallback] = useState("");
    const [exempt, setExempt] = useState(false);

    useEffect(() => {
        if (!tenant) return;
        setFallback(tenant.fallback_number ?? "");
        setExempt(tenant.billing_exempt);
    }, [tenant]);

    const save = useMutation({
        mutationFn: () => adminApi.updateBillingSettings(tenant!.tenant_id, { fallback_number: fallback.trim(), billing_exempt: exempt }),
        onSuccess: () => {
            toast.success("Billing settings saved");
            queryClient.invalidateQueries({ queryKey: ["admin-billing"] });
            onClose();
        },
        onError: (error: Error) => toast.error(error.message || "Could not save the settings"),
    });

    return (
        <Dialog open={!!tenant} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Billing settings</DialogTitle>
                    <DialogDescription>{tenant?.name}</DialogDescription>
                </DialogHeader>

                <div className="grid gap-5">
                    <div className="grid gap-1.5">
                        <Label htmlFor="fallback">Backup number while paused</Label>
                        <Input id="fallback" placeholder="+14155550123" value={fallback} onChange={(e) => setFallback(e.target.value)} />
                        <p className="text-xs text-muted-foreground">
                            When this business runs out of minutes, its callers are forwarded here instead of hearing nothing. Use a mobile number
                            that does <strong>not</strong> forward back to its Calleem number. Leave empty to remove.
                        </p>
                    </div>

                    <div className="flex items-start justify-between gap-4 rounded-xl border border-border p-4">
                        <div>
                            <p className="text-sm font-medium text-foreground">Never pause this business</p>
                            <p className="mt-1 text-xs text-muted-foreground">For your own demo business or a client on a special deal. Minutes are still counted.</p>
                        </div>
                        <Switch checked={exempt} onCheckedChange={setExempt} />
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="ghost" onClick={onClose}>Cancel</Button>
                    <Button disabled={save.isPending} onClick={() => save.mutate()}>
                        {save.isPending ? "Saving…" : "Save"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

export default function AdminBillingPage() {
    const queryClient = useQueryClient();
    const [paymentTenant, setPaymentTenant] = useState<TenantBillingSummary | null>(null);
    const [settingsTenant, setSettingsTenant] = useState<TenantBillingSummary | null>(null);

    const { data, isLoading, refetch, isFetching } = useQuery({
        queryKey: ["admin-billing"],
        queryFn: () => adminApi.getBillingOverview(),
    });

    const sync = useMutation({
        mutationFn: () => adminApi.syncBilling(),
        onSuccess: (res) => {
            toast.success(`Checked ${res.tenants} businesses: ${res.paused} paused, ${res.resumed} turned back on`);
            queryClient.invalidateQueries({ queryKey: ["admin-billing"] });
        },
        onError: (error: Error) => toast.error(error.message || "Sync failed"),
    });

    if (isLoading) return <LoadingState label="Loading billing…" />;

    const ps = data?.platform_summary;
    const marginPct = ps && ps.revenue_30d_usd > 0 ? Math.round((ps.margin_30d_usd / ps.revenue_30d_usd) * 100) : null;
    const tenants = data?.tenants ?? [];

    return (
        <>
            <PageHeader
                eyebrow="Revenue"
                title="Billing"
                description="Minutes, payments and voice costs for every business. Record invoice payments here."
                actions={
                    <>
                        <Button
                            variant="outline"
                            className="border-border bg-transparent text-foreground hover:bg-white/5"
                            disabled={sync.isPending}
                            onClick={() => sync.mutate()}
                            title="Pause businesses with no minutes and turn paid ones back on"
                        >
                            <ShieldCheck className="size-4" /> {sync.isPending ? "Checking…" : "Re-check numbers"}
                        </Button>
                        <Button
                            variant="outline"
                            className="border-border bg-transparent text-foreground hover:bg-white/5"
                            onClick={() => refetch()}
                        >
                            <RefreshCw className={`size-4 ${isFetching ? "animate-spin" : ""}`} /> Refresh
                        </Button>
                    </>
                }
            />

            {ps && !ps.enforcement_enabled && (
                <div className="flex items-start gap-3 rounded-2xl border border-amber-400/25 bg-amber-400/[0.06] px-5 py-4 text-sm">
                    <ShieldAlert className="mt-0.5 size-4 shrink-0 text-amber-300" />
                    <div>
                        <p className="font-medium text-amber-200">Call cut-off is off</p>
                        <p className="mt-0.5 text-amber-100/70">
                            Minutes are counted for every call, but no business is paused when it runs out. Switch it on by deploying with{" "}
                            <code className="rounded bg-black/30 px-1.5 py-0.5 text-xs">BILLING_ENFORCEMENT_ENABLED=true</code>, then press Re-check numbers.
                        </p>
                    </div>
                </div>
            )}

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard label="Revenue · 30 days" value={usd(ps?.revenue_30d_usd ?? 0)} hint={`${ps?.paying_tenants ?? 0} paying ${ps?.paying_tenants === 1 ? "business" : "businesses"}`} icon={CircleDollarSign} tone="green" />
                <StatCard label="Voice cost · 30 days" value={usd(ps?.vapi_cost_30d_usd ?? 0, 2)} hint="What Vapi charged for those calls" icon={TrendingDown} tone="amber" />
                <StatCard
                    label="Margin · 30 days"
                    value={usd(ps?.margin_30d_usd ?? 0)}
                    hint={marginPct === null ? "No payments yet" : `${marginPct}% of revenue`}
                    icon={TrendingUp}
                    tone={(ps?.margin_30d_usd ?? 0) >= 0 ? "lime" : "red"}
                />
                <StatCard
                    label="Minutes owed"
                    value={Math.round(ps?.minutes_owed ?? 0).toLocaleString()}
                    hint={`Prepaid, not used yet · ${ps?.paused_tenants ?? 0} paused`}
                    icon={Clock3}
                    tone="blue"
                />
            </div>

            <Panel title={`Businesses (${tenants.length})`} description="Minutes left and the last 30 days of calls, payments and voice costs" bodyClassName="p-0">
                {tenants.length === 0 ? (
                    <EmptyState icon={Wallet} title="No businesses yet" />
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full min-w-[980px] text-sm [&_td]:whitespace-nowrap [&_th]:whitespace-nowrap">
                            <thead>
                                <tr className="border-b border-border text-left text-[11px] uppercase tracking-[0.06em] text-muted-foreground">
                                    <th className="px-5 py-3 font-semibold">Business</th>
                                    <th className="px-5 py-3 font-semibold">Plan</th>
                                    <th className="px-5 py-3 font-semibold">Calls</th>
                                    <th className="px-5 py-3 text-right font-semibold">Minutes left</th>
                                    <th className="px-5 py-3 text-right font-semibold">Used · 30d</th>
                                    <th className="px-5 py-3 text-right font-semibold">Paid · 30d</th>
                                    <th className="px-5 py-3 text-right font-semibold">Voice cost</th>
                                    <th className="px-5 py-3 text-right font-semibold">Margin</th>
                                    <th className="px-5 py-3" />
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border">
                                {tenants.map((t) => (
                                    <tr key={t.tenant_id} className="transition-colors hover:bg-white/[0.02]">
                                        <td className="px-5 py-3">
                                            <div className="flex items-center gap-3">
                                                <Avatar name={t.name} className="size-8" />
                                                <div className="min-w-0">
                                                    <p className="truncate font-medium text-foreground">{t.name || "—"}</p>
                                                    <p className="truncate text-xs text-muted-foreground">
                                                        {t.billing_period_end ? `Period ends ${format(new Date(t.billing_period_end), "MMM d")}` : t.email}
                                                    </p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-5 py-3"><PlanPill plan={t.billing_plan} /></td>
                                        <td className="px-5 py-3">
                                            <CallsStatusPill paused={t.calls_paused} exempt={t.billing_exempt} minutes={t.minutes_balance} />
                                        </td>
                                        <td className="px-5 py-3 text-right tabular-nums">
                                            <span className={t.minutes_balance <= 0 ? "text-rose-300" : t.minutes_balance <= 30 ? "text-amber-300" : "text-foreground"}>
                                                {Math.round(t.minutes_balance).toLocaleString()}
                                            </span>
                                        </td>
                                        <td className="px-5 py-3 text-right tabular-nums text-muted-foreground">
                                            {Math.round(t.minutes_30d).toLocaleString()} min · {t.calls_30d} calls
                                        </td>
                                        <td className="px-5 py-3 text-right tabular-nums text-foreground">{usd(t.revenue_30d_usd)}</td>
                                        <td className="px-5 py-3 text-right tabular-nums text-amber-200/80">{usd(t.vapi_cost_30d_usd, 2)}</td>
                                        <td className={`px-5 py-3 text-right tabular-nums ${t.margin_30d_usd >= 0 ? "text-emerald-300" : "text-rose-300"}`}>
                                            {usd(t.margin_30d_usd)}
                                        </td>
                                        <td className="px-5 py-3">
                                            <div className="flex items-center justify-end gap-1">
                                                <Button size="sm" onClick={() => setPaymentTenant(t)}>
                                                    <PlusCircle className="size-4" /> Payment
                                                </Button>
                                                <Button
                                                    size="icon"
                                                    variant="ghost"
                                                    title="Billing settings"
                                                    className="size-8 text-muted-foreground hover:text-foreground"
                                                    onClick={() => setSettingsTenant(t)}
                                                >
                                                    <Settings2 className="size-4" />
                                                </Button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </Panel>

            <Panel
                title="Pricing check"
                description={`What clients pay at different usage levels (same model as the landing page), and what you keep after the cost model and ~${STRIPE_FEE_RATE * 100}% Stripe fees. Compare the cost per minute with the real Vapi cost above once calls come in.`}
                bodyClassName="p-0"
            >
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[760px] text-sm [&_td]:whitespace-nowrap [&_th]:whitespace-nowrap">
                        <thead>
                            <tr className="border-b border-border text-left text-[11px] uppercase tracking-[0.06em] text-muted-foreground">
                                <th className="px-5 py-3 font-semibold">Usage</th>
                                <th className="px-5 py-3 text-right font-semibold">Minutes</th>
                                <th className="px-5 py-3 text-right font-semibold">Client pays</th>
                                <th className="px-5 py-3 text-right font-semibold">Cost model</th>
                                <th className="px-5 py-3 text-right font-semibold">Stripe</th>
                                <th className="px-5 py-3 text-right font-semibold">You keep</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {EXAMPLE_USAGE.map(([calls, avg]) => {
                                const quote = quotePrice(calls, avg);
                                const fee = quote.price * STRIPE_FEE_RATE;
                                const keep = quote.price - quote.totalCost - fee;
                                const keepPct = Math.round((keep / quote.price) * 100);
                                return (
                                    <tr key={`${calls}-${avg}`}>
                                        <td className="px-5 py-3 text-foreground">{calls.toLocaleString()} calls × {avg} min</td>
                                        <td className="px-5 py-3 text-right tabular-nums text-muted-foreground">{quote.minutes.toLocaleString()}</td>
                                        <td className="px-5 py-3 text-right tabular-nums text-foreground">{usd(quote.price)}/mo</td>
                                        <td className="px-5 py-3 text-right tabular-nums text-amber-200/80">{usd(quote.totalCost)}</td>
                                        <td className="px-5 py-3 text-right tabular-nums text-amber-200/80">{usd(fee)}</td>
                                        <td className={`px-5 py-3 text-right tabular-nums ${keepPct >= 40 ? "text-emerald-300" : "text-amber-200"}`}>
                                            {usd(keep)} · {keepPct}%
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
                <p className="border-t border-border px-5 py-3 text-xs text-muted-foreground">
                    Cost model: {usd(PRICING.costPerMinute, 3)}/min + {usd(PRICING.costPerCall, 2)}/call + {usd(PRICING.infraPerMonth)}/month per business,
                    target margin {Math.round(PRICING.margin * 100)}%. Extra minutes: {usd(data?.topup_price_per_minute_usd ?? 0, 2)} each. Change these in
                    lib/pricing.ts and backend/services/usage_billing.py together.
                </p>
            </Panel>

            <RecordPaymentDialog tenant={paymentTenant} topupRate={data?.topup_price_per_minute_usd ?? 0.2} onClose={() => setPaymentTenant(null)} />
            <BillingSettingsDialog tenant={settingsTenant} onClose={() => setSettingsTenant(null)} />
        </>
    );
}
