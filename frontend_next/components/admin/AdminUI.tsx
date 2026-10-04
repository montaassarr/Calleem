import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

/** Shared building blocks for the super-admin console (dark .admin-theme). */

const TONES = {
    lime: "bg-[#8cff2e]/10 text-[#b4ff7a] ring-[#8cff2e]/20",
    green: "bg-emerald-400/10 text-emerald-300 ring-emerald-400/20",
    amber: "bg-amber-400/10 text-amber-300 ring-amber-400/25",
    blue: "bg-sky-400/10 text-sky-300 ring-sky-400/20",
    red: "bg-rose-500/10 text-rose-300 ring-rose-400/25",
    slate: "bg-white/[0.04] text-slate-300 ring-white/10",
} as const;

export type Tone = keyof typeof TONES;

export function PageHeader({
    eyebrow,
    title,
    description,
    actions,
}: {
    eyebrow?: string;
    title: React.ReactNode;
    description?: React.ReactNode;
    actions?: React.ReactNode;
}) {
    return (
        <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
                {eyebrow && (
                    <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8cff2e]">{eyebrow}</p>
                )}
                <h1 className="font-host text-[28px] font-bold leading-tight tracking-tight text-foreground">{title}</h1>
                {description && <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground">{description}</p>}
            </div>
            {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
        </div>
    );
}

export function StatCard({
    label,
    value,
    hint,
    icon: Icon,
    tone = "slate",
}: {
    label: string;
    value: React.ReactNode;
    hint?: React.ReactNode;
    icon: LucideIcon;
    tone?: Tone;
}) {
    return (
        <div className="rounded-2xl border border-border bg-card p-5">
            <div className="flex items-start justify-between gap-3">
                <p className="text-[13px] font-medium text-muted-foreground">{label}</p>
                <span className={cn("grid size-9 shrink-0 place-items-center rounded-xl ring-1 ring-inset", TONES[tone])}>
                    <Icon className="size-[18px]" />
                </span>
            </div>
            <p className="mt-3 font-host text-[30px] font-bold leading-none tracking-tight tabular-nums text-foreground">{value}</p>
            {hint && <p className="mt-2 text-xs text-muted-foreground">{hint}</p>}
        </div>
    );
}

export function Panel({
    title,
    description,
    actions,
    children,
    className,
    bodyClassName,
}: {
    title?: React.ReactNode;
    description?: React.ReactNode;
    actions?: React.ReactNode;
    children: React.ReactNode;
    className?: string;
    bodyClassName?: string;
}) {
    return (
        <section className={cn("rounded-2xl border border-border bg-card", className)}>
            {(title || actions) && (
                <header className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-5 py-4">
                    <div>
                        {title && <h2 className="text-[15px] font-semibold text-foreground">{title}</h2>}
                        {description && <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>}
                    </div>
                    {actions}
                </header>
            )}
            <div className={cn("p-5", bodyClassName)}>{children}</div>
        </section>
    );
}

export function Pill({ tone = "slate", dot, children }: { tone?: Tone; dot?: boolean; children: React.ReactNode }) {
    return (
        <span className={cn("inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset", TONES[tone])}>
            {dot && <span className="size-1.5 rounded-full bg-current" />}
            {children}
        </span>
    );
}

export function Avatar({ name, className }: { name?: string | null; className?: string }) {
    const initials = (name || "?")
        .split(/[\s@._-]+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase())
        .join("");
    return (
        <span
            className={cn(
                "grid size-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-[#2f9e57] to-[#0e2e22] text-xs font-semibold text-white ring-1 ring-white/10",
                className,
            )}
        >
            {initials || "?"}
        </span>
    );
}

export function EmptyState({ icon: Icon, title, hint }: { icon: LucideIcon; title: string; hint?: string }) {
    return (
        <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
            <span className="grid size-11 place-items-center rounded-2xl bg-white/[0.04] text-muted-foreground ring-1 ring-inset ring-white/10">
                <Icon className="size-5" />
            </span>
            <p className="text-sm font-medium text-foreground">{title}</p>
            {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
        </div>
    );
}

export function LoadingState({ label = "Loading…" }: { label?: string }) {
    return (
        <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3">
            <div className="size-8 animate-spin rounded-full border-2 border-[#8cff2e] border-t-transparent" />
            <p className="text-sm text-muted-foreground">{label}</p>
        </div>
    );
}

const PLAN_LABELS: Record<string, string> = { trial: "Free trial", monthly: "Monthly", custom: "Custom" };

export function PlanPill({ plan }: { plan: string }) {
    return <Pill tone={plan === "trial" ? "slate" : "lime"}>{PLAN_LABELS[plan] ?? plan}</Pill>;
}

/** Whether a business's AI receptionist is answering, paused for lack of minutes, or never paused. */
export function CallsStatusPill({ paused, exempt, minutes }: { paused: boolean; exempt: boolean; minutes: number }) {
    if (paused) return <Pill dot tone="red">Paused</Pill>;
    if (exempt) return <Pill dot tone="blue">Exempt</Pill>;
    if (minutes <= 30) return <Pill dot tone="amber">Low</Pill>;
    return <Pill dot tone="green">Answering</Pill>;
}
