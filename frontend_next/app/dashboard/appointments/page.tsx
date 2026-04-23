"use client";

import { useState } from "react";
import { Plus, Search, Filter, Clock, Tag, Pencil, Trash2, XCircle, ArrowRight } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { appointmentsApi } from "@/lib/api-endpoints";
import { useRouter } from "next/navigation";
import type { AppointmentResponse } from "@/lib/types";
import AppointmentFormModal from "@/components/dashboard/appointments/AppointmentFormModal";
import { toast } from "sonner";
import Link from "next/link";
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
        staleTime: 0,
        refetchOnWindowFocus: true,
    });

    const deleteMutation = useMutation({
        mutationFn: appointmentsApi.delete,
        onMutate: async (deletedId) => {
            await queryClient.cancelQueries({ queryKey: ["appointments"] });
            const previousAppointments = queryClient.getQueryData(["appointments"]);
            queryClient.setQueryData(["appointments"], (old: any) =>
                old?.filter((appointment: any) => appointment.id !== deletedId) || []
            );
            return { previousAppointments };
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
            refetch();
            toast.success("Appointment permanently deleted");
            setDeleteDialogOpen(false);
            setAppointmentToDelete(null);
        },
        onError: (error: any, deletedId, context: any) => {
            if (context?.previousAppointments) {
                queryClient.setQueryData(["appointments"], context.previousAppointments);
            }
            const errorMessage = error?.response?.data?.detail || "Failed to delete appointment";
            toast.error(errorMessage);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
        },
    });

    const cancelMutation = useMutation({
        mutationFn: (id: string) => appointmentsApi.cancel(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
            refetch();
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
            case 'confirmed': return 'bg-green-100 text-green-700';
            case 'completed': return 'bg-gray-100 text-gray-600';
            case 'cancelled': return 'bg-red-100 text-red-700';
            case 'pending': return 'bg-yellow-100 text-yellow-700';
            case 'no_show': return 'bg-gray-100 text-gray-700';
            default: return 'bg-gray-100 text-gray-700';
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
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Appointments</h1>
                    <p className="text-[14px] text-gray-500 font-medium">Manage and review your daily bookings.</p>
                </div>
                <div className="flex gap-2">
                    <Link
                        href="/dashboard/schedule"
                        className="px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-[20px] font-semibold hover:bg-gray-50 transition-colors flex items-center gap-2 text-sm shadow-sm"
                    >
                        <ArrowRight className="w-4 h-4" />
                        Calendar
                    </Link>
                    <button
                        onClick={handleCreate}
                        className="px-6 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] hover:from-[#1b8550] hover:via-[#0c5c39] hover:to-[#073922] text-white rounded-[20px] font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] flex items-center gap-2 relative overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                        <Plus className="w-5 h-5 relative z-10" />
                        <span className="relative z-10">New Booking</span>
                    </button>
                </div>
            </div>

            {/* Search & Filters */}
            <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-4 mb-6">
                <div className="flex gap-3">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search by client name or phone..."
                            className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                        />
                    </div>
                    <button className="px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors flex items-center gap-2 text-sm">
                        <Filter className="w-4 h-4" />
                        Filter
                    </button>
                </div>
            </div>

            {/* Appointments Table */}
            <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6 flex-1 overflow-hidden flex flex-col">
                {isLoading ? (
                    <div className="p-8 text-center">
                        <p className="text-gray-500">Loading appointments...</p>
                    </div>
                ) : appointments.length === 0 ? (
                    <div className="p-8 text-center">
                        <p className="text-gray-500 mb-4">No appointments found</p>
                        <button
                            onClick={handleCreate}
                            className="px-6 py-2.5 bg-[#0a4c2f] hover:bg-[#073922] text-white rounded-[20px] font-medium transition-colors shadow-sm flex items-center gap-2 mx-auto"
                        >
                            <Plus className="w-5 h-5" />
                            <span>Create First Appointment</span>
                        </button>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse min-w-[700px]">
                            <thead>
                                <tr className="border-b border-gray-100">
                                    <th className="pb-4 font-semibold text-gray-500 text-sm">Customer</th>
                                    <th className="pb-4 font-semibold text-gray-500 text-sm">Service</th>
                                    <th className="pb-4 font-semibold text-gray-500 text-sm">Time</th>
                                    <th className="pb-4 font-semibold text-gray-500 text-sm">Status</th>
                                    <th className="pb-4 font-semibold text-gray-500 text-sm">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {appointments.map((apt: AppointmentResponse) => {
                                    const { date, time } = formatDateTime(apt.datetime);
                                    return (
                                        <tr key={apt.id} className="border-b border-gray-50/50 hover:bg-gray-50/50 transition-colors group">
                                            <td className="py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 font-bold shrink-0">
                                                        {apt.client_name?.split(' ').map((n: string) => n[0]).join('') || '?'}
                                                    </div>
                                                    <div className="flex flex-col">
                                                        <span className="font-semibold text-gray-900">{apt.client_name}</span>
                                                        <span className="text-xs text-gray-500">{apt.client_phone}</span>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="py-4">
                                                <div className="flex items-center gap-2">
                                                    <Tag className="w-4 h-4 text-gray-400" />
                                                    <span className="text-sm font-medium text-gray-700">{apt.service || "N/A"}</span>
                                                </div>
                                            </td>
                                            <td className="py-4">
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-bold text-gray-900 flex items-center gap-2">
                                                        <Clock className="w-4 h-4 text-gray-400" /> {date}
                                                    </span>
                                                    <span className="text-xs text-gray-500 ml-6">{time}</span>
                                                </div>
                                            </td>
                                            <td className="py-4">
                                                <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getStatusColor(apt.status)}`}>
                                                    {apt.status.charAt(0).toUpperCase() + apt.status.slice(1)}
                                                </span>
                                            </td>
                                            <td className="py-4">
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => handleEdit(apt)}
                                                        className="p-2 text-gray-400 hover:text-[#0a4c2f] hover:bg-[#0a4c2f]/5 rounded-lg transition-colors"
                                                        title="Edit"
                                                    >
                                                        <Pencil className="w-4 h-4" />
                                                    </button>
                                                    {apt.status !== 'cancelled' && (
                                                        <button
                                                            onClick={() => handleCancelClick(apt)}
                                                            className="p-2 text-gray-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"
                                                            title="Cancel"
                                                        >
                                                            <XCircle className="w-4 h-4" />
                                                        </button>
                                                    )}
                                                    <button
                                                        onClick={() => handleDeleteClick(apt.id)}
                                                        className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
                                                        title="Delete"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
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

            <AppointmentFormModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                appointment={selectedAppointment}
                mode={modalMode}
            />

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
                        <AlertDialogAction onClick={handleCancelConfirm} className="bg-amber-500 hover:bg-amber-600">
                            Cancel Appointment
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

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
                        <AlertDialogAction onClick={handleDeleteConfirm} className="bg-red-500 hover:bg-red-600">
                            Permanently Delete
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
