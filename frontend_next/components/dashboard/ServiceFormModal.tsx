import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { servicesApi } from "@/lib/api-endpoints";
import { ServiceCreate, ServiceResponse } from "@/lib/types";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

interface ServiceFormModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    service?: ServiceResponse | null;
    mode: "create" | "edit";
}

export default function ServiceFormModal({
    open,
    onOpenChange,
    service,
    mode,
}: ServiceFormModalProps) {
    const queryClient = useQueryClient();
    const [formData, setFormData] = useState<ServiceCreate & { active: boolean }>({
        name: "",
        description: "",
        duration_minutes: 30,
        price: 0,
        active: true,
    });

    // Pre-fill form when editing
    useEffect(() => {
        if (mode === "edit" && service) {
            setFormData({
                name: service.name,
                description: service.description || "",
                duration_minutes: service.duration_minutes,
                price: service.price,
                active: service.active,
            });
        } else {
            // Reset for create mode
            setFormData({
                name: "",
                description: "",
                duration_minutes: 30,
                price: 0,
                active: true,
            });
        }
    }, [mode, service, open]);

    // Create mutation
    const createMutation = useMutation({
        mutationFn: servicesApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["services"] });
            toast.success("Service created successfully!");
            onOpenChange(false);
        },
        onError: (error: any) => {
            // Handle validation errors from FastAPI
            if (error.response?.data?.detail) {
                const detail = error.response.data.detail;
                if (Array.isArray(detail)) {
                    const errorMessages = detail.map((err: any) =>
                        `${err.loc?.join(' -> ') || 'Error'}: ${err.msg}`
                    ).join(', ');
                    toast.error(errorMessages);
                } else if (typeof detail === 'string') {
                    toast.error(detail);
                } else {
                    toast.error("Failed to create service");
                }
            } else {
                toast.error("Failed to create service");
            }
        },
    });

    // Update mutation
    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: ServiceCreate }) =>
            servicesApi.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["services"] });
            toast.success("Service updated successfully!");
            onOpenChange(false);
        },
        onError: (error: any) => {
            // Handle validation errors from FastAPI
            if (error.response?.data?.detail) {
                const detail = error.response.data.detail;
                if (Array.isArray(detail)) {
                    const errorMessages = detail.map((err: any) =>
                        `${err.loc?.join(' -> ') || 'Error'}: ${err.msg}`
                    ).join(', ');
                    toast.error(errorMessages);
                } else if (typeof detail === 'string') {
                    toast.error(detail);
                } else {
                    toast.error("Failed to update service");
                }
            } else {
                toast.error("Failed to update service");
            }
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Validation
        if (!formData.name || formData.price < 0 || formData.duration_minutes < 1) {
            toast.error("Please fill in all required fields correctly");
            return;
        }

        const submitData: ServiceCreate = {
            name: formData.name,
            description: formData.description,
            duration_minutes: formData.duration_minutes,
            price: formData.price,
            active: formData.active,
        };

        if (mode === "create") {
            createMutation.mutate(submitData);
        } else if (service?.id) {
            updateMutation.mutate({ id: service.id, data: submitData });
        }
    };

    const isLoading = createMutation.isPending || updateMutation.isPending;

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <form onSubmit={handleSubmit}>
                    <DialogHeader>
                        <DialogTitle>
                            {mode === "create" ? "Create New Service" : "Edit Service"}
                        </DialogTitle>
                        <DialogDescription>
                            {mode === "create"
                                ? "Add a new service to your offerings."
                                : "Update service details below."}
                        </DialogDescription>
                    </DialogHeader>

                    <div className="grid gap-4 py-4">
                        {/* Service Name */}
                        <div className="grid gap-2">
                            <Label htmlFor="name">
                                Service Name <span className="text-red-500">*</span>
                            </Label>
                            <Input
                                id="name"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                placeholder="e.g., Haircut, Consultation, Massage"
                                required
                            />
                        </div>

                        {/* Description */}
                        <div className="grid gap-2">
                            <Label htmlFor="description">Description</Label>
                            <Textarea
                                id="description"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                placeholder="Brief description of the service..."
                                rows={3}
                            />
                        </div>

                        {/* Duration */}
                        <div className="grid gap-2">
                            <Label htmlFor="duration">
                                Duration (minutes) <span className="text-red-500">*</span>
                            </Label>
                            <Input
                                id="duration"
                                type="number"
                                min="1"
                                step="5"
                                value={formData.duration_minutes}
                                onChange={(e) =>
                                    setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 0 })
                                }
                                required
                            />
                        </div>

                        {/* Price */}
                        <div className="grid gap-2">
                            <Label htmlFor="price">
                                Price ($) <span className="text-red-500">*</span>
                            </Label>
                            <Input
                                id="price"
                                type="number"
                                min="0"
                                step="0.01"
                                value={formData.price}
                                onChange={(e) =>
                                    setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })
                                }
                                required
                            />
                        </div>

                        {/* Active Status */}
                        <div className="flex items-center space-x-2">
                            <Checkbox
                                id="active"
                                checked={formData.active}
                                onCheckedChange={(checked) =>
                                    setFormData({ ...formData, active: checked as boolean })
                                }
                            />
                            <Label
                                htmlFor="active"
                                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                            >
                                Active (visible to clients)
                            </Label>
                        </div>
                    </div>

                    <DialogFooter>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                            disabled={isLoading}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" disabled={isLoading}>
                            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            {mode === "create" ? "Create Service" : "Save Changes"}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
