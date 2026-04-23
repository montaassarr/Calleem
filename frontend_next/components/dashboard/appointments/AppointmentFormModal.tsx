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
import { Loader2, Calendar as CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { AppointmentResponse } from "@/lib/types";
import { useAppointmentForm } from "@/hooks/domain/useAppointmentForm";

interface AppointmentFormModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    appointment?: AppointmentResponse | null;
    mode: "create" | "edit";
    initialDate?: Date;
}

export default function AppointmentFormModal({
    open,
    onOpenChange,
    appointment,
    mode,
    initialDate,
}: AppointmentFormModalProps) {
    const { formData, setFormData, services, timeSlots, submit, isLoading } = useAppointmentForm({
        mode,
        appointment,
        initialDate,
        onSuccess: () => onOpenChange(false),
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        submit();
    };

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
                                        ?.filter((s: any) => s.active)
                                        .map((service: any) => (
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
