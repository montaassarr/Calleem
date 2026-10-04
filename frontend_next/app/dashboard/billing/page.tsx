"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { toast } from "sonner";
import { AlertTriangle, CheckCircle2, Clock3, CreditCard, PhoneCall, PhoneForwarded, PauseCircle, Sparkles } from "lucide-react";
import { billingApi, BillingWallet, WalletHistoryEntry } from "@/lib/api/billing";
import { LEGAL } from "@/lib/legal";
import { quotePrice, USAGE_LIMITS } from "@/lib/pricing";

const card = "bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100";
const usd = (n: number) => n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: n % 1 ? 2 : 0 });
const PLAN_LABELS: Record<string, string> = { monthly: "Monthly plan", custom: "Custom plan" };

function historyLabel(entry: WalletHistoryEntry) {
    if (entry.type === "call") {
        const seconds = Math.round(entry.duration_seconds ?? 0);
        return `Call · ${Math.floor(seconds / 60)}m ${String(seconds % 60).padStart(2, "0")}s`;
    }
    if (entry.source === "trial") return "Free trial minutes";
    const label = entry.plan ? PLAN_LABELS[entry.plan] ?? "Plan" : "Extra minutes";
    return entry.source === "manual" ? `${label} · invoice` : label;
}

function StatusBanner({ wallet }: { wallet: BillingWallet }) {
    if (wallet.calls_paused) {
        return (
            <div className="mb-6 flex items-start gap-3 rounded-[20px] border border-red-200 bg-red-50 px-5 py-4">
                <PauseCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
                <div>
                    <p className="font-semibold text-red-900">Your AI receptionist is paused</p>
                    <p className="mt-0.5 text-sm text-red-800/80">
                        You've used all your minutes. Add minutes below and it starts answering again within a minute.
                        {wallet.fallback_number ? ` Until then, calls go to ${wallet.fallback_number}.` : " Until then, calls are not answered."}
                    </p>
                </div>
            </div>
        );
    }
    if (wallet.low_balance && !wallet.billing_exempt) {
        return (
            <div className="mb-6 flex items-start gap-3 rounded-[20px] border border-amber-200 bg-amber-50 px-5 py-4">
                <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
                <div>
                    <p className="font-semibold text-amber-900">You're running low on minutes</p>
                    <p className="mt-0.5 text-sm text-amber-800/80">
                        {Math.max(0, Math.floor(wallet.minutes_balance))} minutes left. When they run out, your AI receptionist pauses until you add more.
                    </p>
                </div>
            </div>
        );
    }
    return null;
}

function UsageSlider({
    label,
    display,
    value,
    min,
    max,
    step,
    onChange,
}: {
    label: string;
    display: string;
    value: number;
    min: number;
    max: number;
    step: number;
    onChange: (value: number) => void;
}) {
    return (
        <label className="block">
            <div className="mb-3 flex items-end justify-between">
                <span className="text-sm font-semibold text-gray-900">{label}</span>
                <span className="text-2xl font-bold tracking-tight text-[#187848]">{display}</span>
            </div>
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={value}
                onChange={(e) => onChange(Number(e.target.value))}
                className="w-full cursor-pointer accent-[#187848]"
            />
            <div className="mt-1 flex justify-between text-xs text-gray-400">
                <span>{min.toLocaleString()}</span>
                <span>{max.toLocaleString()}</span>
            </div>
        </label>
    );
}

