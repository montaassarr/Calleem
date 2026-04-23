import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { servicesApi } from "@/lib/api-endpoints";
import { ServiceCreate, ServiceResponse } from "@/lib/types";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
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
            setFormData({ name: "", description: "", duration_minutes: 30, price: 0, active: true });
        }
    }, [mode, service, open]);

    const createMutation = useMutation({
        mutationFn: servicesApi.create,
        onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["services"] }); toast.success("Service created successfully!"); onOpenChange(false); },
        onError: (error: any) => {
            if (error.response?.data?.detail) {
                const detail = error.response.data.detail;
                if (Array.isArray(detail)) { toast.error(detail.map((e: any) => `${e.loc?.join(' -> ') || 'Error'}: ${e.msg}`).join(', ')); }
                else if (typeof detail === 'string') { toast.error(detail); }
                else { toast.error("Failed to create service"); }
            } else { toast.error("Failed to create service"); }
        },
    });

    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: ServiceCreate }) => servicesApi.update(id, data),
        onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["services"] }); toast.success("Service updated successfully!"); onOpenChange(false); },
        onError: (error: any) => {
            if (error.response?.data?.detail) {
                const detail = error.response.data.detail;
                if (Array.isArray(detail)) { toast.error(detail.map((e: any) => `${e.loc?.join(' -> ') || 'Error'}: ${e.msg}`).join(', ')); }
                else if (typeof detail === 'string') { toast.error(detail); }
                else { toast.error("Failed to update service"); }
            } else { toast.error("Failed to update service"); }
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.name || formData.price < 0 || formData.duration_minutes < 1) { toast.error("Please fill in all required fields correctly"); return; }
        const submitData: ServiceCreate = { name: formData.name, description: formData.description, duration_minutes: formData.duration_minutes, price: formData.price, active: formData.active };
        if (mode === "create") { createMutation.mutate(submitData); }
        else if (service?.id) { updateMutation.mutate({ id: service.id, data: submitData }); }
    };

    const isLoading = createMutation.isPending || updateMutation.isPending;

    const fields = [
        { id: "name", label: "Service Name", required: true, type: "text", placeholder: "e.g., Haircut, Consultation, Massage" },
        { id: "description", label: "Description", required: false, type: "textarea", placeholder: "Brief description of the service..." },
        { id: "duration_minutes", label: "Duration (minutes)", required: true, type: "number", placeholder: "", min: "1", step: "5" },
        { id: "price", label: "Price ($)", required: true, type: "number", placeholder: "", min: "0", step: "0.01" },
    ];

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px] p-0 rounded-[24px]">
                <form onSubmit={handleSubmit}>
                    <div className="px-6 pt-6 pb-4 border-b border-gray-100">
                        <DialogHeader>
                            <DialogTitle className="text-xl font-bold text-gray-900">
                                {mode === "create" ? "Create New Service" : "Edit Service"}
                            </DialogTitle>
                            <DialogDescription className="text-sm text-gray-500">
                                {mode === "create" ? "Add a new service to your offerings." : "Update service details below."}
                            </DialogDescription>
                        </DialogHeader>
                    </div>

                    <div className="px-6 py-5 space-y-4">
                        {fields.map((field) => (
                            <div key={field.id} className="space-y-2">
                                <label htmlFor={field.id} className="text-sm font-semibold text-gray-700">
                                    {field.label} {field.required && <span className="text-red-500">*</span>}
                                </label>
                                {field.type === "textarea" ? (
                                    <textarea
                                        id={field.id}
                                        value={(formData as any)[field.id]}
                                        onChange={(e) => setFormData({ ...formData, [field.id]: e.target.value })}
                                        placeholder={field.placeholder}
                                        rows={3}
                                        className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all resize-none"
                                    />
                                ) : (
                                    <input
                                        id={field.id}
                                        type={field.type}
                                        min={field.min}
                                        step={field.step}
                                        value={(formData as any)[field.id]}
                                        onChange={(e) => setFormData({ ...formData, [field.id]: field.type === "number" ? (field.step === "0.01" ? parseFloat(e.target.value) || 0 : parseInt(e.target.value) || 0) : e.target.value })}
                                        placeholder={field.placeholder}
                                        required={field.required}
                                        className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
                                    />
                                )}
                            </div>
                        ))}

                        {/* Active Toggle */}
                        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                            <Switch
                                id="active"
                                checked={formData.active}
                                onCheckedChange={(checked) => setFormData({ ...formData, active: checked as boolean })}
                            />
                            <label htmlFor="active" className="text-sm font-medium text-gray-700">Active (visible to clients)</label>
                        </div>
                    </div>

                    <div className="px-6 pb-6 pt-2 flex justify-end gap-2">
                        <button type="button" onClick={() => onOpenChange(false)} disabled={isLoading} className="px-5 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-colors text-sm">
                            Cancel
                        </button>
                        <button type="submit" disabled={isLoading} className="px-5 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-xl font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] relative overflow-hidden disabled:opacity-50 flex items-center gap-2 text-sm">
                            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                            {isLoading && <Loader2 className="w-4 h-4 animate-spin relative z-10" />}
                            <span className="relative z-10">{mode === "create" ? "Create Service" : "Save Changes"}</span>
                        </button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    );
}
