import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Save, ArrowLeft } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const BusinessSettings = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [settings, setSettings] = useState({
    business_name: "Royal Fade Barbershop",
    business_phone: "+1234567890",
    business_email: "info@royalfade.com",
    business_address: "123 Main St, City, State 12345",
    business_hours: "Monday-Saturday 9:00 AM - 8:00 PM",
    timezone: "America/New_York",
    available_services: "Haircut,Beard Trim,Fade,Hot Shave,Hair & Beard Combo",
  });

  const handleSave = () => {
    // TODO: Save to backend
    toast({
      title: "Settings Saved",
      description: "Business settings have been updated successfully",
    });
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center gap-4 mb-6">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/settings')}
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold mb-2">Business Profile</h1>
              <p className="text-muted-foreground">
                Manage your business information and operating hours
              </p>
            </div>
          </div>

          {/* Form */}
          <div className="glass rounded-2xl p-6 max-w-3xl">
            <div className="space-y-6">
              <div>
                <Label htmlFor="business_name">Business Name</Label>
                <Input
                  id="business_name"
                  value={settings.business_name}
                  onChange={(e) => setSettings({ ...settings, business_name: e.target.value })}
                  className="glass-strong mt-2"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="business_phone">Phone Number</Label>
                  <Input
                    id="business_phone"
                    value={settings.business_phone}
                    onChange={(e) => setSettings({ ...settings, business_phone: e.target.value })}
                    className="glass-strong mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="business_email">Email</Label>
                  <Input
                    id="business_email"
                    type="email"
                    value={settings.business_email}
                    onChange={(e) => setSettings({ ...settings, business_email: e.target.value })}
                    className="glass-strong mt-2"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="business_address">Address</Label>
                <Textarea
                  id="business_address"
                  value={settings.business_address}
                  onChange={(e) => setSettings({ ...settings, business_address: e.target.value })}
                  className="glass-strong mt-2"
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="business_hours">Business Hours</Label>
                <Input
                  id="business_hours"
                  value={settings.business_hours}
                  onChange={(e) => setSettings({ ...settings, business_hours: e.target.value })}
                  className="glass-strong mt-2"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Example: Monday-Friday 9:00 AM - 6:00 PM
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="timezone">Timezone</Label>
                  <Input
                    id="timezone"
                    value={settings.timezone}
                    onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                    className="glass-strong mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="available_services">Available Services</Label>
                  <Input
                    id="available_services"
                    value={settings.available_services}
                    onChange={(e) => setSettings({ ...settings, available_services: e.target.value })}
                    className="glass-strong mt-2"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Comma-separated list
                  </p>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <Button 
                  className="gap-2 bg-gradient-to-r from-primary to-accent"
                  onClick={handleSave}
                >
                  <Save className="w-4 h-4" />
                  Save Changes
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => navigate('/settings')}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default BusinessSettings;
