import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Save, ArrowLeft, RefreshCw, AlertCircle } from "lucide-react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useConfig } from "@/hooks/use-config";
import { Alert, AlertDescription } from "@/components/ui/alert";

const BusinessSettings = () => {
  const navigate = useNavigate();
  const { config, isLoading, error, updateConfig, isUpdating, reloadConfig, isReloading } = useConfig();
  
  const [formData, setFormData] = useState({
    business_name: "",
    business_phone: "",
    business_email: "",
    business_address: "",
    timezone: "America/New_York",
  });

  // Load config data into form
  useEffect(() => {
    if (config) {
      setFormData({
        business_name: config.business_name || "",
        business_phone: config.business_phone || "",
        business_email: config.business_email || "",
        business_address: config.business_address || "",
        timezone: config.timezone || "America/New_York",
      });
    }
  }, [config]);

  const handleSave = () => {
    updateConfig(formData);
  };

  const handleReload = () => {
    reloadConfig();
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
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
            <Button
              variant="outline"
              size="sm"
              onClick={handleReload}
              disabled={isReloading}
              className="gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${isReloading ? 'animate-spin' : ''}`} />
              Reload
            </Button>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Failed to load configuration. Please try again.
              </AlertDescription>
            </Alert>
          )}

          {/* Form */}
          <div className="glass rounded-2xl p-6 max-w-3xl">
            {isLoading ? (
              <div className="space-y-6">
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-20 w-full" />
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <Label htmlFor="business_name">Business Name *</Label>
                  <Input
                    id="business_name"
                    value={formData.business_name}
                    onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                    className="glass-strong mt-2"
                    placeholder="Enter your business name"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="business_phone">Phone Number</Label>
                    <Input
                      id="business_phone"
                      value={formData.business_phone}
                      onChange={(e) => setFormData({ ...formData, business_phone: e.target.value })}
                      className="glass-strong mt-2"
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>
                  <div>
                    <Label htmlFor="business_email">Email</Label>
                    <Input
                      id="business_email"
                      type="email"
                      value={formData.business_email}
                      onChange={(e) => setFormData({ ...formData, business_email: e.target.value })}
                      className="glass-strong mt-2"
                      placeholder="contact@business.com"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="business_address">Address</Label>
                  <Textarea
                    id="business_address"
                    value={formData.business_address}
                    onChange={(e) => setFormData({ ...formData, business_address: e.target.value })}
                    className="glass-strong mt-2"
                    rows={3}
                    placeholder="123 Main St, City, State 12345"
                  />
                </div>

                <div>
                  <Label htmlFor="timezone">Timezone *</Label>
                  <Input
                    id="timezone"
                    value={formData.timezone}
                    onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                    className="glass-strong mt-2"
                    placeholder="America/New_York"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Use IANA timezone format (e.g., America/New_York, Europe/London)
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button 
                    className="gap-2 bg-gradient-to-r from-primary to-accent"
                    onClick={handleSave}
                    disabled={isUpdating || !formData.business_name}
                  >
                    {isUpdating ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        Save Changes
                      </>
                    )}
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => navigate('/settings')}
                    disabled={isUpdating}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default BusinessSettings;
