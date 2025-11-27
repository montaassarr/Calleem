import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Plus, Trash2, Scissors } from "lucide-react";
import { useOnboarding } from "@/contexts/OnboardingContext";

export function ServicesStep() {
    const { data, updateData } = useOnboarding();

    const addService = () => {
        updateData({
            services: [
                ...data.services,
                { name: "", duration_minutes: 30, price: 0, description: "" },
            ],
        });
    };

    const removeService = (index: number) => {
        updateData({
            services: data.services.filter((_, i) => i !== index),
        });
    };

    const updateService = (index: number, field: string, value: any) => {
        const newServices = [...data.services];
        newServices[index] = { ...newServices[index], [field]: value };
        updateData({ services: newServices });
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="space-y-2">
                <h2 className="text-2xl font-bold">Your Services</h2>
                <p className="text-muted-foreground">
                    Add the services you offer. You can always add more later.
                </p>
            </div>

            <div className="space-y-4">
                {data.services.length === 0 ? (
                    <div className="glass rounded-2xl p-8 text-center space-y-4">
                        <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
                            <Scissors className="w-8 h-8 text-primary" />
                        </div>
                        <div>
                            <h3 className="font-semibold mb-1">No services yet</h3>
                            <p className="text-sm text-muted-foreground">
                                Click the button below to add your first service
                            </p>
                        </div>
                    </div>
                ) : (
                    data.services.map((service, index) => (
                        <div key={index} className="glass rounded-2xl p-6 space-y-4">
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold">Service {index + 1}</h3>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => removeService(index)}
                                    className="text-red-500 hover:text-red-700"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </Button>
                            </div>

                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor={`service-name-${index}`}>Service Name *</Label>
                                    <Input
                                        id={`service-name-${index}`}
                                        placeholder="e.g., Haircut, Beard Trim, Hot Towel Shave"
                                        value={service.name}
                                        onChange={(e) => updateService(index, "name", e.target.value)}
                                        required
                                    />
                                </div>

                                <div className="grid md:grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label htmlFor={`service-duration-${index}`}>Duration (minutes) *</Label>
                                        <Input
                                            id={`service-duration-${index}`}
                                            type="number"
                                            min="5"
                                            step="5"
                                            placeholder="30"
                                            value={service.duration_minutes}
                                            onChange={(e) =>
                                                updateService(index, "duration_minutes", parseInt(e.target.value) || 0)
                                            }
                                            required
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor={`service-price-${index}`}>Price ($) *</Label>
                                        <Input
                                            id={`service-price-${index}`}
                                            type="number"
                                            min="0"
                                            step="0.01"
                                            placeholder="25.00"
                                            value={service.price}
                                            onChange={(e) =>
                                                updateService(index, "price", parseFloat(e.target.value) || 0)
                                            }
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor={`service-description-${index}`}>Description (Optional)</Label>
                                    <Input
                                        id={`service-description-${index}`}
                                        placeholder="Brief description of the service"
                                        value={service.description}
                                        onChange={(e) => updateService(index, "description", e.target.value)}
                                    />
                                </div>
                            </div>
                        </div>
                    ))
                )}

                <Button onClick={addService} variant="outline" className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Service
                </Button>
            </div>

            {data.services.length > 0 && (
                <div className="glass rounded-xl p-4 border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/20">
                    <p className="text-sm text-green-700 dark:text-green-300">
                        ✓ {data.services.length} service{data.services.length !== 1 ? "s" : ""} added
                    </p>
                </div>
            )}
        </div>
    );
}
