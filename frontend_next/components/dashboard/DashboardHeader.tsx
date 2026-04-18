"use client";

import { useEffect, useState } from "react";
import { Search, Mail, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuth } from "@/contexts/AuthContext";
import { billingApi, DashboardBillingSummary } from "@/lib/api/billing";

export const DashboardHeader = () => {
    const { user } = useAuth();
    const [billingSummary, setBillingSummary] = useState<DashboardBillingSummary | null>(null);

    const displayName = user?.full_name?.trim() || user?.username?.trim() || "User";
    const displayEmail = user?.email || "";
    const creditBalance = Number(billingSummary?.tenant_credit_balance ?? 0);

    useEffect(() => {
        let mounted = true;

        const loadBillingSummary = async () => {
            try {
                const summary = await billingApi.getDashboardSummary();
                if (mounted) {
                    setBillingSummary(summary);
                }
            } catch {
                if (mounted) {
                    setBillingSummary(null);
                }
            }
        };

        loadBillingSummary();
        return () => {
            mounted = false;
        };
    }, []);

    const initials = displayName
        .split(" ")
        .map((part) => part[0])
        .join("")
        .slice(0, 2)
        .toUpperCase();

    return (
        <header className="sticky top-0 z-40 bg-white border-b border-slate-200">
            <div className="flex items-center justify-between p-6">
                <div className="flex-1 max-w-md">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                            placeholder="Search calls, tickets..."
                            className="pl-10 glass-card"
                        />
                        <kbd className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
                            ⌘F
                        </kbd>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <div className="hidden md:flex items-center rounded-lg border border-slate-200 px-3 py-1.5 text-xs">
                        <span className="text-muted-foreground mr-1">Plan:</span>
                        <span className="font-semibold">{billingSummary?.plan_price || "Free"}</span>
                    </div>
                    <div className="hidden md:flex items-center rounded-lg border border-slate-200 px-3 py-1.5 text-xs">
                        <span className="text-muted-foreground mr-1">Credits:</span>
                        <span className="font-semibold">${creditBalance.toFixed(2)}</span>
                    </div>
                    <Button variant="ghost" size="icon" className="relative">
                        <Mail className="w-5 h-5" />
                    </Button>
                    <Button variant="ghost" size="icon" className="relative">
                        <Bell className="w-5 h-5" />
                        <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full" />
                    </Button>
                    <div className="flex items-center gap-3 ml-3 pl-3 border-l border-border">
                        <div className="text-right">
                            <p className="text-sm font-medium">{displayName}</p>
                            <p className="text-xs text-muted-foreground">{displayEmail}</p>
                        </div>
                        <Avatar>
                            <AvatarFallback className="bg-gradient-to-br from-primary to-info text-white">
                                {initials}
                            </AvatarFallback>
                        </Avatar>
                    </div>
                </div>
            </div>
        </header>
    );
};
