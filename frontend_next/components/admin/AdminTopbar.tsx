"use client";

import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ChevronRight } from "lucide-react";

const SECTIONS: Record<string, string> = {
    tenants: "Businesses",
    users: "Accounts",
    contacts: "Leads",
    billing: "Billing",
    "vapi-test": "Voice test",
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const AdminTopbar = () => {
    const pathname = usePathname();
    const section = SECTIONS[pathname.split("/")[2] ?? ""];
    // Real backend health (GET /health), checked every minute.
    const { data: online, isLoading } = useQuery({
        queryKey: ["admin-api-health"],
        queryFn: async () => (await fetch(`${API_BASE}/health`)).ok,
        refetchInterval: 60_000,
        retry: false,
    });
    const today = new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });

    return (
        <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-border bg-background/80 px-8 backdrop-blur-md">
            <nav className="flex items-center gap-1.5 text-[13px]">
                <span className="text-muted-foreground">Admin</span>
                <ChevronRight className="size-3.5 text-[#4c5d54]" />
                <span className="font-medium text-foreground">{section ?? "Overview"}</span>
            </nav>
            <div className="flex items-center gap-3 text-[12.5px] text-muted-foreground">
                <span>{today}</span>
                <span className="h-4 w-px bg-border" />
                <span className="flex items-center gap-1.5">
                    <span
                        className={
                            isLoading
                                ? "size-1.5 rounded-full bg-[#5f7368]"
                                : online
                                  ? "size-1.5 rounded-full bg-[#8cff2e] shadow-[0_0_8px_#8cff2e]"
                                  : "size-1.5 rounded-full bg-rose-500 shadow-[0_0_8px_#f43f5e]"
                        }
                    />
                    {isLoading ? "Checking API…" : online ? "API online" : "API offline"}
                </span>
            </div>
        </header>
    );
};
