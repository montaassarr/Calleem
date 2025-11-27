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
import { useOnboarding } from "@/contexts/OnboardingContext";

const timezones = [
    { value: "America/New_York", label: "Eastern Time (ET)" },
    { value: "America/Chicago", label: "Central Time (CT)" },
    { value: "America/Denver", label: "Mountain Time (MT)" },
    { value: "America/Los_Angeles", label: "Pacific Time (PT)" },
    { value: "America/Phoenix", label: "Arizona (MST)" },
    { value: "America/Anchorage", label: "Alaska Time (AKT)" },
    { value: "Pacific/Honolulu", label: "Hawaii Time (HST)" },
    { value: "UTC", label: "UTC" },
];

export function BusinessDetailsStep() {
    const { data, updateData } = useOnboarding();

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="space-y-2">
                <h2 className="text-2xl font-bold">Business Details</h2>
                <p className="text-muted-foreground">
                    Tell us about your business so we can personalize your experience
                </p>
            </div>

            <div className="glass rounded-2xl p-6 space-y-6">
                <div className="space-y-2">
                    <Label htmlFor="businessName">Business Name *</Label>
                    <Input
                        id="businessName"
                        placeholder="e.g., Royal Fade Barbershop"
                        value={data.businessName}
                        onChange={(e) => updateData({ businessName: e.target.value })}
                        required
                    />
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <Label htmlFor="phone">Phone Number *</Label>
                        <Input
                            id="phone"
                            type="tel"
                            placeholder="+1 (555) 123-4567"
                            value={data.phone}
                            onChange={(e) => updateData({ phone: e.target.value })}
                            required
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="email">Email Address *</Label>
                        <Input
                            id="email"
                            type="email"
                            placeholder="contact@business.com"
                            value={data.email}
                            onChange={(e) => updateData({ email: e.target.value })}
                            required
                        />
                    </div>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="address">Business Address</Label>
                    <Textarea
                        id="address"
                        placeholder="123 Main St, City, State ZIP"
                        value={data.address}
                        onChange={(e) => updateData({ address: e.target.value })}
                        rows={3}
                    />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="timezone">Timezone *</Label>
                    <Select
                        value={data.timezone}
                        onValueChange={(value) => updateData({ timezone: value })}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select your timezone" />
                        </SelectTrigger>
                        <SelectContent>
                            {timezones.map((tz) => (
                                <SelectItem key={tz.value} value={tz.value}>
                                    {tz.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <p className="text-xs text-muted-foreground">
                        This helps us schedule appointments in your local time
                    </p>
                </div>
            </div>
        </div>
    );
}
