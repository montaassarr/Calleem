"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Search, Filter, Calendar as CalendarIcon, Pencil, Trash2, XCircle } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { appointmentsApi } from "@/lib/api-endpoints";
import { useRouter } from "next/navigation";
import type { AppointmentResponse } from "@/lib/types";
import AppointmentFormModal from "@/components/dashboard/AppointmentFormModal";
import { toast } from "sonner";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export default function AppointmentsPage() {
    const router = useRouter();
    const queryClient = useQueryClient();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<"create" | "edit">("create");
    const [selectedAppointment, setSelectedAppointment] = useState<AppointmentResponse | null>(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
    const [appointmentToDelete, setAppointmentToDelete] = useState<string | null>(null);
    const [appointmentToCancel, setAppointmentToCancel] = useState<string | null>(null);

    const { data: appointments = [], isLoading, refetch } = useQuery({
        queryKey: ["appointments"],
        queryFn: () => appointmentsApi.list(),
        staleTime: 0, // Always fetch fresh data
        refetchOnWindowFocus: true, // Refetch when window gains focus
    });

    // Delete mutation (permanently removes from database)
    const deleteMutation = useMutation({
        mutationFn: appointmentsApi.delete,
        // Optimistically update UI before API call completes
        onMutate: async (deletedId) => {
            // Cancel any outgoing refetches
            await queryClient.cancelQueries({ queryKey: ["appointments"] });

            // Snapshot the previous value
            const previousAppointments = queryClient.getQueryData(["appointments"]);

            // Optimistically update to the new value
            queryClient.setQueryData(["appointments"], (old: any) =>
                old?.filter((appointment: any) => appointment.id !== deletedId) || []
            );

            // Return context with snapshot
            return { previousAppointments };
        },
        onSuccess: () => {
            // Immediately refetch to get fresh data
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
            refetch(); // Force immediate refetch
            toast.success("Appointment permanently deleted");
            setDeleteDialogOpen(false);
            setAppointmentToDelete(null);
        },
        onError: (error: any, deletedId, context: any) => {
            // Rollback on error
            if (context?.previousAppointments) {
                queryClient.setQueryData(["appointments"], context.previousAppointments);
            }
            const errorMessage = error?.response?.data?.detail || "Failed to delete appointment";
            toast.error(errorMessage);
        },
        // Always refetch after error or success
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
        },
    });

    // Cancel mutation (updates status to 'cancelled')
    const cancelMutation = useMutation({
        mutationFn: (id: string) => appointmentsApi.cancel(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
            refetch(); // Force immediate refetch
            toast.success("Appointment cancelled successfully");
            setCancelDialogOpen(false);
            setAppointmentToCancel(null);
        },
        onError: (error: any) => {
            const errorMessage = error?.response?.data?.detail || "Failed to cancel appointment";
            toast.error(errorMessage);
        },
    });

    const handleCreate = () => {
        setModalMode("create");
        setSelectedAppointment(null);
        setIsModalOpen(true);
    };

    const handleEdit = (appointment: AppointmentResponse) => {
        setModalMode("edit");
        setSelectedAppointment(appointment);
        setIsModalOpen(true);
    };

    const handleCancelClick = (appointment: AppointmentResponse) => {
        setAppointmentToCancel(appointment.id);
        setCancelDialogOpen(true);
    };

    const handleCancelConfirm = () => {
        if (appointmentToCancel) {
            cancelMutation.mutate(appointmentToCancel);
        }
    };

    const handleDeleteClick = (id: string) => {
        setAppointmentToDelete(id);
        setDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = () => {
        if (appointmentToDelete) {
            deleteMutation.mutate(appointmentToDelete);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'confirmed':
                return 'bg-green-100 text-green-700 border-green-200';
            case 'completed':
                return 'bg-blue-100 text-blue-700 border-blue-200';
            case 'cancelled':
                return 'bg-red-100 text-red-700 border-red-200';
            case 'no_show':
                return 'bg-gray-100 text-gray-700 border-gray-200';
            default:
                return 'bg-gray-100 text-gray-700 border-gray-200';
        }
    };

    const formatDateTime = (datetime: string) => {
        const date = new Date(datetime);
        return {
            date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        };
    };

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Appointments</h1>
                    <p className="text-muted-foreground">Manage all your bookings and schedules</p>
                </div>
                <Button
                    className="gap-2 bg-gradient-to-r from-primary to-accent hover:opacity-90"
                    onClick={handleCreate}
                >
                    <Plus className="w-4 h-4" />
                    New Appointment
                </Button>
            </div>

            {/* Filters */}
            <div className="glass rounded-2xl p-4 mb-6">
                <div className="flex gap-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                            placeholder="Search by client name or phone..."
                            className="pl-10 glass-strong"
                        />
                    </div>
                    <Button variant="outline" className="gap-2">
                        <Filter className="w-4 h-4" />
                        Filter
                    </Button>
                    <Button variant="outline" className="gap-2">
                        <CalendarIcon className="w-4 h-4" />
                        Calendar View
                    </Button>
                </div>
            </div>

            {/* Appointments List */}
            <div className="glass rounded-2xl overflow-hidden">
                {isLoading ? (
                    <div className="p-8 text-center">
                        <p className="text-muted-foreground">Loading appointments...</p>
                    </div>
                ) : appointments.length === 0 ? (
                    <div className="p-8 text-center">
                        <p className="text-muted-foreground mb-4">No appointments found</p>
                        <Button onClick={handleCreate}>
                            <Plus className="w-4 h-4 mr-2" />
                            Create First Appointment
                        </Button>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-white/5 border-b border-white/10">
                                <tr>
                                    <th className="text-left p-4 font-semibold">Client</th>
                                    <th className="text-left p-4 font-semibold">Service</th>
                                    <th className="text-left p-4 font-semibold">Date</th>
                                    <th className="text-left p-4 font-semibold">Time</th>
                                    <th className="text-left p-4 font-semibold">Duration</th>
                                    <th className="text-left p-4 font-semibold">Status</th>
                                    <th className="text-left p-4 font-semibold">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {appointments.map((appointment: AppointmentResponse) => {
                                    const { date, time } = formatDateTime(appointment.datetime);
                                    return (
                                        <tr key={appointment.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                            <td className="p-4">
                                                <div>
                                                    <p className="font-medium">{appointment.client_name}</p>
                                                    <p className="text-sm text-muted-foreground">{appointment.client_phone}</p>
                                                </div>
                                            </td>
                                            <td className="p-4">{appointment.service || "N/A"}</td>
                                            <td className="p-4">{date}</td>
                                            <td className="p-4">{time}</td>
                                            <td className="p-4">{appointment.duration_minutes} min</td>
                                            <td className="p-4">
                                                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(appointment.status)}`}>
                                                    {appointment.status}
                                                </span>
                                            </td>
                                            <td className="p-4">
                                                <div className="flex gap-2">
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => handleEdit(appointment)}
                                                        title="Edit appointment"
                                                    >
                                                        <Pencil className="w-4 h-4" />
                                                    </Button>
                                                    {appointment.status !== 'cancelled' && (
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            onClick={() => handleCancelClick(appointment)}
                                                            className="text-cyan-500 hover:text-cyan-700"
                                                            title="Cancel appointment"
                                                        >
                                                            <XCircle className="w-4 h-4" />
                                                        </Button>
                                                    )}
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => handleDeleteClick(appointment.id)}
                                                        className="text-red-500 hover:text-red-700"
                                                        title="Permanently delete"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </Button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Appointment Form Modal */}
            <AppointmentFormModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                appointment={selectedAppointment}
                mode={modalMode}
            />

            {/* Cancel Confirmation Dialog */}
            <AlertDialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Cancel Appointment</AlertDialogTitle>
                        <AlertDialogDescription>
                            Are you sure you want to cancel this appointment? The appointment will be marked as cancelled but remain in the system for records.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Keep Appointment</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleCancelConfirm}
                            className="bg-cyan-500 hover:bg-cyan-600"
                        >
                            Cancel Appointment
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

            {/* Delete Confirmation Dialog */}
            <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Permanently Delete Appointment</AlertDialogTitle>
                        <AlertDialogDescription>
                            Are you sure you want to permanently delete this appointment? This will remove it completely from the database and cannot be undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleDeleteConfirm}
                            className="bg-red-500 hover:bg-red-600"
                        >
                            Permanently Delete
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