/** Usage-based plan, priced like the landing page calculator. */
function PlanBuilder({
    wallet,
    busy,
    onStart,
    onManage,
}: {
    wallet: BillingWallet;
    busy: boolean;
    onStart: (calls: number, avgMinutes: number) => void;
    onManage: () => void;
}) {
    const queryClient = useQueryClient();
    const [calls, setCalls] = useState(wallet.plan_calls ?? 300);
    const [avgMinutes, setAvgMinutes] = useState(wallet.plan_avg_minutes ?? 3);
    const quote = quotePrice(calls, avgMinutes);
    const online = wallet.checkout.provider === "stripe";
    const hasPlan = wallet.has_subscription;
    const unchanged = hasPlan && calls === wallet.plan_calls && avgMinutes === wallet.plan_avg_minutes;

    const change = useMutation({
        mutationFn: () => billingApi.changePlan(calls, avgMinutes),
        onSuccess: () => {
            toast.success("Plan changed. The new price and minutes start at your next renewal.");
            queryClient.invalidateQueries({ queryKey: ["billing-wallet"] });
        },
        onError: (error: Error) => toast.error(error.message || "Could not change the plan"),
    });

    const primary = "w-full rounded-full bg-white px-4 py-3 text-center text-sm font-bold text-[#0a4c2f] transition-colors hover:bg-white/90 disabled:opacity-60";

    return (
        <div className={`${card} p-6 md:p-8`}>
            <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
                <div className="space-y-8">
                    <UsageSlider
                        label="Calls per month"
                        display={calls.toLocaleString()}
                        value={calls}
                        min={USAGE_LIMITS.minCalls}
                        max={USAGE_LIMITS.maxCalls}
                        step={100}
                        onChange={setCalls}
                    />
                    <UsageSlider
                        label="Average call length"
                        display={`${avgMinutes} min`}
                        value={avgMinutes}
                        min={USAGE_LIMITS.minAvgMinutes}
                        max={USAGE_LIMITS.maxAvgMinutes}
                        step={0.5}
                        onChange={setAvgMinutes}
                    />
                    <p className="text-xs leading-relaxed text-gray-500">
                        Pick what you expect. Your plan gives you {quote.minutes.toLocaleString()} call minutes each month, counted by
                        the second. Unused minutes carry over, and you can add extra minutes any time. More than{" "}
                        {USAGE_LIMITS.maxCalls.toLocaleString()} calls a month? <Link href="/contact" className="font-semibold text-[#187848] hover:underline">Talk to us</Link>.
                    </p>
                    {wallet.plan_next && (
                        <p className="rounded-xl bg-[#187848]/5 px-4 py-3 text-sm text-[#0a4c2f]">
                            From your next renewal: {wallet.plan_next.calls.toLocaleString()} calls of {wallet.plan_next.avg_minutes} min (
                            {wallet.plan_next.minutes.toLocaleString()} minutes) for {usd(wallet.plan_next.price_usd)}/month.
                        </p>
                    )}
                </div>

                <div className="flex flex-col rounded-2xl bg-gradient-to-b from-[#187848] to-[#0a4c2f] p-6 text-white">
                    <p className="text-sm font-medium text-white/70">{hasPlan ? "Your monthly plan" : "Monthly plan"}</p>
                    <p className="mt-2 text-[44px] font-bold leading-none tracking-tight">
                        {usd(quote.price)}
                        <span className="text-base font-medium text-white/60">/month</span>
                    </p>
                    <ul className="mt-5 space-y-2 text-sm text-white/85">
                        <li className="flex gap-2"><CheckCircle2 className="h-4 w-4 shrink-0" /> {quote.minutes.toLocaleString()} call minutes every month</li>
                        <li className="flex gap-2"><CheckCircle2 className="h-4 w-4 shrink-0" /> Unused minutes carry over</li>
                        <li className="flex gap-2">
                            <CheckCircle2 className="h-4 w-4 shrink-0" /> Extra minutes {usd(wallet.checkout.topup_price_per_minute_usd)} each
                        </li>
                    </ul>
                    <div className="mt-6 flex-1" />
                    {!online ? (
                        <Link href={LEGAL.contactUrl} className={primary}>
                            Request this plan
                        </Link>
                    ) : hasPlan ? (
                        <div className="space-y-2">
                            <button disabled={busy || unchanged || change.isPending} onClick={() => change.mutate()} className={primary}>
                                {change.isPending ? "Saving…" : unchanged ? "This is your plan" : "Change to this plan"}
                            </button>
                            <button
                                disabled={busy}
                                onClick={onManage}
                                className="w-full rounded-full px-4 py-2 text-sm font-semibold text-white/85 hover:bg-white/10 disabled:opacity-60"
                            >
                                Card, invoices or cancel
                            </button>
                        </div>
                    ) : (
                        <button disabled={busy} onClick={() => onStart(calls, avgMinutes)} className={primary}>
                            Start monthly plan
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}

function FallbackNumberCard({ wallet }: { wallet: BillingWallet }) {
    const queryClient = useQueryClient();
    const [value, setValue] = useState(wallet.fallback_number ?? "");
    useEffect(() => setValue(wallet.fallback_number ?? ""), [wallet.fallback_number]);

    const save = useMutation({
        mutationFn: () => billingApi.setFallbackNumber(value.trim()),
        onSuccess: () => {
            toast.success(value.trim() ? "Backup number saved" : "Backup number removed");
            queryClient.invalidateQueries({ queryKey: ["billing-wallet"] });
        },
        onError: (error: Error) => toast.error(error.message || "Could not save the number"),
    });

    return (
        <div className={`${card} p-6`}>
            <div className="flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-[#187848] to-[#0a4c2f] text-white">
                    <PhoneForwarded className="h-5 w-5" />
                </div>
                <div>
                    <h3 className="font-bold text-gray-900">If you run out of minutes</h3>
                    <p className="text-sm text-gray-500">Send callers to your own phone instead of leaving them unanswered.</p>
                </div>
            </div>
            <form
                className="mt-5 flex flex-col gap-3 sm:flex-row"
                onSubmit={(e) => {
                    e.preventDefault();
                    save.mutate();
                }}
            >
                <input
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    placeholder="+14155550123"
                    inputMode="tel"
                    className="h-11 flex-1 rounded-xl border border-gray-200 bg-white px-4 text-sm text-gray-900 outline-none focus:border-[#187848]"
                />
                <button
                    type="submit"
                    disabled={save.isPending || value.trim() === (wallet.fallback_number ?? "")}
                    className="h-11 rounded-full bg-[#0a4c2f] px-6 text-sm font-semibold text-white transition-colors hover:bg-[#187848] disabled:opacity-50"
                >
                    {save.isPending ? "Saving…" : "Save"}
                </button>
            </form>
            <p className="mt-2 text-xs text-gray-500">
                Use international format. Pick a mobile that does not forward calls back to your Calleem number, or calls would loop.
            </p>
        </div>
    );
}

function History() {
    const history = useInfiniteQuery({
        queryKey: ["billing-history"],
        queryFn: ({ pageParam }) => billingApi.getHistory(pageParam, 20),
        initialPageParam: 1,
        getNextPageParam: (last) => (last.has_more ? last.page + 1 : undefined),
    });
    const entries = history.data?.pages.flatMap((p) => p.entries) ?? [];

    return (
        <div className={`${card} overflow-hidden`}>
            <div className="border-b border-gray-100 px-6 py-4">
                <h3 className="font-bold text-gray-900">History</h3>
                <p className="text-sm text-gray-500">Minutes added and minutes used by calls</p>
            </div>
            {history.isLoading ? (
                <p className="px-6 py-8 text-sm text-gray-500">Loading…</p>
            ) : entries.length === 0 ? (
                <p className="px-6 py-8 text-sm text-gray-500">Nothing yet. Your calls and payments will show up here.</p>
            ) : (
                <ul className="divide-y divide-gray-100">
                    {entries.map((entry, i) => (
                        <li key={`${entry.created_at}-${i}`} className="flex items-center gap-4 px-6 py-3">
                            <div className={`grid h-9 w-9 shrink-0 place-items-center rounded-full ${entry.type === "call" ? "bg-gray-100 text-gray-500" : "bg-[#187848]/10 text-[#187848]"}`}>
                                {entry.type === "call" ? <PhoneCall className="h-4 w-4" /> : <CreditCard className="h-4 w-4" />}
                            </div>
                            <div className="min-w-0 flex-1">
                                <p className="truncate text-sm font-medium text-gray-900">{historyLabel(entry)}</p>
                                <p className="text-xs text-gray-500">{entry.created_at ? format(new Date(entry.created_at), "MMM d, yyyy · HH:mm") : ""}</p>
                            </div>
                            <span className={`text-sm font-semibold tabular-nums ${entry.minutes >= 0 ? "text-[#187848]" : "text-gray-700"}`}>
                                {entry.minutes >= 0 ? "+" : "−"}
                                {Math.abs(entry.minutes).toLocaleString(undefined, { maximumFractionDigits: 1 })} min
                            </span>
                        </li>
                    ))}
                </ul>
            )}
            {history.hasNextPage && (
                <div className="border-t border-gray-100 px-6 py-3 text-center">
                    <button
                        onClick={() => history.fetchNextPage()}
                        disabled={history.isFetchingNextPage}
                        className="text-sm font-semibold text-[#187848] hover:underline disabled:opacity-50"
                    >
                        {history.isFetchingNextPage ? "Loading…" : "Show more"}
                    </button>
                </div>
            )}
        </div>
    );
}

function BillingContent() {
    const searchParams = useSearchParams();
    const justPaid = searchParams.get("paid") === "1";
    const [opening, setOpening] = useState(false);

    const { data: wallet, isLoading, isError } = useQuery({
        queryKey: ["billing-wallet"],
        queryFn: () => billingApi.getWallet(),
        // After a checkout, Stripe's notification can take a few seconds; keep checking briefly.
        refetchInterval: justPaid ? 5000 : false,
    });

    // All three go to a Stripe-hosted page; buttons stay disabled until the browser leaves.
    const goTo = async (getUrl: () => Promise<string>) => {
        setOpening(true);
        try {
            window.location.href = await getUrl();
        } catch (error) {
            toast.error(error instanceof Error ? error.message : "Could not open the payment page");
            setOpening(false);
        }
    };
    const startPlan = (calls: number, avgMinutes: number) =>
        goTo(async () => (await billingApi.createCheckout({ kind: "plan", calls, avg_minutes: avgMinutes })).checkout_url);
    const buyMinutes = (minutes: number) =>
        goTo(async () => (await billingApi.createCheckout({ kind: "minutes", minutes })).checkout_url);
    const manage = () => goTo(async () => (await billingApi.openPortal()).portal_url);

    if (isLoading) return <p className="text-sm text-gray-500">Loading billing…</p>;
    if (isError || !wallet) return <p className="text-sm text-red-600">Could not load your billing details. Please refresh the page.</p>;

    const minutesLeft = Math.max(0, Math.floor(wallet.minutes_balance));
    const fill = wallet.plan_minutes ? Math.min(100, (Math.max(0, wallet.minutes_balance) / wallet.plan_minutes) * 100) : null;

    return (
        <div>
            <div className="mb-8">
                <h1 className="mb-1 text-[32px] font-bold leading-none tracking-tight text-gray-900">Billing</h1>
                <p className="text-[14px] font-medium text-gray-500">Minutes for your AI receptionist. Each call uses minutes, counted by the second.</p>
            </div>

            {justPaid && (
                <div className="mb-6 flex items-start gap-3 rounded-[20px] border border-emerald-200 bg-emerald-50 px-5 py-4">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" />
                    <p className="text-sm text-emerald-900">Thank you! Your payment went through. The minutes appear here within a minute.</p>
                </div>
            )}
            <StatusBanner wallet={wallet} />

            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <div className={`${card} p-6`}>
                    <div className="flex items-center gap-2 text-sm font-medium text-gray-500">
                        <Clock3 className="h-4 w-4" /> Minutes left
                    </div>
                    <p className={`mt-3 text-[40px] font-bold leading-none tracking-tight ${wallet.calls_paused ? "text-red-600" : "text-gray-900"}`}>
                        {minutesLeft.toLocaleString()}
                    </p>
                    {fill !== null && (
                        <div className="mt-4 h-2 overflow-hidden rounded-full bg-gray-100">
                            <div className="h-full rounded-full bg-[#187848]" style={{ width: `${fill}%` }} />
                        </div>
                    )}
                    <p className="mt-3 text-xs text-gray-500">About {Math.floor(minutesLeft / 3).toLocaleString()} calls of 3 minutes</p>
                </div>

                <div className={`${card} p-6`}>
                    <div className="flex items-center gap-2 text-sm font-medium text-gray-500">
                        <Sparkles className="h-4 w-4" /> Plan
                    </div>
                    <p className="mt-3 text-[28px] font-bold leading-none tracking-tight text-gray-900">{wallet.plan_name}</p>
                    <p className="mt-3 text-xs text-gray-500">
                        {wallet.plan === "trial"
                            ? "Free minutes to try Calleem. Choose your plan below to keep going."
                            : [
                                  wallet.plan_minutes ? `${wallet.plan_minutes.toLocaleString()} min/month` : null,
                                  wallet.plan_price_usd ? `${usd(wallet.plan_price_usd)}/month` : null,
                                  wallet.period_end ? `renews ${format(new Date(wallet.period_end), "MMM d")}` : null,
                              ]
                                  .filter(Boolean)
                                  .join(" · ") || "Active"}
                    </p>
                </div>

                <div className={`${card} p-6`}>
                    <div className="flex items-center gap-2 text-sm font-medium text-gray-500">
                        <PhoneCall className="h-4 w-4" /> This month
                    </div>
                    <p className="mt-3 text-[28px] font-bold leading-none tracking-tight text-gray-900">
                        {wallet.this_month.calls.toLocaleString()} <span className="text-base font-medium text-gray-500">calls</span>
                    </p>
                    <p className="mt-3 text-xs text-gray-500">{Math.round(wallet.this_month.minutes).toLocaleString()} minutes used</p>
                </div>
            </div>

            <h2 className="mb-4 mt-10 text-xl font-bold text-gray-900">{wallet.has_subscription ? "Your plan" : "Choose your plan"}</h2>
            <PlanBuilder wallet={wallet} busy={opening} onStart={startPlan} onManage={manage} />

            <div className={`${card} mt-4 flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between`}>
                <div>
                    <h3 className="font-bold text-gray-900">Need more minutes?</h3>
                    <p className="text-sm text-gray-500">
                        Extra minutes are {usd(wallet.checkout.topup_price_per_minute_usd)} each and never expire.
                    </p>
                </div>
                <div className="flex flex-wrap gap-2">
                    {wallet.checkout.provider === "stripe" ? (
                        wallet.checkout.topups.map((topup) => (
                            <button
                                key={topup.minutes}
                                disabled={opening}
                                onClick={() => buyMinutes(topup.minutes)}
                                className="rounded-full border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-900 transition-colors hover:bg-gray-50 disabled:opacity-60"
                            >
                                +{topup.minutes.toLocaleString()} min · {usd(topup.price_usd)}
                            </button>
                        ))
                    ) : (
                        <Link
                            href={LEGAL.contactUrl}
                            className="rounded-full border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-900 transition-colors hover:bg-gray-50"
                        >
                            Request minutes
                        </Link>
                    )}
                </div>
            </div>

            <div className="mt-10 grid grid-cols-1 gap-4 lg:grid-cols-2">
                <FallbackNumberCard wallet={wallet} />
                <History />
            </div>
        </div>
    );
}

export default function BillingPage() {
    return (
        <Suspense fallback={<p className="text-sm text-gray-500">Loading billing…</p>}>
            <BillingContent />
        </Suspense>
    );
}
