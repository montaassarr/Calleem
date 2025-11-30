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
import { Calendar } from "@/components/ui/calendar";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { toast } from "sonner";
import { Loader2, Calendar as CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

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
    date: Date | undefined;
    time: string;
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
        date: undefined,
        time: "",
        duration_minutes: 30,
        notes: "",
    });

    // Generate time slots (every 15 mins)
    const timeSlots = [];
    for (let i = 0; i < 24 * 4; i++) {
        const hour = Math.floor(i / 4);
        const minute = (i % 4) * 15;
        const date = new Date();
        date.setHours(hour, minute);
        const timeString = format(date, "h:mm a"); // 9:00 AM
        const value = `${hour.toString().padStart(2, "0")}:${minute.toString().padStart(2, "0")}`; // 09:00
        timeSlots.push({ value, label: timeString });
    }

    // Fetch active services for dropdown
    const { data: services } = useQuery<ServiceResponse[]>({
        queryKey: ["services"],
        queryFn: () => servicesApi.list(),
    });

    // Pre-fill form when editing
    useEffect(() => {
        if (mode === "edit" && appointment) {
            const dateObj = new Date(appointment.datetime);
            const hours = String(dateObj.getHours()).padStart(2, "0");
            const minutes = String(dateObj.getMinutes()).padStart(2, "0");

            setFormData({
                client_name: appointment.client_name,
                client_phone: appointment.client_phone,
                service: appointment.service || "",
                date: dateObj,
                time: `${hours}:${minutes}`,
                duration_minutes: appointment.duration_minutes || 30,
                notes: appointment.notes || "",
            });
        } else {
            // Reset for create mode
            setFormData({
                client_name: "",
                client_phone: "",
                service: "",
                date: undefined,
                time: "09:00", // Default to 9 AM
                duration_minutes: 30,
                notes: "",
            });
        }
    }, [mode, appointment, open]);

    // Create mutation
    const createMutation = useMutation({
        mutationFn: appointmentsApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
            queryClient.refetchQueries({ queryKey: ["appointments"] });
            toast.success("Appointment created successfully!");
            onOpenChange(false);
        },
        onError: (error: any) => {
            console.error("Create error:", error);
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
            queryClient.invalidateQueries({ queryKey: ["appointments"] });
            queryClient.refetchQueries({ queryKey: ["appointments"] });
            toast.success("Appointment updated successfully!");
            onOpenChange(false);
        },
        onError: (error: any) => {
            console.error("Update error:", error);
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
        if (!formData.client_name || !formData.client_phone || !formData.service || !formData.date || !formData.time) {
            toast.error("Please fill in all required fields");
            return;
        }

        // Combine date and time
        const [hours, minutes] = formData.time.split(":").map(Number);
        const combinedDate = new Date(formData.date);
        combinedDate.setHours(hours, minutes, 0, 0);

        // Convert to ISO string
        const isoDatetime = combinedDate.toISOString();

        if (mode === "create") {
            const createData: AppointmentCreate = {
                client_name: formData.client_name,
                client_phone: formData.client_phone,
                service: formData.service,
                datetime: isoDatetime,
                duration_minutes: formData.duration_minutes,
                notes: formData.notes,
            };
            createMutation.mutate(createData);
        } else if (appointment?.id) {
            const updateData: AppointmentUpdate = {};

            if (formData.client_name && formData.client_name !== appointment.client_name) {
                updateData.client_name = formData.client_name;
            }
            if (formData.service && formData.service !== appointment.service) {
                updateData.service = formData.service;
            }
            if (isoDatetime !== appointment.datetime) {
                updateData.datetime = isoDatetime;
            }
            if (formData.duration_minutes && formData.duration_minutes !== appointment.duration_minutes) {
                updateData.duration_minutes = formData.duration_minutes;
            }
            if (formData.notes !== appointment.notes) {
                updateData.notes = formData.notes || undefined;
            }

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
                                        )) || []}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Date & Time */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label>Date <span className="text-red-500">*</span></Label>
                                <Popover>
                                    <PopoverTrigger asChild>
                                        <Button
                                            variant={"outline"}
                                            className={cn(
                                                "w-full justify-start text-left font-normal",
                                                !formData.date && "text-muted-foreground"
                                            )}
                                        >
                                            <CalendarIcon className="mr-2 h-4 w-4" />
                                            {formData.date ? format(formData.date, "PPP") : <span>Pick a date</span>}
                                        </Button>
                                    </PopoverTrigger>
                                    <PopoverContent className="w-auto p-0">
                                        <Calendar
                                            mode="single"
                                            selected={formData.date}
                                            onSelect={(date) => setFormData({ ...formData, date })}
                                            initialFocus
                                        />
                                    </PopoverContent>
                                </Popover>
                            </div>
                            <div className="grid gap-2">
                                <Label>Time <span className="text-red-500">*</span></Label>
                                <Select
                                    value={formData.time}
                                    onValueChange={(value) => setFormData({ ...formData, time: value })}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select time" />
                                    </SelectTrigger>
                                    <SelectContent className="max-h-[200px]">
                                        {timeSlots.map((slot) => (
                                            <SelectItem key={slot.value} value={slot.value}>
                                                {slot.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        {/* Duration */}
                        <div className="grid gap-2">
                            <Label htmlFor="duration">Duration (minutes)</Label>
                            <Input
                                id="duration"
                                type="number"
                                min="15"
                                step="15"
                                value={formData.duration_minutes || 30}
                                onChange={(e) =>
                                    setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 30 })
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
