import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
    title: string;
    value: string;
    icon: LucideIcon;
    trend?: {
        value: string;
        isPositive: boolean;
    };
    variant?: "primary" | "success" | "warning" | "info";
    status?: string;
}

export const StatCard = ({ title, value, icon: Icon, trend, variant = "primary", status }: StatCardProps) => {
    const isPrimaryVariant = variant === "primary";

    return (
        <div
            className={cn(
                "relative overflow-hidden rounded-2xl p-6 transition-all hover:shadow-2xl hover:-translate-y-2 shine",
                isPrimaryVariant
                    ? "bg-gradient-to-br from-primary to-accent text-white shadow-xl shadow-primary/20"
                    : "glass-card"
            )}
        >
            <div className="flex items-start justify-between mb-4">
                <div>
                    <p className={cn("text-sm font-medium mb-2", isPrimaryVariant ? "text-white/80" : "text-muted-foreground")}>
                        {title}
                    </p>
                    <h3 className="text-4xl font-bold">{value}</h3>
                </div>
                <div className={cn(
                    "p-3 rounded-xl",
                    isPrimaryVariant ? "bg-white/20" : "bg-secondary"
                )}>
                    <Icon className="w-6 h-6" />
                </div>
            </div>

            {trend && (
                <div className="flex items-center gap-1">
                    {trend.isPositive ? (
                        <TrendingUp className="w-4 h-4" />
                    ) : (
                        <TrendingDown className="w-4 h-4" />
                    )}
                    <span className={cn("text-sm", isPrimaryVariant ? "text-white/90" : "text-foreground")}>
                        {trend.value}
                    </span>
                </div>
            )}

            {status && (
                <p className={cn("text-sm mt-2", isPrimaryVariant ? "text-white/80" : "text-muted-foreground")}>
                    {status}
                </p>
            )}
        </div>
    );
};
