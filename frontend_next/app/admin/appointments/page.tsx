"use client";

import React, { useEffect, useState } from 'react';
import { DataTable } from '@/components/admin/DataTable';
import { CrudModal } from '@/components/admin/CrudModal';
import { DeleteDialog } from '@/components/admin/DeleteDialog';
import { adminApi, Appointment } from '@/lib/api/admin';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { AppointmentResponse, AppointmentStatus } from "@/lib/types";
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '@/contexts/AuthContext';

export default function AppointmentsPage() {
    const { user: currentUser } = useAuth();
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [pageSize] = useState(10);
    const [statusFilter, setStatusFilter] = useState<string>('all');

    // Modal states
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [selectedAppt, setSelectedAppt] = useState<Appointment | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    type AppointmentForm = {
        client_name: string;
        client_phone: string;
        service: string;
        datetime: string;
        duration_minutes: number;
        status: AppointmentStatus;
        source: string;
        business_id: string;
        location_id: string;
        notes: string;
    };

    const initialFormState: AppointmentForm = {
        client_name: '',
        client_phone: '',
        service: '',
        datetime: '',
        duration_minutes: 30,
        status: 'confirmed',
        source: 'manual',
        business_id: currentUser?.business_id || currentUser?.tenant_id || '',
        location_id: '',
        notes: ''
    };

    const [formData, setFormData] = useState<AppointmentForm>(initialFormState);

    const { toast } = useToast();

    const fetchAppointments = async () => {
        try {
            setLoading(true);
            const filter = statusFilter !== 'all' ? statusFilter : undefined;
            const data = await adminApi.getAppointments((page - 1) * pageSize, pageSize, filter);

            if (Array.isArray(data)) {
                setAppointments(data);
                setTotal(data.length);
            } else {
                setAppointments(data.items || []);
                setTotal(data.total || 0);
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch appointments",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAppointments();
    }, [page, statusFilter]);

    const handleAdd = () => {
        setSelectedAppt(null);
        setFormData({
            ...initialFormState,
            datetime: new Date().toISOString().slice(0, 16),
            business_id: currentUser?.business_id || currentUser?.tenant_id || ''
        });
        setIsModalOpen(true);
    };

    const handleEdit = (appt: Appointment) => {
        setSelectedAppt(appt);
        setFormData({
            client_name: appt.client_name,
            client_phone: appt.client_phone,
            service: appt.service,
            datetime: new Date(appt.datetime).toISOString().slice(0, 16),
            duration_minutes: appt.duration_minutes,
            status: appt.status,
            source: appt.source || 'manual',
            business_id: appt.business_id || currentUser?.business_id || currentUser?.tenant_id || '',
            location_id: appt.location_id || '',
            notes: appt.notes || ''
        });
        setIsModalOpen(true);
    };

    const handleDeleteClick = (appt: Appointment) => {
        setSelectedAppt(appt);
        setIsDeleteOpen(true);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setIsSubmitting(true);
            const submitData: Partial<AppointmentResponse> = {
                ...formData,
                datetime: new Date(formData.datetime).toISOString()
            };

            if (selectedAppt) {
                await adminApi.updateAppointment(selectedAppt.id, submitData);
                toast({ title: "Success", description: "Appointment updated successfully" });
            } else {
                await adminApi.createAppointment(submitData);
                toast({ title: "Success", description: "Appointment created successfully" });
            }
            setIsModalOpen(false);
            fetchAppointments();
        } catch (error: any) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Operation failed",
                variant: "destructive"
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDeleteConfirm = async () => {
        if (!selectedAppt) return;
        try {
            setIsSubmitting(true);
            await adminApi.deleteAppointment(selectedAppt.id);
            toast({ title: "Success", description: "Appointment deleted successfully" });
            setIsDeleteOpen(false);
            fetchAppointments();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to delete appointment",
                variant: "destructive"
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const appointmentStatuses: AppointmentStatus[] = [
        'confirmed',
        'pending',
        'completed',
        'cancelled',
        'no_show'
    ];

    const statusStyles: Record<AppointmentStatus, string> = {
        confirmed: "bg-green-100 text-green-800 hover:bg-green-200",
        pending: "bg-yellow-100 text-yellow-800 hover:bg-yellow-200",
        cancelled: "bg-red-100 text-red-800 hover:bg-red-200",
        completed: "bg-blue-100 text-blue-800 hover:bg-blue-200",
        no_show: "bg-gray-100 text-gray-800 hover:bg-gray-200"
    };

    const formatStatusLabel = (status: AppointmentStatus) =>
        status
            .replace('_', ' ')
            .replace(/(^|\s)\w/g, (char) => char.toUpperCase());

    const getStatusBadge = (status: AppointmentStatus) => {
        return (
            <Badge className={statusStyles[status]}>
                {formatStatusLabel(status)}
            </Badge>
        );
    };

    const columns = [
        {
            key: 'datetime',
            label: 'Date & Time',
            render: (date: string) => new Date(date).toLocaleString()
        },
        { key: 'client_name', label: 'Client' },
        { key: 'service', label: 'Service' },
        {
            key: 'status',
            label: 'Status',
            render: (status: AppointmentStatus) => getStatusBadge(status)
        },
        {
            key: 'duration_minutes',
            label: 'Duration',
            render: (mins: number) => `${mins} min`
        }
    ];

    return (
        <div className="p-6">
            <div className="mb-4 flex items-center space-x-2">
                <span className="text-sm font-medium">Filter Status:</span>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="All Statuses" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Statuses</SelectItem>
                        <SelectItem value="confirmed">Confirmed</SelectItem>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                        <SelectItem value="no_show">No Show</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <DataTable
                title="Appointments"
                columns={columns}
                data={appointments}
                total={total}
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
                onAdd={handleAdd}
                onEdit={handleEdit}
                onDelete={handleDeleteClick}
                isLoading={loading}
            />

            <CrudModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                title={selectedAppt ? "Edit Appointment" : "New Appointment"}
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="client_name">Client Name</Label>
                            <Input
                                id="client_name"
                                value={formData.client_name}
                                onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="client_phone">Phone Number</Label>
                            <Input
                                id="client_phone"
                                value={formData.client_phone}
                                onChange={(e) => setFormData({ ...formData, client_phone: e.target.value })}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="service">Service</Label>
                            <Input
                                id="service"
                                value={formData.service}
                                onChange={(e) => setFormData({ ...formData, service: e.target.value })}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="datetime">Date & Time</Label>
                            <Input
                                id="datetime"
                                type="datetime-local"
                                value={formData.datetime}
                                onChange={(e) => setFormData({ ...formData, datetime: e.target.value })}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="duration">Duration (minutes)</Label>
                            <Input
                                id="duration"
                                type="number"
                                value={formData.duration_minutes}
                                onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="status">Status</Label>
                            <Select
                                value={formData.status}
                                onValueChange={(value) => setFormData({ ...formData, status: value as AppointmentStatus })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select status" />
                                </SelectTrigger>
                                <SelectContent>
                                    {appointmentStatuses.map((status) => (
                                        <SelectItem key={status} value={status}>
                                            {formatStatusLabel(status)}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="source">Source</Label>
                            <Select
                                value={formData.source}
                                onValueChange={(value) => setFormData({ ...formData, source: value })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select source" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="manual">Manual</SelectItem>
                                    <SelectItem value="phone">Phone Call</SelectItem>
                                    <SelectItem value="whatsapp">WhatsApp</SelectItem>
                                    <SelectItem value="web">Web Booking</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        {/* Only show business_id field for super_admin */}
                        {currentUser?.role === 'super_admin' && (
                            <div className="space-y-2">
                                <Label htmlFor="business_id">Business ID</Label>
                                <Input
                                    id="business_id"
                                    value={formData.business_id}
                                    onChange={(e) => setFormData({ ...formData, business_id: e.target.value })}
                                    placeholder="Auto-assigned if empty"
                                />
                            </div>
                        )}
                        <div className="space-y-2">
                            <Label htmlFor="location_id">Location ID</Label>
                            <Input
                                id="location_id"
                                value={formData.location_id}
                                onChange={(e) => setFormData({ ...formData, location_id: e.target.value })}
                                placeholder="Optional"
                            />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="notes">Notes</Label>
                        <Textarea
                            id="notes"
                            value={formData.notes}
                            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                        />
                    </div>
                    <div className="flex justify-end space-x-2 pt-4">
                        <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                        <Button type="submit" disabled={isSubmitting}>
                            {isSubmitting ? "Saving..." : "Save Appointment"}
                        </Button>
                    </div>
                </form>
            </CrudModal>

            <DeleteDialog
                open={isDeleteOpen}
                onOpenChange={setIsDeleteOpen}
                onConfirm={handleDeleteConfirm}
                title="Delete Appointment"
                description="Are you sure you want to delete this appointment?"
                isLoading={isSubmitting}
            />
        </div>
    );
}
