"use client";

import { useState } from "react";
import { Switch } from "@/components/ui/switch";
import { Plus, Pencil, Trash2, Clock, DollarSign, ArrowUpRight } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { servicesApi } from "@/lib/api-endpoints";
import type { ServiceResponse } from "@/lib/types";
import { toast } from "sonner";
import ServiceFormModal from "@/components/dashboard/ServiceFormModal";
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

const serviceColors = [
    "from-[#187848] to-[#0a4c2f]",
    "from-[#ff9f2d] to-[#e8870a]",
    "from-[#5b8eff] to-[#3d6ee0]",
    "from-[#e14949] to-[#c23030]",
    "from-[#8b5cf6] to-[#6d3fcf]",
    "from-[#187848] to-[#0a4c2f]",
];

export default function ServicesPage() {
    const queryClient = useQueryClient();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<"create" | "edit">("create");
    const [selectedService, setSelectedService] = useState<ServiceResponse | null>(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [serviceToDelete, setServiceToDelete] = useState<string | null>(null);

    const { data: services = [], isLoading } = useQuery({
        queryKey: ["services"],
        queryFn: () => servicesApi.list({ active_only: false }),
    });

    const toggleActiveMutation = useMutation({
        mutationFn: ({ id, active }: { id: string; active: boolean }) =>
            servicesApi.toggleActive(id, active),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["services"] });
            toast.success("Service status updated");
        },
        onError: () => {
            toast.error("Failed to update service status");
        },
    });

    const deleteMutation = useMutation({
        mutationFn: servicesApi.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["services"] });
            toast.success("Service deleted successfully");
            setDeleteDialogOpen(false);
            setServiceToDelete(null);
        },
        onError: () => {
            toast.error("Failed to delete service");
        },
    });

    const handleCreate = () => {
        setModalMode("create");
        setSelectedService(null);
        setIsModalOpen(true);
    };

    const handleEdit = (service: ServiceResponse) => {
        setModalMode("edit");
        setSelectedService(service);
        setIsModalOpen(true);
    };

    const handleDeleteClick = (id: string) => {
        setServiceToDelete(id);
        setDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = () => {
        if (serviceToDelete) {
            deleteMutation.mutate(serviceToDelete);
        }
    };

    const handleToggleActive = (id: string, currentStatus: boolean) => {
        toggleActiveMutation.mutate({ id, active: !currentStatus });
    };

    return (
        <div>
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Services</h1>
                    <p className="text-[14px] text-gray-500 font-medium">Manage your service offerings and pricing.</p>
                </div>
                <button
                    onClick={handleCreate}
                    className="px-6 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] hover:from-[#1b8550] hover:via-[#0c5c39] hover:to-[#073922] text-white rounded-[20px] font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] flex items-center gap-2 relative overflow-hidden"
                >
                    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                    <Plus className="w-5 h-5 relative z-10" />
                    <span className="relative z-10">New Service</span>
                </button>
            </div>

            {/* Services Grid */}
            {isLoading ? (
                <div className="flex items-center justify-center py-12">
                    <div className="w-8 h-8 border-2 border-[#0a4c2f] border-t-transparent rounded-full animate-spin"></div>
                </div>
            ) : services.length === 0 ? (
                <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-12 text-center">
                    <p className="text-gray-500 mb-4">No services found</p>
                    <button onClick={handleCreate} className="px-6 py-2.5 bg-[#0a4c2f] hover:bg-[#073922] text-white rounded-[20px] font-medium transition-colors">
                        Create your first service
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                    {services.map((service: ServiceResponse, idx: number) => (
                        <div
                            key={service.id}
                            className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 overflow-hidden hover:shadow-md transition-shadow group"
                        >
                            {/* Color header bar */}
                            <div className={`h-2 bg-gradient-to-r ${serviceColors[idx % serviceColors.length]}`}></div>

                            <div className="p-6">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-lg font-bold text-gray-900 mb-1 truncate">{service.name}</h3>
                                        <p className="text-sm text-gray-500 line-clamp-2">
                                            {service.description || "No description"}
                                        </p>
                                    </div>
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center border shrink-0 ml-3 ${service.active ? 'border-green-300 bg-green-50 text-green-700' : 'border-gray-200 bg-gray-50 text-gray-400'
                                        }`}>
                                        <ArrowUpRight className="w-4 h-4 stroke-[2.5px]" />
                                    </div>
                                </div>

                                <div className="flex items-center gap-4 mb-5">
                                    <div className="flex items-center gap-1.5 text-sm text-gray-600">
                                        <Clock className="w-4 h-4 text-gray-400" />
                                        <span className="font-medium">{service.duration_minutes} min</span>
                                    </div>
                                    <div className="flex items-center gap-1.5 text-sm text-gray-600">
                                        <DollarSign className="w-4 h-4 text-gray-400" />
                                        <span className="font-bold text-gray-900">${service.price.toFixed(2)}</span>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                                    <div className="flex items-center gap-2">
                                        <Switch
                                            checked={service.active}
                                            onCheckedChange={() => handleToggleActive(service.id, service.active)}
                                        />
                                        <span className={`text-xs font-bold ${service.active ? 'text-green-700' : 'text-gray-400'}`}>
                                            {service.active ? "Active" : "Inactive"}
                                        </span>
                                    </div>
                                    <div className="flex gap-1">
                                        <button
                                            onClick={() => handleEdit(service)}
                                            className="p-2 text-gray-400 hover:text-[#0a4c2f] hover:bg-[#0a4c2f]/5 rounded-lg transition-colors"
                                        >
                                            <Pencil className="w-4 h-4" />
                                        </button>
                                        <button
                                            onClick={() => handleDeleteClick(service.id)}
                                            className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <ServiceFormModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                service={selectedService}
                mode={modalMode}
            />

            <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Delete Service</AlertDialogTitle>
                        <AlertDialogDescription>
                            Are you sure you want to delete this service? This action cannot be undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleDeleteConfirm} className="bg-red-500 hover:bg-red-600">
                            Delete
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
