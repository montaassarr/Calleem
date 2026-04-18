"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronLeft, ChevronRight, Loader2, PhoneCall, RefreshCw } from "lucide-react";
import { callsApi } from "@/lib/api/calls";
import type { CallDetailResponse, CallListItem } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";

const PAGE_SIZE = 10;

const formatDate = (value: string | null) => {
    if (!value) return "—";
    return new Date(value).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
};

const formatDuration = (seconds: number) => `${seconds ?? 0}`;

export function CallHistoryPage() {
    const router = useRouter();
    const [page, setPage] = useState(1);
    const [items, setItems] = useState<CallListItem[]>([]);
    const [hasMore, setHasMore] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedCallId, setSelectedCallId] = useState<string | null>(null);
    const [selectedCall, setSelectedCall] = useState<CallDetailResponse | null>(null);
    const [detailLoading, setDetailLoading] = useState(false);
    const [detailError, setDetailError] = useState<string | null>(null);

    useEffect(() => {
        let mounted = true;

        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await callsApi.list(page, PAGE_SIZE);
                if (!mounted) return;
                const sanitizedItems = (response.items || []).map((item: any) => ({
                    callId: item?.callId || item?.id || item?.call?.id || null,
                    createdAt: item?.createdAt || item?.created_at || item?.startedAt || null,
                    clientPhoneNumber: item?.clientPhoneNumber || item?.client_phone_number || item?.customer_phone || null,
                    durationSeconds: Number(item?.durationSeconds ?? item?.duration ?? 0),
                    status: item?.status || null,
                    endedReason: item?.endedReason || item?.ended_reason || null,
                })).filter((item: any) => Boolean(item.callId));

                setItems(sanitizedItems);
                setHasMore(Boolean(response.hasMore));
            } catch (err: any) {
                if (!mounted) return;
                setError(err?.message || "Unable to load call history right now.");
                setItems([]);
                setHasMore(false);
            } finally {
                if (mounted) setLoading(false);
            }
        };

        load();
        return () => {
            mounted = false;
        };
    }, [page]);

    const emptyState = useMemo(() => {
        if (error) {
            return error;
        }
        return "No calls yet.";
    }, [error]);

    const openCallDetails = async (callId: string | null | undefined) => {
        const normalizedId = String(callId ?? "").trim();
        if (!normalizedId || normalizedId === "undefined" || normalizedId === "null") {
            return;
        }

        setSelectedCallId(normalizedId);
        setSelectedCall(null);
        setDetailError(null);
        setDetailLoading(true);

        try {
            const detail = await callsApi.get(normalizedId);
            setSelectedCall(detail);
        } catch (err: any) {
            setDetailError(err?.message || "Unable to load call details.");
        } finally {
            setDetailLoading(false);
        }
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Recent Calls</h1>
                    <p className="text-muted-foreground">Review the 10 most recent calls and open any call for the full transcript.</p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => setPage(1)} disabled={loading}>
                        <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                        Refresh
                    </Button>
                </div>
            </div>

            <div className="bg-white border border-slate-200 shadow-sm rounded-2xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-slate-50 border-b border-slate-200 text-left">
                            <tr>
                                <th className="px-4 py-3 font-medium">Created At</th>
                                <th className="px-4 py-3 font-medium">Client Phone</th>
                                <th className="px-4 py-3 font-medium">Duration (sec)</th>
                                <th className="px-4 py-3 font-medium">Status</th>
                                <th className="px-4 py-3 font-medium">Ended Reason</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td className="px-4 py-10 text-center text-muted-foreground" colSpan={5}>
                                        <div className="flex items-center justify-center gap-2">
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                            Loading calls...
                                        </div>
                                    </td>
                                </tr>
                            ) : items.length === 0 ? (
                                <tr>
                                    <td className="px-4 py-12 text-center text-muted-foreground" colSpan={5}>
                                        <PhoneCall className="h-10 w-10 mx-auto mb-3 opacity-50" />
                                        <p className="font-medium">{emptyState}</p>
                                        <p className="text-sm mt-1">
                                            {error ? "Please try again in a moment." : "Your call history will appear here once calls come in."}
                                        </p>
                                    </td>
                                </tr>
                            ) : (
                                items.map((call) => (
                                    <tr
                                        key={call.callId}
                                        className="border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors"
                                        onClick={() => {
                                            if (!call.callId) return;
                                            openCallDetails(call.callId);
                                        }}
                                    >
                                        <td className="px-4 py-4 whitespace-nowrap">{formatDate(call.createdAt)}</td>
                                        <td className="px-4 py-4 whitespace-nowrap font-medium">{call.clientPhoneNumber || "—"}</td>
                                        <td className="px-4 py-4 whitespace-nowrap">{formatDuration(call.durationSeconds)}</td>
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            <Badge variant={call.status === "ended" ? "default" : "secondary"}>
                                                {call.status || "unknown"}
                                            </Badge>
                                        </td>
                                        <td className="px-4 py-4 max-w-[260px] truncate text-muted-foreground">
                                            {call.endedReason || "—"}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                <div className="flex items-center justify-between gap-3 px-4 py-3 border-t border-slate-200 bg-slate-50">
                    <p className="text-sm text-muted-foreground">Page {page}</p>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage((current) => Math.max(1, current - 1))}
                            disabled={page === 1 || loading}
                        >
                            <ChevronLeft className="h-4 w-4 mr-1" />
                            Previous
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage((current) => current + 1)}
                            disabled={!hasMore || loading}
                        >
                            Next
                            <ChevronRight className="h-4 w-4 ml-1" />
                        </Button>
                    </div>
                </div>
            </div>

            <Dialog open={Boolean(selectedCallId)} onOpenChange={(open) => {
                if (!open) {
                    setSelectedCallId(null);
                    setSelectedCall(null);
                    setDetailError(null);
                    setDetailLoading(false);
                }
            }}>
                <DialogContent className="w-[96vw] max-w-[96vw] sm:max-w-[92vw] lg:max-w-[84vw] xl:max-w-[74vw] 2xl:max-w-[68vw] max-h-[92vh] overflow-hidden p-5 sm:p-6">
                    <DialogHeader>
                        <DialogTitle>Call Details</DialogTitle>
                        <DialogDescription>
                            Detailed call metadata and transcript.
                        </DialogDescription>
                    </DialogHeader>

                    <div className="overflow-y-auto pr-1">
                        {detailLoading ? (
                            <div className="flex items-center justify-center py-12 text-muted-foreground">
                                <Loader2 className="h-5 w-5 animate-spin mr-2" />
                                Loading call details...
                            </div>
                        ) : detailError ? (
                            <div className="py-10 text-center">
                                <PhoneCall className="h-10 w-10 mx-auto mb-3 opacity-50 text-muted-foreground" />
                                <p className="font-medium">Could not load details</p>
                                <p className="text-sm text-muted-foreground mt-1">{detailError}</p>
                            </div>
                        ) : !selectedCall ? (
                            <div className="py-10 text-center text-muted-foreground">
                                No call selected.
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    <div className="border rounded-lg p-3">
                                        <p className="text-xs text-muted-foreground mb-1">Client Number</p>
                                        <p className="font-semibold">{selectedCall.clientPhoneNumber || "—"}</p>
                                    </div>
                                    <div className="border rounded-lg p-3">
                                        <p className="text-xs text-muted-foreground mb-1">Created At</p>
                                        <p className="font-semibold">{formatDate(selectedCall.createdAt)}</p>
                                    </div>
                                    <div className="border rounded-lg p-3">
                                        <p className="text-xs text-muted-foreground mb-1">Duration (sec)</p>
                                        <p className="font-semibold">{formatDuration(selectedCall.durationSeconds)}</p>
                                    </div>
                                    <div className="border rounded-lg p-3">
                                        <p className="text-xs text-muted-foreground mb-1">Status</p>
                                        <p className="font-semibold capitalize">{selectedCall.status || "unknown"}</p>
                                    </div>
                                </div>

                                <div className="border rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="font-semibold">Transcript</h3>
                                        <Badge variant={selectedCall.status === "ended" ? "default" : "secondary"}>
                                            {selectedCall.status || "unknown"}
                                        </Badge>
                                    </div>

                                    {!selectedCall.messages || selectedCall.messages.length === 0 ? (
                                        <div className="py-8 text-center text-muted-foreground">
                                            <p className="font-medium">No transcript available</p>
                                            <p className="text-sm mt-1">This call does not have structured transcript messages yet.</p>
                                        </div>
                                    ) : (
                                        <div className="space-y-3 max-h-[46vh] overflow-y-auto pr-1">
                                            {selectedCall.messages.map((message, index) => {
                                                const isClient = message.role === "client";
                                                return (
                                                    <div key={`${message.role}-${index}`} className={`flex ${isClient ? "justify-start" : "justify-end"}`}>
                                                        <div className={`max-w-[82%] rounded-2xl px-4 py-2.5 ${isClient ? "bg-slate-100 text-slate-900 rounded-tl-none" : "bg-primary text-primary-foreground rounded-tr-none"}`}>
                                                            <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                                                            {message.timestamp && (
                                                                <p className="text-[10px] opacity-70 mt-1">
                                                                    {new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                                                                </p>
                                                            )}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>

                                <div className="flex justify-end">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                            if (!selectedCall.callId) return;
                                            router.push(`/dashboard/calls/${selectedCall.callId}`);
                                        }}
                                    >
                                        Open full page
                                    </Button>
                                </div>
                            </div>
                        )}
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
