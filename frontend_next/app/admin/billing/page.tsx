"use client";

import React, { useEffect, useState } from "react";
import { adminApi, BillingOverview, TenantBillingSummary } from "@/lib/api/admin";
import { toast } from "sonner";
import {
    DollarSign,
    TrendingUp,
    TrendingDown,
    Building2,
    Phone,
    Clock,
    CreditCard,
    PlusCircle,
    RefreshCw,
    ChevronDown,
    ChevronUp,
    Wifi,
    WifiOff,
} from "lucide-react";

// ─── helpers ────────────────────────────────────────────────────────────────

function fmt(n: number, decimals = 2) {
    return n.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

function planColor(plan: string) {
    if (plan === "pro") return "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
    if (plan === "enterprise") return "bg-violet-500/20 text-violetald-400 border border-violet-500/30";
    return "bg-slate-600/40 text-slate-400 border border-slate-600/40";
}

function statusDot(status: string) {
    return status === "active"
        ? <span className="flex items-center gap-1.5 text-emerald-400"><Wifi className="w-3 h-3" /> Active</span>
        : <span className="flex items-center gap-1.5 text-slate-500"><WifiOff className="w-3 h-3" /> {status}</span>;
}

function creditBar(balance: number, subscription: number) {
    if (subscription <= 0) return null;
    const pct = Math.max(0, Math.min(100, (balance / subscription) * 100));
    const color = pct > 50 ? "bg-emerald-500" : pct > 20 ? "bg-amber-500" : "bg-red-500";
    return (
        <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden mt-1">
            <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
        </div>
    );
}

// ─── pricing calc (mirrors landing page logic) ────────────────────────────────

function calcPrice(calls: number, duration: number, costPerMin = 0.082, costPerCall = 0.10, infra = 30, margin = 0.40) {
    const variable = calls * (costPerCall + duration * costPerMin);
    const total = variable + infra;
    const raw = total / (1 - Math.min(margin, 0.95));
    let price = Math.ceil(raw / 10) * 10 - 1;
    const floor = Math.ceil((infra * 1.5) / 10) * 10 - 1;
    if (price < floor) price = floor;
    const profit = price - total;
    return { price, total, profit, margin: (profit / price) * 100 };
}

// ─── AddCredits modal ────────────────────────────────────────────────────────

function AddCreditsModal({
    tenant,
    onClose,
    onSuccess,
}: {
    tenant: TenantBillingSummary;
    onClose: () => void;
    onSuccess: (newBalance: number) => void;
}) {
    const [amount, setAmount] = useState("");
    const [note, setNote] = useState("");
    const [loading, setLoading] = useState(false);
    const presets = [10, 25, 50, 100, 200, 500];

    const submit = async () => {
        const n = parseFloat(amount);
        if (!n || n <= 0) { toast.error("Enter a valid amount"); return; }
        setLoading(true);
        try {
            const res = await adminApi.addCredits(tenant.tenant_id, n, note || undefined);
            toast.success(`Added $${fmt(n)} to ${tenant.name}`);
            onSuccess(res.new_balance);
        } catch {
            toast.error("Failed to add credits");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
                <h3 className="text-lg font-bold text-white mb-1">Add Credits</h3>
                <p className="text-slate-400 text-sm mb-5">{tenant.name} · current balance: <span className="text-white font-semibold">${fmt(tenant.credit_balance)}</span></p>

                <div className="flex flex-wrap gap-2 mb-4">
                    {presets.map(p => (
                        <button key={p} onClick={() => setAmount(String(p))}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${amount === String(p) ? "bg-emerald-500 border-emerald-500 text-white" : "bg-slate-700 border-slate-600 text-slate-300 hover:border-emerald-500/50"}`}>
                            ${p}
                        </button>
                    ))}
                </div>

                <input
                    type="number"
                    placeholder="Custom amount ($)"
                    value={amount}
                    onChange={e => setAmount(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-600 rounded-lg px-4 py-2.5 text-white text-sm mb-3 focus:border-emerald-500 outline-none"
                />
                <input
                    type="text"
                    placeholder="Note (optional)"
                    value={note}
                    onChange={e => setNote(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-600 rounded-lg px-4 py-2.5 text-white text-sm mb-5 focus:border-emerald-500 outline-none"
                />

                <div className="flex gap-3">
                    <button onClick={onClose} className="flex-1 py-2.5 rounded-lg border border-slate-600 text-slate-300 hover:bg-slate-700 transition-colors text-sm font-medium">
                        Cancel
                    </button>
                    <button onClick={submit} disabled={loading}
                        className="flex-1 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed">
                        {loading ? "Adding…" : "Add Credits"}
                    </button>
                </div>
            </div>
        </div>
    );
}

// ─── Pricing Calculator ───────────────────────────────────────────────────────

function PricingCalc() {
    const [calls, setCalls] = useState(500);
    const [duration, setDuration] = useState(3);
    const [margin, setMargin] = useState(40);
    const f = calcPrice(calls, duration, 0.082, 0.10, 30, margin / 100);

    return (
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6">
            <h3 className="text-base font-bold text-white mb-1">Dynamic Pricing Calculator</h3>
            <p className="text-slate-400 text-xs mb-5">Same logic as the landing page — adjust to preview what tenants would pay.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-xs text-slate-400 uppercase tracking-wider">Monthly Calls</label>
                        <span className="text-sm font-bold text-emerald-400">{calls.toLocaleString()}</span>
                    </div>
                    <input type="range" min="100" max="5000" step="100" value={calls}
                        onChange={e => setCalls(Number(e.target.value))}
                        className="w-full accent-emerald-500 h-1.5 bg-slate-700 rounded-full appearance-none cursor-pointer" />
                </div>
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-xs text-slate-400 uppercase tracking-wider">Avg Duration</label>
                        <span className="text-sm font-bold text-emerald-400">{duration} min</span>
                    </div>
                    <input type="range" min="1" max="15" step="0.5" value={duration}
                        onChange={e => setDuration(Number(e.target.value))}
                        className="w-full accent-emerald-500 h-1.5 bg-slate-700 rounded-full appearance-none cursor-pointer" />
                </div>
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-xs text-slate-400 uppercase tracking-wider">Target Margin</label>
                        <span className="text-sm font-bold text-emerald-400">{margin}%</span>
                    </div>
                    <input type="range" min="10" max="80" step="5" value={margin}
                        onChange={e => setMargin(Number(e.target.value))}
                        className="w-full accent-emerald-500 h-1.5 bg-slate-700 rounded-full appearance-none cursor-pointer" />
                </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
                <div className="bg-slate-900/60 rounded-xl p-4 text-center">
                    <p className="text-xs text-slate-500 mb-1">Suggested Price</p>
                    <p className="text-2xl font-bold text-white">${f.price}<span className="text-sm text-slate-500">/mo</span></p>
                </div>
                <div className="bg-slate-900/60 rounded-xl p-4 text-center">
                    <p className="text-xs text-slate-500 mb-1">Total Cost</p>
                    <p className="text-2xl font-bold text-red-400">${fmt(f.total)}</p>
                </div>
                <div className="bg-slate-900/60 rounded-xl p-4 text-center">
                    <p className="text-xs text-slate-500 mb-1">Net Profit</p>
                    <p className="text-2xl font-bold text-emerald-400">${fmt(f.profit)}</p>
                    <p className="text-xs text-slate-500">{fmt(f.margin, 1)}% margin</p>
                </div>
            </div>
        </div>
    );
}

// ─── Tenant Row ───────────────────────────────────────────────────────────────

function TenantRow({ t, onAddCredits }: { t: TenantBillingSummary; onAddCredits: () => void }) {
    const [expanded, setExpanded] = useState(false);
    const hasAssistants = t.assistants && t.assistants.length > 0;

    return (
        <>
            <tr className="border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors">
                <td className="py-3 px-4">
                    <div className="flex flex-col">
                        <span className="text-sm font-semibold text-white">{t.name || "—"}</span>
                        <span className="text-xs text-slate-500">{t.email}</span>
                    </div>
                </td>
                <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold capitalize ${planColor(t.plan)}`}>{t.plan || "free"}</span>
                </td>
                <td className="py-3 px-4">{statusDot(t.subscription_status)}</td>
                <td className="py-3 px-4">
                    <div>
                        <span className="text-sm font-bold text-white">${fmt(t.credit_balance)}</span>
                        {t.monthly_subscription_usd > 0 && (
                            <span className="text-xs text-slate-500 ml-1">/ ${fmt(t.monthly_subscription_usd)}</span>
                        )}
                        {creditBar(t.credit_balance, t.monthly_subscription_usd)}
                    </div>
                </td>
                <td className="py-3 px-4 text-sm text-amber-400">${fmt(t.total_vapi_cost_usd, 4)}</td>
                <td className="py-3 px-4">
                    <span className={`text-sm font-semibold ${t.profit_usd >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                        {t.profit_usd >= 0 ? "+" : ""}${fmt(t.profit_usd, 2)}
                    </span>
                </td>
                <td className="py-3 px-4 text-sm text-slate-300">{t.total_calls}</td>
                <td className="py-3 px-4 text-sm text-slate-300">{fmt(t.total_minutes, 1)} min</td>
                <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                        <button onClick={onAddCredits}
                            className="flex items-center gap-1 px-2.5 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400 rounded-lg text-xs font-medium transition-colors border border-emerald-600/30">
                            <PlusCircle className="w-3 h-3" /> Credits
                        </button>
                        {hasAssistants && (
                            <button onClick={() => setExpanded(v => !v)}
                                className="p-1.5 text-slate-400 hover:text-white transition-colors rounded">
                                {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            </button>
                        )}
                    </div>
                </td>
            </tr>
            {expanded && t.assistants.map(a => (
                <tr key={a.assistant_id} className="bg-slate-900/40 border-b border-slate-700/20">
                    <td colSpan={2} className="py-2 pl-8 text-xs text-slate-500 font-mono">{a.assistant_id}</td>
                    <td colSpan={2} className="py-2 text-xs text-slate-400">{a.total_calls} calls</td>
                    <td className="py-2 text-xs text-amber-400">${fmt(a.total_cost_usd, 4)}</td>
                    <td colSpan={4} className="py-2 text-xs text-slate-400">{fmt(a.total_minutes, 1)} min</td>
                </tr>
            ))}
        </>
    );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function AdminBillingPage() {
    const [data, setData] = useState<BillingOverview | null>(null);
    const [loading, setLoading] = useState(true);
    const [modalTenant, setModalTenant] = useState<TenantBillingSummary | null>(null);

    const load = async () => {
        setLoading(true);
        try {
            const res = await adminApi.getBillingOverview();
            setData(res);
        } catch {
            toast.error("Failed to load billing overview");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(); }, []);

    const handleCreditsAdded = (tenantId: string, newBalance: number) => {
        setData(prev => {
            if (!prev) return prev;
            return {
                ...prev,
                tenants: prev.tenants.map(t =>
                    t.tenant_id === tenantId ? { ...t, credit_balance: newBalance } : t
                ),
            };
        });
        setModalTenant(null);
    };

    const ps = data?.platform_summary;
    const marginPct = ps && ps.total_subscription_revenue_usd > 0
        ? (ps.platform_margin_usd / ps.total_subscription_revenue_usd) * 100 : 0;

    const summaryCards = ps ? [
        {
            label: "Monthly Revenue",
            value: `$${fmt(ps.total_subscription_revenue_usd)}`,
            icon: DollarSign,
            color: "text-emerald-400",
            bg: "bg-emerald-500/10 border-emerald-500/20",
        },
        {
            label: "Vapi Cost",
            value: `$${fmt(ps.total_vapi_cost_usd, 4)}`,
            icon: TrendingDown,
            color: "text-amber-400",
            bg: "bg-amber-500/10 border-amber-500/20",
        },
        {
            label: "Gross Margin",
            value: `$${fmt(ps.platform_margin_usd)} (${fmt(marginPct, 1)}%)`,
            icon: TrendingUp,
            color: marginPct >= 0 ? "text-emerald-400" : "text-red-400",
            bg: marginPct >= 0 ? "bg-emerald-500/10 border-emerald-500/20" : "bg-red-500/10 border-red-500/20",
        },
        {
            label: "Active Tenants",
            value: `${ps.active_tenants} / ${ps.total_tenants}`,
            icon: Building2,
            color: "text-blue-400",
            bg: "bg-blue-500/10 border-blue-500/20",
        },
    ] : [];

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center">
                    <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                    <p className="text-slate-400 text-sm">Loading billing data…</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 text-white">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Billing Overview</h1>
                    <p className="text-slate-400 mt-1 text-sm">Platform revenue, Vapi costs, and per-tenant credit management.</p>
                </div>
                <button onClick={load}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl text-sm font-medium transition-colors">
                    <RefreshCw className="w-4 h-4" /> Refresh
                </button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {summaryCards.map((c, i) => (
                    <div key={i} className={`bg-slate-800 border rounded-2xl p-5 ${c.bg}`}>
                        <div className="flex items-center justify-between mb-3">
                            <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">{c.label}</p>
                            <c.icon className={`w-4 h-4 ${c.color}`} />
                        </div>
                        <p className={`text-2xl font-bold ${c.color}`}>{c.value}</p>
                    </div>
                ))}
            </div>

            {/* Pricing Calculator */}
            <PricingCalc />

            {/* Tenants Table */}
            <div className="bg-slate-800 border border-slate-700 rounded-2xl overflow-hidden">
                <div className="p-5 border-b border-slate-700 flex items-center justify-between">
                    <div>
                        <h2 className="text-base font-bold text-white">Tenant Billing</h2>
                        <p className="text-slate-400 text-xs mt-0.5">{data?.tenants.length ?? 0} tenants</p>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span className="flex items-center gap-1.5"><Phone className="w-3 h-3" /> Calls</span>
                        <span className="flex items-center gap-1.5"><Clock className="w-3 h-3" /> Minutes</span>
                        <span className="flex items-center gap-1.5"><CreditCard className="w-3 h-3" /> Credits</span>
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-slate-700 text-xs text-slate-500 uppercase tracking-wider">
                                <th className="text-left py-3 px-4">Tenant</th>
                                <th className="text-left py-3 px-4">Plan</th>
                                <th className="text-left py-3 px-4">Status</th>
                                <th className="text-left py-3 px-4">Credits</th>
                                <th className="text-left py-3 px-4">Vapi Cost</th>
                                <th className="text-left py-3 px-4">Profit</th>
                                <th className="text-left py-3 px-4">Calls</th>
                                <th className="text-left py-3 px-4">Minutes</th>
                                <th className="text-left py-3 px-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data?.tenants.length === 0 ? (
                                <tr>
                                    <td colSpan={9} className="text-center text-slate-500 py-10">No tenants found.</td>
                                </tr>
                            ) : (
                                data?.tenants.map(t => (
                                    <TenantRow key={t.tenant_id} t={t} onAddCredits={() => setModalTenant(t)} />
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Add Credits Modal */}
            {modalTenant && (
                <AddCreditsModal
                    tenant={modalTenant}
                    onClose={() => setModalTenant(null)}
                    onSuccess={(newBalance) => handleCreditsAdded(modalTenant.tenant_id, newBalance)}
                />
            )}
        </div>
    );
}
