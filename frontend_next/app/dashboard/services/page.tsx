"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Plus, Pencil, Trash2, Clock, DollarSign } from "lucide-react";
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
        <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Services</h1>
                    <p className="text-muted-foreground">Manage your service offerings</p>
                </div>
                <Button
                    className="gap-2 bg-gradient-to-r from-primary to-accent hover:opacity-90"
                    onClick={handleCreate}
                >
                    <Plus className="w-4 h-4" />
                    New Service
                </Button>
            </div>

            {/* Services Grid */}
            <div className="bg-white border border-slate-200 shadow-sm p-6">
                {isLoading ? (
                    <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                ) : services.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-muted-foreground mb-4">No services found</p>
                        <Button onClick={handleCreate}>Create your first service</Button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {services.map((service: ServiceResponse) => (
                            <div
                                key={service.id}
                                className="bg-white border border-slate-200 shadow-sm p-6 hover:shadow-lg transition-shadow"
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex-1">
                                        <h3 className="text-lg font-semibold mb-2">{service.name}</h3>
                                        <p className="text-sm text-muted-foreground mb-4">
                                            {service.description || "No description"}
                                        </p>
                                    </div>
                                    <Badge variant={service.active ? "default" : "secondary"}>
                                        {service.active ? "Active" : "Inactive"}
                                    </Badge>
                                </div>

                                <div className="space-y-3 mb-4">
                                    <div className="flex items-center gap-2 text-sm">
                                        <Clock className="w-4 h-4 text-muted-foreground" />
                                        <span>{service.duration_minutes} minutes</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-sm">
                                        <DollarSign className="w-4 h-4 text-muted-foreground" />
                                        <span>${service.price.toFixed(2)}</span>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                                    <div className="flex items-center gap-2">
                                        <Switch
                                            checked={service.active}
                                            onCheckedChange={() => handleToggleActive(service.id, service.active)}
                                        />
                                        <span className="text-sm text-muted-foreground">Active</span>
                                    </div>
                                    <div className="flex gap-2">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleEdit(service)}
                                        >
                                            <Pencil className="w-4 h-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleDeleteClick(service.id)}
                                            className="text-red-500 hover:text-red-700"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Service Form Modal */}
            <ServiceFormModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                service={selectedService}
                mode={modalMode}
            />

            {/* Delete Confirmation Dialog */}
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
                        <AlertDialogAction
                            onClick={handleDeleteConfirm}
                            className="bg-red-500 hover:bg-red-600"
                        >
                            Delete
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
