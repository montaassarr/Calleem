"use client";

import { Search, Mail, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export const DashboardHeader = () => {
    return (
        <header className="sticky top-0 z-40 glass border-b border-white/60 bg-background/80 backdrop-blur-md">
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
                    <Button variant="ghost" size="icon" className="relative">
                        <Mail className="w-5 h-5" />
                    </Button>
                    <Button variant="ghost" size="icon" className="relative">
                        <Bell className="w-5 h-5" />
                        <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full" />
                    </Button>
                    <div className="flex items-center gap-3 ml-3 pl-3 border-l border-border">
                        <div className="text-right">
                            <p className="text-sm font-medium">Sarah Johnson</p>
                            <p className="text-xs text-muted-foreground">sarah@support.com</p>
                        </div>
                        <Avatar>
                            <AvatarFallback className="bg-gradient-to-br from-primary to-info text-white">
                                SJ
                            </AvatarFallback>
                        </Avatar>
                    </div>
                </div>
            </div>
        </header>
    );
};
