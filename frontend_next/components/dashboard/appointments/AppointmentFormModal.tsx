import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
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
}

export default function AppointmentFormModal({
    open,
    onOpenChange,
    appointment,
    mode,
}: AppointmentFormModalProps) {
    const { formData, setFormData, services, timeSlots, submit, isLoading } = useAppointmentForm({
        mode,
        appointment,
        onSuccess: () => onOpenChange(false),
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        submit();
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px] p-0 rounded-[24px]">
                <form onSubmit={handleSubmit}>
                    <div className="px-6 pt-6 pb-4 border-b border-gray-100">
                        <DialogHeader>
                            <DialogTitle className="text-xl font-bold text-gray-900">
                                {mode === "create" ? "Create New Appointment" : "Edit Appointment"}
                            </DialogTitle>
                            <DialogDescription className="text-sm text-gray-500">
                                {mode === "create" ? "Schedule a new appointment for a client." : "Update appointment details below."}
                            </DialogDescription>
                        </DialogHeader>
                    </div>

                    <div className="px-6 py-5 space-y-4 max-h-[65vh] overflow-y-auto">
                        {/* Client Name */}
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Client Name <span className="text-red-500">*</span></label>
                            <input
                                value={formData.client_name}
                                onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                                placeholder="John Doe"
                                required
                                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                            />
                        </div>

                        {/* Client Phone */}
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Phone Number <span className="text-red-500">*</span></label>
                            <input
                                type="tel"
                                value={formData.client_phone}
                                onChange={(e) => setFormData({ ...formData, client_phone: e.target.value })}
                                placeholder="+1234567890"
                                required
                                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                            />
                        </div>

                        {/* Service */}
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Service <span className="text-red-500">*</span></label>
                            <Select value={formData.service} onValueChange={(value) => setFormData({ ...formData, service: value })}>
                                <SelectTrigger className="bg-gray-50 border-gray-200 rounded-xl focus:ring-[#0a4c2f]/20">
                                    <SelectValue placeholder="Select a service" />
                                </SelectTrigger>
                                <SelectContent>
                                    {services?.filter((s: any) => s.active).map((svc: any) => (
                                        <SelectItem key={svc.id} value={svc.name}>
                                            {svc.name} ({svc.duration_minutes} min - ${svc.price})
                                        </SelectItem>
                                    )) || []}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Date & Time */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-gray-700">Date <span className="text-red-500">*</span></label>
                                <Popover>
                                    <PopoverTrigger asChild>
                                        <button
                                            type="button"
                                            className={cn(
                                                "w-full flex items-center gap-2 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-left font-normal hover:bg-gray-100 transition-colors",
                                                !formData.date && "text-gray-400"
                                            )}
                                        >
                                            <CalendarIcon className="h-4 w-4 text-gray-400 shrink-0" />
                                            {formData.date ? format(formData.date, "PPP") : "Pick a date"}
                                        </button>
                                    </PopoverTrigger>
                                    <PopoverContent className="w-auto p-0 rounded-xl">
                                        <Calendar
                                            mode="single"
                                            selected={formData.date}
                                            onSelect={(date) => setFormData({ ...formData, date })}
                                            initialFocus
                                        />
                                    </PopoverContent>
                                </Popover>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-gray-700">Time <span className="text-red-500">*</span></label>
                                <Select value={formData.time} onValueChange={(value) => setFormData({ ...formData, time: value })}>
                                    <SelectTrigger className="bg-gray-50 border-gray-200 rounded-xl focus:ring-[#0a4c2f]/20">
                                        <SelectValue placeholder="Select time" />
                                    </SelectTrigger>
                                    <SelectContent className="max-h-[200px]">
                                        {timeSlots.map((slot) => (
                                            <SelectItem key={slot.value} value={slot.value}>{slot.label}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        {/* Duration */}
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Duration (minutes)</label>
                            <input
                                type="number"
                                min="15"
                                step="15"
                                value={formData.duration_minutes || 30}
                                onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) || 30 })}
                                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                            />
                        </div>

                        {/* Notes */}
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-gray-700">Notes</label>
                            <textarea
                                value={formData.notes}
                                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                placeholder="Any special instructions or notes..."
                                rows={3}
                                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all resize-none"
                            />
                        </div>
                    </div>

                    <div className="px-6 pb-6 pt-2 flex justify-end gap-2 border-t border-gray-100">
                        <button type="button" onClick={() => onOpenChange(false)} disabled={isLoading} className="px-5 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-colors text-sm">
                            Cancel
                        </button>
                        <button type="submit" disabled={isLoading} className="px-5 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-xl font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] relative overflow-hidden disabled:opacity-50 flex items-center gap-2 text-sm">
                            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                            {isLoading && <Loader2 className="w-4 h-4 animate-spin relative z-10" />}
                            <span className="relative z-10">{mode === "create" ? "Create Appointment" : "Save Changes"}</span>
                        </button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    );
}
