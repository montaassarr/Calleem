"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { PhoneForwarded } from "lucide-react";
import { assistantApi, TransferNumberSettings } from "@/lib/api-endpoints";

/**
 * "Transfer urgent calls to": the owner's phone that emergencies (burst pipe, flooding, no heat)
 * and callers who ask for a person are put straight through to. Saving applies it to the assistant at once.
 */
export function CallTransferCard() {
    const queryClient = useQueryClient();
    const { data, isLoading, isError } = useQuery({
        queryKey: ["transfer-number"],
        queryFn: () => assistantApi.getTransferNumber(),
    });
    const saved = data?.transfer_phone_number ?? "";
    const [value, setValue] = useState(saved);
    useEffect(() => setValue(saved), [saved]);

    const save = useMutation({
        mutationFn: () => assistantApi.setTransferNumber(value.trim()),
        onSuccess: (result: TransferNumberSettings) => {
            queryClient.setQueryData(["transfer-number"], result);
            toast.success(result.transfer_phone_number ? `Urgent calls now go to ${result.transfer_phone_number}` : "Call transfer turned off");
        },
        onError: (error: Error) => toast.error(error.message || "Could not save the number"),
    });

    // A saved number that isn't in use (e.g. Transfer Call switched off in Tools) can be saved again to turn it back on.
    const paused = !!data?.transfer_phone_number && !data.active;
    const canSave = !isLoading && !save.isPending && (value.trim() !== saved || paused);

    return (
        <div className="mt-6 bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
            <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-gradient-to-br from-[#187848] to-[#0a4c2f] text-white">
                    <PhoneForwarded className="h-5 w-5" />
                </div>
                <div>
                    <h3 className="font-bold text-lg text-gray-900">Transfer urgent calls to</h3>
                    <p className="text-sm text-gray-500">
                        Emergencies like a burst pipe, flooding or no heat, and callers who ask for a person, are put straight through to this phone.
                    </p>
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
                    autoComplete="tel"
                    aria-label="Phone number to transfer urgent calls to"
                    disabled={isLoading}
                    className="h-11 flex-1 px-4 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                />
                <button
                    type="submit"
                    disabled={!canSave}
                    className="h-11 rounded-full bg-[#0a4c2f] px-6 text-sm font-semibold text-white transition-colors hover:bg-[#187848] disabled:opacity-50"
                >
                    {save.isPending ? "Saving…" : "Save"}
                </button>
            </form>
            <p className="mt-2 text-xs text-gray-500">
                Your cell in international format (+1 for the US), e.g. +14155550123. Leave it empty and save to stop transferring calls.
                Don't use a number that forwards to your Calleem line, or calls would loop.
            </p>
            {paused && (
                <p className="mt-2 text-xs font-medium text-amber-700">Calls aren&apos;t being transferred right now. Save to turn transfers back on.</p>
            )}
            {isError && <p className="mt-2 text-xs text-red-600">Could not load your transfer number. Please refresh the page.</p>}
        </div>
    );
}
