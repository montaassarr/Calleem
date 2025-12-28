"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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

            const response = await fetch(`${API_BASE}/api/v1/contacts?${params}`);
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
            const response = await fetch(`${API_BASE}/api/v1/contacts/stats`);
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
                headers: { "Content-Type": "application/json" },
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
                headers: { "Content-Type": "application/json" },
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

    const getStatusBadge = (status: string) => {
        const variants: Record<string, { color: string; icon: React.ReactNode }> = {
            new: { color: "bg-blue-500", icon: <Clock className="w-3 h-3" /> },
            read: { color: "bg-yellow-500", icon: <Eye className="w-3 h-3" /> },
            responded: { color: "bg-green-500", icon: <CheckCircle className="w-3 h-3" /> },
            archived: { color: "bg-gray-500", icon: <Archive className="w-3 h-3" /> },
        };
        const variant = variants[status] || variants.new;
        return (
            <Badge className={`${variant.color} text-white flex items-center gap-1`}>
                {variant.icon}
                {status.charAt(0).toUpperCase() + status.slice(1)}
            </Badge>
        );
    };

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
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Contact Submissions</h1>
                    <p className="text-muted-foreground">
                        Manage contact form submissions from the landing page
                    </p>
                </div>
                <Button onClick={loadData} disabled={loading}>
                    <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                    Refresh
                </Button>
            </div>

            {/* Stats Cards */}
            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Total</p>
                                    <p className="text-2xl font-bold">{stats.total}</p>
                                </div>
                                <Users className="w-8 h-8 text-primary opacity-50" />
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">New</p>
                                    <p className="text-2xl font-bold text-blue-500">{stats.new}</p>
                                </div>
                                <Clock className="w-8 h-8 text-blue-500 opacity-50" />
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Today</p>
                                    <p className="text-2xl font-bold text-green-500">{stats.today}</p>
                                </div>
                                <Calendar className="w-8 h-8 text-green-500 opacity-50" />
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="pt-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">This Month</p>
                                    <p className="text-2xl font-bold">{stats.this_month}</p>
                                </div>
                                <MessageSquare className="w-8 h-8 text-primary opacity-50" />
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Filters */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                            <Input
                                placeholder="Search by name, email, or business..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                        <Select value={statusFilter} onValueChange={setStatusFilter}>
                            <SelectTrigger className="w-[180px]">
                                <SelectValue placeholder="Filter by status" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Status</SelectItem>
                                <SelectItem value="new">New</SelectItem>
                                <SelectItem value="read">Read</SelectItem>
                                <SelectItem value="responded">Responded</SelectItem>
                                <SelectItem value="archived">Archived</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </CardContent>
            </Card>

            {/* Contacts List */}
            <Card>
                <CardHeader>
                    <CardTitle>All Contacts</CardTitle>
                    <CardDescription>
                        {contacts.length} contact{contacts.length !== 1 ? "s" : ""} found
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="flex items-center justify-center py-12">
                            <RefreshCw className="w-8 h-8 animate-spin text-primary" />
                        </div>
                    ) : contacts.length === 0 ? (
                        <div className="text-center py-12 text-muted-foreground">
                            <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                            <p>No contacts found</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {contacts.map((contact) => (
                                <div
                                    key={contact.id}
                                    onClick={() => openContactDetail(contact)}
                                    className="p-4 border rounded-lg hover:bg-accent cursor-pointer transition-colors"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                                <h3 className="font-semibold">{contact.full_name}</h3>
                                                {getStatusBadge(contact.status)}
                                            </div>
                                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                                <span className="flex items-center gap-1">
                                                    <Building2 className="w-3 h-3" />
                                                    {contact.business_name}
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <Mail className="w-3 h-3" />
                                                    {contact.email}
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <Phone className="w-3 h-3" />
                                                    {contact.phone_number}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="text-sm text-muted-foreground">
                                            {formatDate(contact.created_at)}
                                        </div>
                                    </div>
                                    {contact.message && (
                                        <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
                                            {contact.message}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

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
        </div>
    );
}
