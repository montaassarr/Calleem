"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { CalendarCheck, Loader2, MessageCircle, Mic, RotateCcw, Send } from "lucide-react";
import { whatsappApi } from "@/lib/api/whatsapp";
import { useConfig } from "@/contexts/ConfigContext";

interface ChatMessage {
    role: "customer" | "assistant";
    text: string;
    at: Date;
    tools?: string[];
    appointmentId?: string | null;
    failed?: boolean;
}

const TOOL_LABELS: Record<string, string> = {
    getCurrentDateTime: "Checked today's date",
    getAvailableServices: "Looked up services",
    getBusinessLocation: "Looked up the address",
    checkAvailability: "Checked availability",
    bookAppointment: "Booked the appointment",
};

const SUGGESTIONS = [
    "Hi, what services do you offer?",
    "Can I book for tomorrow at 2pm?",
    "Where are you located?",
];

function newSessionId() {
    if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
    return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
}

export default function ChatTestPage() {
    const { config } = useConfig();
    const [sessionId, setSessionId] = useState(newSessionId);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState("");
    const [sending, setSending] = useState(false);
    const endRef = useRef<HTMLDivElement>(null);

    const businessName = config?.business_name || "Your business";

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, sending]);

    const send = async (text: string) => {
        const message = text.trim();
        if (!message || sending) return;
        setInput("");
        setMessages((prev) => [...prev, { role: "customer", text: message, at: new Date() }]);
        setSending(true);
        try {
            const reply = await whatsappApi.testChat(message, sessionId);
            setMessages((prev) => [
                ...prev,
                { role: "assistant", text: reply.response, at: new Date(), tools: reply.tools_used, appointmentId: reply.appointment_id },
            ]);
        } catch {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", text: "The assistant couldn't answer. Please try again in a moment.", at: new Date(), failed: true },
            ]);
        } finally {
            setSending(false);
        }
    };

    const restart = async () => {
        const old = sessionId;
        setSessionId(newSessionId());
        setMessages([]);
        whatsappApi.resetTestChat(old).catch(() => undefined);
    };

    return (
        <div className="flex flex-col h-[calc(100vh-200px)] min-h-[520px]">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-4">
                <div>
                    <h1 className="text-[24px] font-bold text-gray-900 flex items-center gap-2">
                        <MessageCircle className="h-6 w-6" />Chat Test
                    </h1>
                    <p className="text-sm text-gray-500">
                        Write as if you were a customer texting your business. The assistant uses your real services, prices, hours and calendar.
                    </p>
                </div>
                <div className="flex gap-2 shrink-0">
                    <button
                        onClick={restart}
                        className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center gap-2"
                    >
                        <RotateCcw className="w-4 h-4" />New conversation
                    </button>
                    <Link
                        href="/dashboard/voice-agent/test"
                        className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center gap-2"
                    >
                        <Mic className="w-4 h-4" />Voice Test
                    </Link>
                </div>
            </div>

            <div className="rounded-[24px] border border-gray-100 shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] flex-1 flex flex-col min-h-0 overflow-hidden">
                {/* Header, like a phone chat */}
                <div className="px-5 py-3 bg-[#0a4c2f] text-white flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-white/15 flex items-center justify-center font-bold">
                        {businessName.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                        <h3 className="font-semibold text-sm truncate">{businessName}</h3>
                        <span className="text-xs text-white/70">{sending ? "typing..." : "AI receptionist · online"}</span>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-2 bg-[#efeae2]">
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-center gap-4 px-6">
                            <p className="text-sm text-gray-600 bg-white/80 rounded-xl px-4 py-2 shadow-sm max-w-md">
                                Bookings made here are real: they appear in your Appointments marked &quot;Booked from the Chat Test&quot;.
                            </p>
                            <div className="flex flex-wrap justify-center gap-2">
                                {SUGGESTIONS.map((s) => (
                                    <button
                                        key={s}
                                        onClick={() => send(s)}
                                        className="text-sm bg-white border border-gray-200 rounded-full px-3 py-1.5 text-gray-700 hover:bg-gray-50"
                                    >
                                        {s}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {messages.map((m, i) => (
                        <div key={i} className={`flex ${m.role === "customer" ? "justify-end" : "justify-start"}`}>
                            <div
                                className={`max-w-[80%] px-3 py-2 rounded-lg shadow-sm text-sm ${m.role === "customer"
                                    ? "bg-[#d9fdd3] text-gray-900 rounded-tr-none"
                                    : m.failed
                                        ? "bg-red-50 text-red-800 rounded-tl-none"
                                        : "bg-white text-gray-900 rounded-tl-none"
                                    }`}
                            >
                                <p className="whitespace-pre-wrap">{m.text}</p>
                                {!!m.tools?.length && (
                                    <div className="flex flex-wrap gap-1 mt-1.5">
                                        {Array.from(new Set(m.tools)).map((t) => (
                                            <span key={t} className="text-[10px] font-semibold bg-[#0a4c2f]/10 text-[#0a4c2f] px-1.5 py-0.5 rounded">
                                                {TOOL_LABELS[t] || t}
                                            </span>
                                        ))}
                                    </div>
                                )}
                                {m.appointmentId && (
                                    <Link
                                        href="/dashboard/appointments"
                                        className="mt-1.5 inline-flex items-center gap-1 text-xs font-semibold text-[#0a4c2f] hover:underline"
                                    >
                                        <CalendarCheck className="w-3.5 h-3.5" />See it in Appointments
                                    </Link>
                                )}
                                <p className="text-[10px] text-gray-500 text-right mt-0.5">
                                    {m.at.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                                </p>
                            </div>
                        </div>
                    ))}

                    {sending && (
                        <div className="flex justify-start">
                            <div className="bg-white px-3 py-2.5 rounded-lg rounded-tl-none shadow-sm flex gap-1">
                                {[0, 150, 300].map((delay) => (
                                    <span key={delay} className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${delay}ms` }} />
                                ))}
                            </div>
                        </div>
                    )}
                    <div ref={endRef} />
                </div>

                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        send(input);
                    }}
                    className="p-3 bg-[#f0f2f5] flex gap-2"
                >
                    <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type a message"
                        maxLength={2000}
                        autoComplete="off"
                        className="flex-1 rounded-full border border-gray-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20"
                    />
                    <button
                        type="submit"
                        disabled={sending || !input.trim()}
                        aria-label="Send"
                        className="w-10 h-10 bg-[#0a4c2f] hover:bg-[#073922] text-white rounded-full flex items-center justify-center transition-colors disabled:opacity-40"
                    >
                        {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                    </button>
                </form>
            </div>
        </div>
    );
}
