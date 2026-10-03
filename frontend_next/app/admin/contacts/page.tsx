"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
    Mail,
    Phone,
    Building2,
    Calendar,
    Search,
    RefreshCw,
    Eye,
    Trash2,
    MessageSquare,
    Users,
    Clock,
    CheckCircle,
    Archive,
    ChevronDown,
    X,
} from "lucide-react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Avatar, EmptyState, LoadingState, PageHeader, Panel, Pill, StatCard, type Tone } from "@/components/admin/AdminUI";

interface Contact {
    id: string;
    full_name: string;
    email: string;
    business_name: string;
    business_type: string;
    phone_number: string;
    monthly_calls: string;
    message?: string;
    newsletter: boolean;
    status: "new" | "read" | "responded" | "archived";
    admin_notes?: string;
    created_at: string;
    updated_at: string;
}

interface ContactStats {
    total: number;
    new: number;
    read: number;
    responded: number;
    archived: number;
    today: number;
    this_week: number;
    this_month: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Lead management endpoints are super-admin only.
const authHeaders = (): Record<string, string> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    return token ? { Authorization: `Bearer ${token}` } : {};
};

export default function ContactsPage() {
    const [contacts, setContacts] = useState<Contact[]>([]);
    const [stats, setStats] = useState<ContactStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState<string>("all");
    const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
    const [isDetailOpen, setIsDetailOpen] = useState(false);
    const [adminNotes, setAdminNotes] = useState("");

    const fetchContacts = useCallback(async () => {
        try {
            const params = new URLSearchParams();
            if (searchTerm) params.append("search", searchTerm);
            if (statusFilter !== "all") params.append("status", statusFilter);

            const response = await fetch(`${API_BASE}/api/v1/contacts?${params}`, { headers: authHeaders() });
            if (!response.ok) throw new Error("Failed to fetch contacts");
            const data = await response.json();
            setContacts(data);
        } catch (error) {
            console.error("Error fetching contacts:", error);
            toast.error("Failed to load contacts");
        }
    }, [searchTerm, statusFilter]);

    const fetchStats = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/v1/contacts/stats`, { headers: authHeaders() });
            if (!response.ok) throw new Error("Failed to fetch stats");
            const data = await response.json();
            setStats(data);
        } catch (error) {
            console.error("Error fetching stats:", error);
        }
    }, []);

    const loadData = useCallback(async () => {
        setLoading(true);
        await Promise.all([fetchContacts(), fetchStats()]);
        setLoading(false);
    }, [fetchContacts, fetchStats]);

    useEffect(() => {
        loadData();
        // Auto-refresh every 30 seconds
        const interval = setInterval(loadData, 30000);
        return () => clearInterval(interval);
    }, [loadData]);

    const updateContactStatus = async (contactId: string, status: string) => {
        try {
            const response = await fetch(`${API_BASE}/api/v1/contacts/${contactId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json", ...authHeaders() },
                body: JSON.stringify({ status }),
            });
            if (!response.ok) throw new Error("Failed to update contact");
            toast.success("Contact status updated");
            await loadData();
        } catch (error) {
            console.error("Error updating contact:", error);
            toast.error("Failed to update contact");
        }
    };

    const updateAdminNotes = async (contactId: string) => {
        try {
            const response = await fetch(`${API_BASE}/api/v1/contacts/${contactId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json", ...authHeaders() },
                body: JSON.stringify({ admin_notes: adminNotes }),
            });
            if (!response.ok) throw new Error("Failed to update notes");
            toast.success("Notes saved");
            await loadData();
        } catch (error) {
            console.error("Error updating notes:", error);
            toast.error("Failed to save notes");
        }
    };

    const deleteContact = async (contactId: string) => {
        if (!confirm("Are you sure you want to delete this contact?")) return;

        try {
            const response = await fetch(`${API_BASE}/api/v1/contacts/${contactId}`, {
                method: "DELETE",
                headers: authHeaders(),
            });
            if (!response.ok) throw new Error("Failed to delete contact");
            toast.success("Contact deleted");
            setIsDetailOpen(false);
            await loadData();
        } catch (error) {
            console.error("Error deleting contact:", error);
            toast.error("Failed to delete contact");
        }
    };

    const openContactDetail = (contact: Contact) => {
        setSelectedContact(contact);
        setAdminNotes(contact.admin_notes || "");
        setIsDetailOpen(true);
        // Mark as read if new
        if (contact.status === "new") {
            updateContactStatus(contact.id, "read");
        }
    };

    const STATUS_TONE: Record<string, Tone> = { new: "lime", read: "blue", responded: "green", archived: "slate" };
    const getStatusBadge = (status: string) => (
        <Pill dot tone={STATUS_TONE[status] || "slate"}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </Pill>
    );

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    return (
        <>
            <PageHeader
                eyebrow="Clients"
                title="Leads"
                description="Businesses that filled in the contact form on calleem.tech. This is your sales pipeline."
                actions={
                    <Button variant="outline" className="border-border bg-transparent text-foreground hover:bg-white/5" onClick={loadData} disabled={loading}>
                        <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} /> Refresh
                    </Button>
                }
            />

            {stats && (
                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <StatCard label="All leads" value={stats.total} hint="Since launch" icon={Users} tone="lime" />
                    <StatCard label="New" value={stats.new} hint={stats.new ? "Not opened yet" : "All caught up"} icon={Clock} tone={stats.new ? "amber" : "slate"} />
                    <StatCard label="Today" value={stats.today} hint="Submitted today" icon={Calendar} tone="blue" />
                    <StatCard label="This month" value={stats.this_month} hint={`${stats.responded} responded so far`} icon={MessageSquare} tone="green" />
                </div>
            )}

            <Panel
                bodyClassName="p-0"
                title={`${contacts.length} lead${contacts.length !== 1 ? "s" : ""}`}
                actions={
                    <div className="flex items-center gap-2">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                                placeholder="Search name, email or business…"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="h-9 w-[280px] rounded-xl pl-9"
                            />
                        </div>
                        <Select value={statusFilter} onValueChange={setStatusFilter}>
                            <SelectTrigger className="h-9 w-[150px] rounded-xl">
                                <SelectValue placeholder="Filter by status" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All statuses</SelectItem>
                                <SelectItem value="new">New</SelectItem>
                                <SelectItem value="read">Read</SelectItem>
                                <SelectItem value="responded">Responded</SelectItem>
                                <SelectItem value="archived">Archived</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                }
            >
                {loading ? (
                    <LoadingState label="Loading leads…" />
                ) : contacts.length === 0 ? (
                    <EmptyState icon={MessageSquare} title="No leads found" hint="Contact-form submissions will show up here." />
                ) : (
                    <ul className="divide-y divide-border">
                        {contacts.map((contact) => (
                            <li
                                key={contact.id}
                                onClick={() => openContactDetail(contact)}
                                className="flex cursor-pointer gap-4 px-5 py-4 transition-colors hover:bg-white/[0.02]"
                            >
                                <Avatar name={contact.business_name} className="mt-0.5 from-sky-600 to-slate-800" />
                                <div className="min-w-0 flex-1">
                                    <div className="flex flex-wrap items-center gap-2">
                                        <p className="font-medium text-foreground">{contact.business_name}</p>
                                        {getStatusBadge(contact.status)}
                                        <span className="text-xs text-muted-foreground">
                                            {contact.business_type} · {contact.monthly_calls} calls/mo
                                        </span>
                                    </div>
                                    <p className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                                        <span>{contact.full_name}</span>
                                        <span className="flex items-center gap-1">
                                            <Mail className="size-3" />
                                            {contact.email}
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <Phone className="size-3" />
                                            {contact.phone_number}
                                        </span>
                                    </p>
                                    {contact.message && <p className="mt-2 line-clamp-2 text-sm text-[#b9c7bf]">“{contact.message}”</p>}
                                </div>
                                <p className="shrink-0 text-xs text-muted-foreground">{formatDate(contact.created_at)}</p>
                            </li>
                        ))}
                    </ul>
                )}
            </Panel>

            {/* Contact Detail Modal */}
            <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                    {selectedContact && (
                        <>
                            <DialogHeader>
                                <DialogTitle className="flex items-center justify-between">
                                    <span>{selectedContact.full_name}</span>
                                    {getStatusBadge(selectedContact.status)}
                                </DialogTitle>
                                <DialogDescription>
                                    Submitted on {formatDate(selectedContact.created_at)}
                                </DialogDescription>
                            </DialogHeader>

                            <div className="space-y-6">
                                {/* Contact Info */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-sm font-medium text-muted-foreground">Email</label>
                                        <p className="flex items-center gap-2">
                                            <Mail className="w-4 h-4" />
                                            <a href={`mailto:${selectedContact.email}`} className="text-primary hover:underline">
                                                {selectedContact.email}
                                            </a>
                                        </p>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-muted-foreground">Phone</label>
                                        <p className="flex items-center gap-2">
                                            <Phone className="w-4 h-4" />
                                            <a href={`tel:${selectedContact.phone_number}`} className="text-primary hover:underline">
                                                {selectedContact.phone_number}
                                            </a>
                                        </p>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-muted-foreground">Business Name</label>
                                        <p className="flex items-center gap-2">
                                            <Building2 className="w-4 h-4" />
                                            {selectedContact.business_name}
                                        </p>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-muted-foreground">Business Type</label>
                                        <p>{selectedContact.business_type}</p>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-muted-foreground">Monthly Calls</label>
                                        <p>{selectedContact.monthly_calls}</p>
                                    </div>
                                    <div>
                                        <label className="text-sm font-medium text-muted-foreground">Newsletter</label>
                                        <p>{selectedContact.newsletter ? "Yes" : "No"}</p>
                                    </div>
                                </div>

                                {/* Message */}
                                {selectedContact.message && (
                                    <div>
                                        <label className="text-sm font-medium text-muted-foreground">Message</label>
                                        <p className="mt-1 p-3 bg-muted rounded-lg">{selectedContact.message}</p>
                                    </div>
                                )}

                                {/* Status Update */}
                                <div>
                                    <label className="text-sm font-medium text-muted-foreground">Update Status</label>
                                    <Select
                                        value={selectedContact.status}
                                        onValueChange={(value) => updateContactStatus(selectedContact.id, value)}
                                    >
                                        <SelectTrigger className="mt-1">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="new">New</SelectItem>
                                            <SelectItem value="read">Read</SelectItem>
                                            <SelectItem value="responded">Responded</SelectItem>
                                            <SelectItem value="archived">Archived</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                {/* Admin Notes */}
                                <div>
                                    <label className="text-sm font-medium text-muted-foreground">Admin Notes</label>
                                    <Textarea
                                        value={adminNotes}
                                        onChange={(e) => setAdminNotes(e.target.value)}
                                        placeholder="Add notes about this contact..."
                                        className="mt-1"
                                        rows={3}
                                    />
                                    <Button
                                        onClick={() => updateAdminNotes(selectedContact.id)}
                                        size="sm"
                                        className="mt-2"
                                    >
                                        Save Notes
                                    </Button>
                                </div>
                            </div>

                            <DialogFooter className="flex justify-between">
                                <Button
                                    variant="destructive"
                                    onClick={() => deleteContact(selectedContact.id)}
                                >
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Delete
                                </Button>
                                <Button variant="outline" onClick={() => setIsDetailOpen(false)}>
                                    Close
                                </Button>
                            </DialogFooter>
                        </>
                    )}
                </DialogContent>
            </Dialog>
        </>
    );
}
