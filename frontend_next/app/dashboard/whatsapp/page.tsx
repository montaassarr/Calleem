"use client";

import { useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
    CheckCircle2,
    ChevronDown,
    Copy,
    ExternalLink,
    Loader2,
    MessageCircle,
    Smartphone,
    Unplug,
    XCircle,
} from "lucide-react";
import { whatsappApi, WhatsAppConnectionInput, WhatsAppConversation } from "@/lib/api/whatsapp";
import { LEGAL } from "@/lib/legal";

const card = "bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6";
const inputClass =
    "w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20";

function errorMessage(error: unknown) {
    const detail = (error as any)?.response?.data?.detail;
    return typeof detail === "string" ? detail : "Something went wrong. Please try again.";
}

function CopyField({ label, value }: { label: string; value: string }) {
    return (
        <div>
            <label className="text-xs font-semibold text-gray-600 mb-1 block">{label}</label>
            <div className="flex gap-2">
                <input value={value} readOnly className={`${inputClass} font-mono text-xs`} />
                <button
                    type="button"
                    onClick={() => {
                        navigator.clipboard.writeText(value);
                        toast.success("Copied");
                    }}
                    className="px-3 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50"
                    aria-label={`Copy ${label}`}
                >
                    <Copy className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}

function Step({ n, title, children }: { n: number; title: string; children: React.ReactNode }) {
    return (
        <li className="flex gap-3">
            <span className="w-7 h-7 rounded-full bg-gradient-to-br from-[#187848] to-[#0a4c2f] text-white text-xs font-bold flex items-center justify-center shrink-0">
                {n}
            </span>
            <div className="text-sm text-gray-600">
                <p className="font-semibold text-gray-900 mb-0.5">{title}</p>
                {children}
            </div>
        </li>
    );
}

function Conversation({ conversation }: { conversation: WhatsAppConversation }) {
    const [open, setOpen] = useState(false);
    const last = conversation.transcript[conversation.transcript.length - 1];
    return (
        <div className="border border-gray-100 rounded-xl">
            <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between gap-3 p-3 text-left">
                <div className="min-w-0">
                    <p className="text-sm font-semibold text-gray-900 truncate">
                        {conversation.customer_name || conversation.customer_phone}
                        {conversation.customer_name && <span className="font-normal text-gray-400"> · {conversation.customer_phone}</span>}
                    </p>
                    <p className="text-xs text-gray-500 truncate">{last?.text}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[11px] text-gray-400">{new Date(conversation.updated_at).toLocaleString([], { dateStyle: "short", timeStyle: "short" })}</span>
                    <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${open ? "rotate-180" : ""}`} />
                </div>
            </button>
            {open && (
                <div className="p-3 pt-0 space-y-1.5 bg-[#efeae2]/40 rounded-b-xl">
                    {conversation.transcript.map((m, i) => (
                        <div key={i} className={`flex ${m.role === "customer" ? "justify-start" : "justify-end"}`}>
                            <p className={`max-w-[80%] text-sm px-3 py-1.5 rounded-lg whitespace-pre-wrap ${m.role === "customer" ? "bg-white" : "bg-[#d9fdd3]"}`}>
                                {m.text}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default function WhatsAppPage() {
    const queryClient = useQueryClient();
    const { data: status, isLoading } = useQuery({ queryKey: ["whatsapp-status"], queryFn: whatsappApi.getStatus });
    const { data: conversations = [] } = useQuery({
        queryKey: ["whatsapp-conversations"],
        queryFn: () => whatsappApi.listConversations(20),
        enabled: !!status?.configured,
        refetchInterval: 30_000,
    });

    const [form, setForm] = useState<WhatsAppConnectionInput>({ phone_number_id: "", waba_id: "", access_token: "", app_secret: "" });
    const [editing, setEditing] = useState(false);
    const [guideOpen, setGuideOpen] = useState(false);

    const connect = useMutation({
        mutationFn: () => whatsappApi.connect(form),
        onSuccess: (data) => {
            queryClient.setQueryData(["whatsapp-status"], data);
            setEditing(false);
            setForm({ phone_number_id: "", waba_id: "", access_token: "", app_secret: "" });
            toast.success("WhatsApp connected", { description: `${data.phone_number} now gets answers from your AI receptionist.` });
        },
        onError: (error) => toast.error(errorMessage(error)),
    });

    const disconnect = useMutation({
        mutationFn: whatsappApi.disconnect,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["whatsapp-status"] });
            toast.success("WhatsApp disconnected", { description: "Your AI receptionist no longer answers this number." });
        },
        onError: (error) => toast.error(errorMessage(error)),
    });

    const startEditing = () => {
        setForm({ phone_number_id: status?.phone_number_id || "", waba_id: status?.waba_id || "", access_token: "", app_secret: "" });
        setEditing(true);
    };

    const showForm = !status?.configured || editing;
    const tokenOptional = status?.platform_ready || (editing && status?.uses_own_token);

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">WhatsApp</h1>
                <p className="text-[14px] text-gray-500 font-medium">
                    Your AI receptionist answers customers on WhatsApp, 24/7: questions, prices and bookings.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Status */}
                <div className={card}>
                    <div className="flex items-center gap-3 mb-5">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#187848] to-[#0a4c2f] flex items-center justify-center">
                            <Smartphone className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h3 className="font-bold text-gray-900">Your WhatsApp number</h3>
                            {isLoading ? (
                                <span className="text-sm text-gray-400">Checking...</span>
                            ) : status?.configured ? (
                                <span className="text-sm font-bold text-green-700 flex items-center gap-1">
                                    <CheckCircle2 className="w-4 h-4" />Connected
                                </span>
                            ) : (
                                <span className="text-sm font-bold text-gray-500 flex items-center gap-1">
                                    <XCircle className="w-4 h-4" />Not connected
                                </span>
                            )}
                        </div>
                    </div>

                    {status?.configured ? (
                        <div className="space-y-3">
                            <div className="p-3.5 bg-gray-50 rounded-xl">
                                <p className="text-xl font-bold text-gray-900">{status.phone_number}</p>
                                <p className="text-sm text-gray-500">{status.verified_name}</p>
                            </div>
                            <p className="text-xs text-gray-500">
                                {status.last_message_at
                                    ? `Last message answered ${new Date(status.last_message_at).toLocaleString()}`
                                    : "No messages yet. Send a WhatsApp message to this number to try it."}
                            </p>
                            <div className="flex flex-wrap gap-2 pt-1">
                                <Link
                                    href="/dashboard/whatsapp/chat"
                                    className="px-4 py-2 bg-[#0a4c2f] text-white rounded-xl text-sm font-semibold hover:bg-[#073922] flex items-center gap-2"
                                >
                                    <MessageCircle className="w-4 h-4" />Open Chat Test
                                </Link>
                                {!editing && (
                                    <button onClick={startEditing} className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50">
                                        Change settings
                                    </button>
                                )}
                                <button
                                    onClick={() => {
                                        if (confirm("Stop answering WhatsApp messages with the AI receptionist?")) disconnect.mutate();
                                    }}
                                    disabled={disconnect.isPending}
                                    className="px-4 py-2 bg-white border border-red-200 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 flex items-center gap-2"
                                >
                                    <Unplug className="w-4 h-4" />Disconnect
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-3 text-sm text-gray-600">
                            <p>Connect a WhatsApp Business number and every message gets an instant answer, using your services, prices, hours and calendar.</p>
                            <p>
                                Want to see how it answers first?{" "}
                                <Link href="/dashboard/whatsapp/chat" className="font-semibold text-[#187848] hover:underline">Try the Chat Test</Link>.
                            </p>
                            <p>
                                Not sure how to get the details below? Read the guide underneath, or{" "}
                                <Link href={LEGAL.contactUrl} className="font-semibold text-[#187848] hover:underline">ask us to set it up with you</Link>.
                            </p>
                        </div>
                    )}
                </div>

                {/* Connect form */}
                <div className={card}>
                    {showForm ? (
                        <form
                            onSubmit={(e) => {
                                e.preventDefault();
                                connect.mutate();
                            }}
                            className="space-y-4"
                        >
                            <h3 className="font-bold text-gray-900">{editing ? "Update the connection" : "Connect your number"}</h3>
                            <div>
                                <label className="text-xs font-semibold text-gray-600 mb-1 block">Phone number ID *</label>
                                <input
                                    required
                                    inputMode="numeric"
                                    pattern="\d{5,25}"
                                    value={form.phone_number_id}
                                    onChange={(e) => setForm({ ...form, phone_number_id: e.target.value.trim() })}
                                    placeholder="e.g. 106540352242922"
                                    className={inputClass}
                                />
                                <p className="text-[11px] text-gray-400 mt-1">Meta app → WhatsApp → API Setup. It is a long number, not your phone number.</p>
                            </div>
                            <div>
                                <label className="text-xs font-semibold text-gray-600 mb-1 block">
                                    Access token {tokenOptional ? "(leave empty to keep the current one)" : "*"}
                                </label>
                                <input
                                    required={!tokenOptional}
                                    type="password"
                                    autoComplete="off"
                                    value={form.access_token}
                                    onChange={(e) => setForm({ ...form, access_token: e.target.value.trim() })}
                                    placeholder="Permanent token of your system user"
                                    className={inputClass}
                                />
                                {status?.platform_ready && !editing && (
                                    <p className="text-[11px] text-gray-400 mt-1">Leave empty if Calleem set up your number for you.</p>
                                )}
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                    <label className="text-xs font-semibold text-gray-600 mb-1 block">WhatsApp Business Account ID</label>
                                    <input
                                        inputMode="numeric"
                                        value={form.waba_id}
                                        onChange={(e) => setForm({ ...form, waba_id: e.target.value.trim() })}
                                        placeholder="Optional"
                                        className={inputClass}
                                    />
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-gray-600 mb-1 block">
                                        App secret {status?.has_app_secret && editing ? "(saved)" : ""}
                                    </label>
                                    <input
                                        type="password"
                                        autoComplete="off"
                                        value={form.app_secret}
                                        onChange={(e) => setForm({ ...form, app_secret: e.target.value.trim() })}
                                        placeholder="Only with your own Meta app"
                                        className={inputClass}
                                    />
                                </div>
                            </div>
                            <div className="flex gap-2">
                                <button
                                    type="submit"
                                    disabled={connect.isPending}
                                    className="px-5 py-2.5 bg-[#0a4c2f] text-white rounded-xl text-sm font-semibold hover:bg-[#073922] disabled:opacity-60 flex items-center gap-2"
                                >
                                    {connect.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                                    {connect.isPending ? "Checking with Meta..." : editing ? "Save" : "Connect"}
                                </button>
                                {editing && (
                                    <button type="button" onClick={() => setEditing(false)} className="px-4 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 hover:bg-gray-50">
                                        Cancel
                                    </button>
                                )}
                            </div>
                        </form>
                    ) : (
                        <div className="space-y-4">
                            <h3 className="font-bold text-gray-900">Connection details</h3>
                            <dl className="text-sm space-y-2">
                                <div className="flex justify-between gap-4"><dt className="text-gray-500">Phone number ID</dt><dd className="font-mono text-gray-900">{status?.phone_number_id}</dd></div>
                                {status?.waba_id && <div className="flex justify-between gap-4"><dt className="text-gray-500">Business Account ID</dt><dd className="font-mono text-gray-900">{status.waba_id}</dd></div>}
                                <div className="flex justify-between gap-4"><dt className="text-gray-500">Meta app</dt><dd className="text-gray-900">{status?.uses_own_token ? "Your own app" : "Managed by Calleem"}</dd></div>
                            </dl>
                        </div>
                    )}

                    {status?.verify_token && (
                        <div className="mt-6 pt-5 border-t border-gray-100 space-y-3">
                            <p className="text-xs text-gray-500">Only if you use your own Meta app: paste these in your app under WhatsApp → Configuration → Webhook, then subscribe to <b>messages</b>.</p>
                            <CopyField label="Callback URL" value={status.webhook_url} />
                            <CopyField label="Verify token" value={status.verify_token} />
                        </div>
                    )}
                </div>

                {/* Guide */}
                <div className={`lg:col-span-2 ${card}`}>
                    <button onClick={() => setGuideOpen(!guideOpen)} className="w-full flex items-center justify-between text-left">
                        <div>
                            <h3 className="font-bold text-gray-900">Guide: what you need to connect WhatsApp</h3>
                            <p className="text-sm text-gray-500">About 30 minutes, once. We can do it with you on a call.</p>
                        </div>
                        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${guideOpen ? "rotate-180" : ""}`} />
                    </button>

                    {guideOpen && (
                        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <div>
                                <h4 className="font-semibold text-gray-900 mb-3">Before you start</h4>
                                <ul className="space-y-2 text-sm text-gray-600 list-disc pl-5">
                                    <li>A phone number for WhatsApp that can receive an SMS or a call. It must <b>not</b> be on the WhatsApp or WhatsApp Business app (delete that account first, or use another number such as your Calleem line).</li>
                                    <li>A Facebook account that is admin of your business on <a className="text-[#187848] underline" href="https://business.facebook.com" target="_blank" rel="noopener noreferrer">Meta Business</a> (create one if needed: business name, your name, business email).</li>
                                    <li>Your business name as customers know it: Meta shows it on WhatsApp and checks it.</li>
                                    <li>A square logo and a short description for your WhatsApp profile.</li>
                                    <li>Your services with prices, opening hours and FAQs filled in on Calleem: the assistant answers from them.</li>
                                </ul>
                                <h4 className="font-semibold text-gray-900 mt-6 mb-2">What you give us (in the form above)</h4>
                                <ul className="space-y-1 text-sm text-gray-600 list-disc pl-5">
                                    <li>Phone number ID</li>
                                    <li>WhatsApp Business Account ID</li>
                                    <li>Permanent access token</li>
                                    <li>App secret</li>
                                </ul>
                                <p className="text-xs text-gray-400 mt-3">They are stored encrypted and only used to read and answer your WhatsApp messages. Replying to customers who message you first is free on WhatsApp.</p>
                            </div>

                            <ol className="space-y-4">
                                <Step n={1} title="Create the app">
                                    On <a className="text-[#187848] underline" href="https://developers.facebook.com/apps" target="_blank" rel="noopener noreferrer">developers.facebook.com</a> → Create app → use case <i>Connect with customers through WhatsApp</i> → pick your business.
                                </Step>
                                <Step n={2} title="Add your number">
                                    In the app: WhatsApp → API Setup → Add phone number. Enter your business name and category, then the code Meta sends to the number. Copy the <b>Phone number ID</b> and <b>WhatsApp Business Account ID</b> shown there.
                                </Step>
                                <Step n={3} title="Create a permanent token">
                                    Meta Business settings → Users → System users → Add (Admin). Assign assets: your app and your WhatsApp account, full control. Then Generate token → your app → expiry <i>Never</i> → permissions <code className="text-xs">whatsapp_business_messaging</code> and <code className="text-xs">whatsapp_business_management</code>. Copy it.
                                </Step>
                                <Step n={4} title="Copy the app secret">
                                    App settings → Basic → App secret → Show.
                                </Step>
                                <Step n={5} title="Point the webhook to Calleem">
                                    WhatsApp → Configuration → Webhook → Edit: paste the Callback URL and Verify token shown above, Verify and save. Under Webhook fields, subscribe to <b>messages</b>.
                                </Step>
                                <Step n={6} title="Publish the app">
                                    App settings → Basic: Privacy policy URL <code className="text-xs">{LEGAL.website}/privacy</code>, then switch the app to <b>Live</b>. If WhatsApp Manager asks for a payment method, add one.
                                </Step>
                                <Step n={7} title="Connect and test">
                                    Paste the four values in the form above and press Connect. Then send a WhatsApp message to your number from another phone.
                                </Step>
                            </ol>
                        </div>
                    )}
                    {guideOpen && (
                        <a
                            href="https://developers.facebook.com/docs/whatsapp/cloud-api/get-started"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-6 inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700"
                        >
                            <ExternalLink className="w-4 h-4" />Meta&apos;s own getting-started guide
                        </a>
                    )}
                </div>

                {/* Conversations */}
                {status?.configured && (
                    <div className={`lg:col-span-2 ${card}`}>
                        <h3 className="font-bold text-gray-900 mb-4">Recent WhatsApp conversations</h3>
                        {conversations.length === 0 ? (
                            <p className="text-sm text-gray-500">No conversations yet.</p>
                        ) : (
                            <div className="space-y-2">
                                {conversations.map((c) => <Conversation key={c.id} conversation={c} />)}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
