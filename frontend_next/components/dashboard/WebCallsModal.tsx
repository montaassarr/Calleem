"use client";

import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Loader2, Phone } from "lucide-react";

interface WebCall {
    id: string;
    phoneNumber: string;
    duration?: number;
    createdAt?: string;
    endedAt?: string;
    transcript?: string;
    status?: string;
    cost?: number;
}

interface WebCallsModalProps {
    isOpen: boolean;
    onClose: () => void;
    calls: WebCall[];
    isLoading?: boolean;
}

const formatDuration = (seconds?: number) => {
    if (!seconds) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
};

const formatDate = (dateStr?: string) => {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
};

const formatCost = (cost?: number) => {
    if (typeof cost !== "number") return "—";
    return `$${cost.toFixed(2)}`;
};

export function WebCallsModal({ isOpen, onClose, calls, isLoading = false }: WebCallsModalProps) {
    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="max-w-3xl max-h-[85vh] overflow-hidden">
                <DialogHeader>
                    <DialogTitle>All Web Calls</DialogTitle>
                    <DialogDescription>
                        Review recent calls with duration, status, and cost.
                    </DialogDescription>
                </DialogHeader>

                <div className="overflow-y-auto pr-1">
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-6 w-6 animate-spin" />
                        </div>
                    ) : calls.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            <Phone className="h-10 w-10 mx-auto mb-2 opacity-50" />
                            <p>No web calls found</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {calls.map((call) => (
                                <div
                                    key={call.id}
                                    className="rounded-lg border border-slate-200 p-4 bg-white"
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div>
                                            <p className="font-medium">{call.phoneNumber || "Web Call"}</p>
                                            <p className="text-xs text-muted-foreground mt-1">
                                                {formatDate(call.createdAt)}
                                            </p>
                                        </div>
                                        <Badge variant={call.status === "ended" ? "default" : "secondary"}>
                                            {call.status || "unknown"}
                                        </Badge>
                                    </div>

                                    <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                                        <p>
                                            <span className="text-muted-foreground">Duration: </span>
                                            <span className="font-medium">{formatDuration(call.duration)}</span>
                                        </p>
                                        <p>
                                            <span className="text-muted-foreground">Cost: </span>
                                            <span className="font-medium">{formatCost(call.cost)}</span>
                                        </p>
                                        <p className="truncate">
                                            <span className="text-muted-foreground">Ended: </span>
                                            <span className="font-medium">{formatDate(call.endedAt)}</span>
                                        </p>
                                    </div>

                                    {call.transcript && (
                                        <p className="mt-3 text-sm text-muted-foreground line-clamp-3">
                                            {call.transcript}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
