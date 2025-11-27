"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    Save,
    ArrowLeft,
    RefreshCw,
    AlertCircle,
    Clock
} from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useConfig } from "@/hooks/use-config";
import { Switch } from "@/components/ui/switch";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { toast } from "sonner";

interface DayHours {
    day_of_week: number;
    open_time: string;
    close_time: string;
    is_open: boolean;
}

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
const DAY_LABELS: Record<string, string> = {
    monday: 'Monday',
    tuesday: 'Tuesday',
    wednesday: 'Wednesday',
    thursday: 'Thursday',
    friday: 'Friday',
    saturday: 'Saturday',
    sunday: 'Sunday',
};

export default function HoursSettingsPage() {
    const router = useRouter();
    const { config, isLoading, error, updateConfig, isUpdating, reloadConfig, isReloading } = useConfig();

    const [hours, setHours] = useState<DayHours[]>(
        DAYS.map((day, index) => ({ day_of_week: index, open_time: '09:00', close_time: '18:00', is_open: true }))
    );

    useEffect(() => {
        if (config?.opening_hours && config.opening_hours.length > 0) {
            setHours(config.opening_hours.map(h => ({
                day_of_week: h.day_of_week,
                open_time: h.open_time,
                close_time: h.close_time,
                is_open: h.is_open
            })));
        }
    }, [config]);

    const handleSave = () => {
        updateConfig({
            opening_hours: hours
        }, {
            onSuccess: () => toast.success("Business hours updated successfully"),
            onError: () => toast.error("Failed to update business hours"),
        });
    };

    const updateDay = (dayOfWeek: number, field: keyof DayHours, value: any) => {
        setHours(hours.map(h =>
            h.day_of_week === dayOfWeek ? { ...h, [field]: value } : h
        ));
    };

    const copyToAll = (sourceDayOfWeek: number) => {
        const source = hours.find(h => h.day_of_week === sourceDayOfWeek);
        if (source) {
            setHours(hours.map(h => ({
                ...h,
                open_time: source.open_time,
                close_time: source.close_time,
                is_open: source.is_open,
            })));
        }
    };

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => router.push('/dashboard/settings')}
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold mb-2">Business Hours</h1>
                        <p className="text-muted-foreground">
                            Set your operating hours for each day of the week
                        </p>
                    </div>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => reloadConfig()}
                    disabled={isReloading}
                    className="gap-2"
                >
                    <RefreshCw className={`w-4 h-4 ${isReloading ? 'animate-spin' : ''}`} />
                    Reload
                </Button>
            </div>

            {/* Error Alert */}
            {error && (
                <Alert variant="destructive" className="mb-6 max-w-4xl">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        Failed to load business hours configuration. Please try again.
                    </AlertDescription>
                </Alert>
            )}

            {/* Hours Configuration */}
            <div className="max-w-4xl space-y-3 mb-6">
                {isLoading ? (
                    <>
                        {DAYS.map(day => (
                            <Skeleton key={day} className="h-24 w-full" />
                        ))}
                    </>
                ) : (
                    <>
                        {hours.map((dayHours, index) => (
                            <Card key={dayHours.day_of_week} className="glass">
                                <CardHeader className="pb-3">
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="text-lg flex items-center gap-2">
                                            <Clock className="w-5 h-5" />
                                            {DAY_LABELS[DAYS[index]]}
                                        </CardTitle>
                                        <div className="flex items-center gap-4">
                                            <div className="flex items-center gap-2">
                                                <Switch
                                                    checked={dayHours.is_open}
                                                    onCheckedChange={(checked) => updateDay(dayHours.day_of_week, 'is_open', checked)}
                                                    disabled={isUpdating}
                                                />
                                                <span className="text-sm text-muted-foreground min-w-[60px]">
                                                    {dayHours.is_open ? 'Open' : 'Closed'}
                                                </span>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => copyToAll(dayHours.day_of_week)}
                                                disabled={isUpdating}
                                                className="text-xs"
                                            >
                                                Copy to All
                                            </Button>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    {dayHours.is_open && (
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <Label className="text-xs text-muted-foreground">Opening Time</Label>
                                                <Input
                                                    type="time"
                                                    value={dayHours.open_time}
                                                    onChange={(e) => updateDay(dayHours.day_of_week, 'open_time', e.target.value)}
                                                    className="glass-strong mt-1"
                                                    disabled={isUpdating}
                                                />
                                            </div>
                                            <div>
                                                <Label className="text-xs text-muted-foreground">Closing Time</Label>
                                                <Input
                                                    type="time"
                                                    value={dayHours.close_time}
                                                    onChange={(e) => updateDay(dayHours.day_of_week, 'close_time', e.target.value)}
                                                    className="glass-strong mt-1"
                                                    disabled={isUpdating}
                                                />
                                            </div>
                                        </div>
                                    )}
                                    {!dayHours.is_open && (
                                        <p className="text-sm text-muted-foreground italic">
                                            Business is closed on this day
                                        </p>
                                    )}
                                </CardContent>
                            </Card>
                        ))}
                    </>
                )}
            </div>

            {/* Quick Actions */}
            <Card className="glass max-w-4xl mb-6">
                <CardHeader>
                    <CardTitle className="text-base">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="flex gap-2 flex-wrap">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                            setHours(hours.map(h => ({ ...h, open_time: '09:00', close_time: '17:00', is_open: true })));
                        }}
                        disabled={isUpdating}
                    >
                        Standard Hours (9 AM - 5 PM)
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                            setHours(hours.map(h => ({ ...h, open_time: '08:00', close_time: '20:00', is_open: true })));
                        }}
                        disabled={isUpdating}
                    >
                        Extended Hours (8 AM - 8 PM)
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                            setHours(hours.map((h) => ({
                                ...h,
                                is_open: h.day_of_week < 5 // Monday-Friday
                            })));
                        }}
                        disabled={isUpdating}
                    >
                        Weekdays Only
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                            setHours(hours.map(h => ({ ...h, is_open: true })));
                        }}
                        disabled={isUpdating}
                    >
                        Open All Week
                    </Button>
                </CardContent>
            </Card>

            {/* Save Button */}
            <div className="max-w-4xl">
                <div className="flex gap-3">
                    <Button
                        className="gap-2 bg-gradient-to-r from-primary to-accent"
                        onClick={handleSave}
                        disabled={isUpdating || isLoading}
                    >
                        {isUpdating ? (
                            <>
                                <RefreshCw className="w-4 h-4 animate-spin" />
                                Saving...
                            </>
                        ) : (
                            <>
                                <Save className="w-4 h-4" />
                                Save Business Hours
                            </>
                        )}
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => router.push('/dashboard/settings')}
                        disabled={isUpdating}
                    >
                        Cancel
                    </Button>
                </div>
            </div>

            {/* Info */}
            <div className="glass rounded-lg p-4 max-w-4xl mt-6 border border-blue-500/20">
                <p className="text-sm text-blue-600 dark:text-blue-400">
                    💡 <strong>Tip:</strong> The AI receptionist will use these hours to inform customers about availability and prevent bookings outside business hours. Use &quot;Copy to All&quot; to quickly apply one day&apos;s schedule to the entire week.
                </p>
            </div>
        </div>
    );
}
