import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { useOnboarding } from "@/contexts/OnboardingContext";

const days = [
    { key: "monday", label: "Monday" },
    { key: "tuesday", label: "Tuesday" },
    { key: "wednesday", label: "Wednesday" },
    { key: "thursday", label: "Thursday" },
    { key: "friday", label: "Friday" },
    { key: "saturday", label: "Saturday" },
    { key: "sunday", label: "Sunday" },
];

export function BusinessHoursStep() {
    const { data, updateData } = useOnboarding();

    const updateHours = (day: string, field: string, value: any) => {
        updateData({
            businessHours: {
                ...data.businessHours,
                [day]: {
                    ...data.businessHours[day],
                    [field]: value,
                },
            },
        });
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="space-y-2">
                <h2 className="text-2xl font-bold">Business Hours</h2>
                <p className="text-muted-foreground">
                    Set your operating hours for each day of the week
                </p>
            </div>

            <div className="glass rounded-2xl p-6 space-y-4">
                {days.map((day) => {
                    const hours = data.businessHours[day.key];
                    return (
                        <div
                            key={day.key}
                            className={`p-4 rounded-lg border transition-all ${hours.enabled
                                    ? "border-primary/20 bg-primary/5"
                                    : "border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50"
                                }`}
                        >
                            <div className="flex items-center justify-between mb-3">
                                <Label htmlFor={`${day.key}-enabled`} className="text-base font-semibold">
                                    {day.label}
                                </Label>
                                <Switch
                                    id={`${day.key}-enabled`}
                                    checked={hours.enabled}
                                    onCheckedChange={(checked) => updateHours(day.key, "enabled", checked)}
                                />
                            </div>

                            {hours.enabled && (
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label htmlFor={`${day.key}-open`} className="text-sm text-muted-foreground">
                                            Opening Time
                                        </Label>
                                        <Input
                                            id={`${day.key}-open`}
                                            type="time"
                                            value={hours.open}
                                            onChange={(e) => updateHours(day.key, "open", e.target.value)}
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor={`${day.key}-close`} className="text-sm text-muted-foreground">
                                            Closing Time
                                        </Label>
                                        <Input
                                            id={`${day.key}-close`}
                                            type="time"
                                            value={hours.close}
                                            onChange={(e) => updateHours(day.key, "close", e.target.value)}
                                        />
                                    </div>
                                </div>
                            )}

                            {!hours.enabled && (
                                <p className="text-sm text-muted-foreground">Closed</p>
                            )}
                        </div>
                    );
                })}
            </div>

            <div className="glass rounded-xl p-4 border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/20">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                    💡 Tip: You can update these hours anytime from Settings → Business Hours
                </p>
            </div>
        </div>
    );
}
