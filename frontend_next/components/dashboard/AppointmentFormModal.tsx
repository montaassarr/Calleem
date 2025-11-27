import { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { appointmentsApi, servicesApi } from "@/lib/api-endpoints";
import { AppointmentCreate, AppointmentUpdate, AppointmentResponse, ServiceResponse } from "@/lib/types";
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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

interface AppointmentFormModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    appointment?: AppointmentResponse | null;
    mode: "create" | "edit";
}

interface FormData {
    client_name: string;
    client_phone: string;
    service: string;
    datetime: string;
    duration_minutes: number;
    notes?: string;
}

export default function AppointmentFormModal({
    open,
    onOpenChange,
    appointment,
    mode,
}: AppointmentFormModalProps) {
    const queryClient = useQueryClient();
    const [formData, setFormData] = useState<FormData>({
        client_name: "",
        client_phone: "",
        service: "",
        datetime: "",
        duration_minutes: 30,
        notes: "",
    });

    // Fetch active services for dropdown
    const { data: services } = useQuery<ServiceResponse[]>({
        queryKey: ["services"],
        queryFn: () => servicesApi.list(),
    });

    // Pre-fill form when editing
    useEffect(() => {
        if (mode === "edit" && appointment) {
            // Convert ISO datetime to datetime-local format (YYYY-MM-DDTHH:MM)
            const formatDatetimeForInput = (isoString: string) => {
                const date = new Date(isoString);
                // Get local datetime in YYYY-MM-DDTHH:MM format
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                return `${year}-${month}-${day}T${hours}:${minutes}`;
            };

            setFormData({
                client_name: appointment.client_name,
                client_phone: appointment.client_phone,
                service: appointment.service || "",
                datetime: formatDatetimeForInput(appointment.datetime),
                duration_minutes: appointment.duration_minutes || 30,
                notes: appointment.notes || "",
            });
        } else {
            // Reset for create mode
            setFormData({
                client_name: "",
                client_phone: "",
                service: "",
                datetime: "",
                duration_minutes: 30,
                notes: "",
            });
        }
    }, [mode, appointment, open]);

    // Create mutation
    const createMutation = useMutation({
        mutationFn: appointmentsApi.create,
        onSuccess: () => {
            // Force immediate refresh of appointments list
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
            queryClient.refetchQueries({ queryKey: ["appointments"] });
            toast.success("Appointment created successfully!");
            onOpenChange(false);
        },
        onError: (error: any) => {
            console.error("Create error:", error);
            // Handle validation errors from FastAPI
            if (error.response?.data?.detail) {
                const detail = error.response.data.detail;
                if (Array.isArray(detail)) {
                    // Pydantic validation errors
                    const errorMessages = detail.map((err: any) =>
                        `${err.loc?.join(' -> ') || 'Error'}: ${err.msg}`
                    ).join(', ');
                    toast.error(errorMessages);
                } else if (typeof detail === 'string') {
                    toast.error(detail);
                } else {
                    toast.error("Failed to create appointment");
                }
            } else {
                toast.error(error.message || "Failed to create appointment");
            }
        },
    });

    // Update mutation
    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: AppointmentUpdate }) =>
            appointmentsApi.update(id, data),
        onSuccess: () => {
            // Force immediate refresh of appointments list
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
            queryClient.refetchQueries({ queryKey: ["appointments"] });
            toast.success("Appointment updated successfully!");
            onOpenChange(false);
        },
        onError: (error: any) => {
            console.error("Update error:", error);
            // Handle validation errors from FastAPI
            if (error.response?.data?.detail) {
                const detail = error.response.data.detail;
                if (Array.isArray(detail)) {
                    // Pydantic validation errors
                    const errorMessages = detail.map((err: any) =>
                        `${err.loc?.join(' -> ') || 'Error'}: ${err.msg}`
                    ).join(', ');
                    toast.error(errorMessages);
                } else if (typeof detail === 'string') {
                    toast.error(detail);
                } else {
                    toast.error("Failed to update appointment");
                }
            } else {
                toast.error(error.message || "Failed to update appointment");
            }
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Validation
        if (!formData.client_name || !formData.client_phone || !formData.service || !formData.datetime) {
            toast.error("Please fill in all required fields");
            return;
        }

        // Convert datetime-local format to ISO 8601
        // datetime-local gives us "2025-11-15T14:30"
        // We need to convert it to "2025-11-15T14:30:00" (add seconds)
        const formattedDatetime = formData.datetime.includes(':')
            ? formData.datetime.length === 16
                ? `${formData.datetime}:00`  // Add seconds if missing
                : formData.datetime
            : formData.datetime;

        if (mode === "create") {
            // For create, send all fields as AppointmentCreate
            const createData: AppointmentCreate = {
                client_name: formData.client_name,
                client_phone: formData.client_phone,
                service: formData.service,
                datetime: formattedDatetime,
                duration_minutes: formData.duration_minutes,
                notes: formData.notes,
            };
            createMutation.mutate(createData);
        } else if (appointment?.id) {
            // For update, build object with only non-empty fields
            const updateData: AppointmentUpdate = {};

            // Only include fields that have values
            if (formData.client_name && formData.client_name !== appointment.client_name) {
                updateData.client_name = formData.client_name;
            }
            if (formData.service && formData.service !== appointment.service) {
                updateData.service = formData.service;
            }
            if (formData.datetime && formattedDatetime !== appointment.datetime) {
                updateData.datetime = formattedDatetime;
            }
            if (formData.duration_minutes && formData.duration_minutes !== appointment.duration_minutes) {
                updateData.duration_minutes = formData.duration_minutes;
            }
            if (formData.notes !== appointment.notes) {
                updateData.notes = formData.notes || undefined;
            }

            // Check if there are any changes
            if (Object.keys(updateData).length === 0) {
                toast.info("No changes to save");
                onOpenChange(false);
                return;
            }

            updateMutation.mutate({ id: appointment.id, data: updateData });
        }
    };

    const isLoading = createMutation.isPending || updateMutation.isPending;

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <form onSubmit={handleSubmit}>
                    <DialogHeader>
                        <DialogTitle>
                            {mode === "create" ? "Create New Appointment" : "Edit Appointment"}
                        </DialogTitle>
                        <DialogDescription>
                            {mode === "create"
                                ? "Schedule a new appointment for a client."
                                : "Update appointment details below."}
                        </DialogDescription>
                    </DialogHeader>

                    <div className="grid gap-4 py-4">
                        {/* Client Name */}
                        <div className="grid gap-2">
                            <Label htmlFor="client_name">
                                Client Name <span className="text-red-500">*</span>
                            </Label>
                            <Input
                                id="client_name"
                                value={formData.client_name}
                                onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                                placeholder="John Doe"
                                required
                            />
                        </div>

                        {/* Client Phone */}
                        <div className="grid gap-2">
                            <Label htmlFor="client_phone">
                                Phone Number <span className="text-red-500">*</span>
                            </Label>
                            <Input
                                id="client_phone"
                                type="tel"
                                value={formData.client_phone}
                                onChange={(e) => setFormData({ ...formData, client_phone: e.target.value })}
                                placeholder="+1234567890"
                                required
                            />
                        </div>

                        {/* Service */}
                        <div className="grid gap-2">
                            <Label htmlFor="service">
                                Service <span className="text-red-500">*</span>
                            </Label>
                            <Select
                                value={formData.service}
                                onValueChange={(value) => setFormData({ ...formData, service: value })}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a service" />
                                </SelectTrigger>
                                <SelectContent>
                                    {services
                                        ?.filter((s) => s.active)
                                        .map((service) => (
                                            <SelectItem key={service.id} value={service.name}>
                                                {service.name} ({service.duration_minutes} min - ${service.price})
                                            </SelectItem>
                                        ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Date & Time */}
                        <div className="grid gap-2">
                            <Label htmlFor="datetime">
                                Date & Time <span className="text-red-500">*</span>
                            </Label>
                            <Input
                                id="datetime"
                                type="datetime-local"
                                value={formData.datetime}
                                onChange={(e) =>
                                    setFormData({ ...formData, datetime: e.target.value })
                                }
                                required
                            />
                        </div>

                        {/* Duration */}
                        <div className="grid gap-2">
                            <Label htmlFor="duration">Duration (minutes)</Label>
                            <Input
                                id="duration"
                                type="number"
                                min="15"
                                step="15"
                                value={formData.duration_minutes}
                                onChange={(e) =>
                                    setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })
                                }
                            />
                        </div>

                        {/* Notes */}
                        <div className="grid gap-2">
                            <Label htmlFor="notes">Notes</Label>
                            <Textarea
                                id="notes"
                                value={formData.notes}
                                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                placeholder="Any special instructions or notes..."
                                rows={3}
                            />
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
                            {mode === "create" ? "Create Appointment" : "Save Changes"}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
