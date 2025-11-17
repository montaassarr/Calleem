import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Save, ArrowLeft, RefreshCw, AlertCircle, CheckCircle, XCircle, Eye, EyeOff } from "lucide-react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useConfig } from "@/hooks/use-config";
import { Switch } from "@/components/ui/switch";

const IntegrationsSettings = () => {
  const navigate = useNavigate();
  const { config, isLoading, error, updateConfig, isUpdating, reloadConfig, isReloading } = useConfig();
  
  const [showKeys, setShowKeys] = useState({
    access_token: false,
    verify_token: false,
  });
  
  const [formData, setFormData] = useState({
    phone_number_id: "",
    access_token: "",
    verify_token: "",
    webhook_url: "",
    is_enabled: true,
  });

  useEffect(() => {
    if (config?.whatsapp_config) {
      setFormData({
        phone_number_id: config.whatsapp_config.phone_number_id || "",
        access_token: config.whatsapp_config.access_token || "",
        verify_token: config.whatsapp_config.verify_token || "",
        webhook_url: config.whatsapp_config.webhook_url || "",
        is_enabled: config.whatsapp_config.is_enabled ?? true,
      });
    }
  }, [config]);

  const handleSave = () => {
    updateConfig({
      whatsapp_config: formData
    });
  };

  const toggleKeyVisibility = (key: keyof typeof showKeys) => {
    setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
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
                <h1 className="text-3xl font-bold mb-2">WhatsApp Integration</h1>
                <p className="text-muted-foreground">
                  Configure WhatsApp Cloud API for customer messaging
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
            <Alert variant="destructive" className="mb-6 max-w-3xl">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Failed to load WhatsApp configuration. Please try again.
              </AlertDescription>
            </Alert>
          )}

          {/* WhatsApp Cloud API Configuration */}
          <div className="glass rounded-2xl p-6 max-w-3xl mb-6">
            {isLoading ? (
              <div className="space-y-6">
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold">WhatsApp Cloud API</h3>
                    <p className="text-sm text-muted-foreground">Connect your WhatsApp Business Account</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Switch
                      checked={formData.is_enabled}
                      onCheckedChange={(checked) => setFormData({ ...formData, is_enabled: checked })}
                    />
                    <span className="text-sm font-medium">
                      {formData.is_enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="phone_number_id">Phone Number ID *</Label>
                    <Input
                      id="phone_number_id"
                      value={formData.phone_number_id}
                      onChange={(e) => setFormData({ ...formData, phone_number_id: e.target.value })}
                      className="glass-strong mt-2"
                      placeholder="123456789012345"
                      disabled={isUpdating}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Find this in your Facebook Business Manager → WhatsApp → API Setup
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="access_token">Access Token *</Label>
                    <div className="relative mt-2">
                      <Input
                        id="access_token"
                        type={showKeys.access_token ? "text" : "password"}
                        value={formData.access_token}
                        onChange={(e) => setFormData({ ...formData, access_token: e.target.value })}
                        className="glass-strong pr-10"
                        placeholder="EAAxxxxxxxxxxxxx..."
                        disabled={isUpdating}
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        className="absolute right-0 top-0"
                        onClick={() => toggleKeyVisibility('access_token')}
                      >
                        {showKeys.access_token ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Generate a permanent access token from Meta Business Suite
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="verify_token">Webhook Verify Token</Label>
                    <div className="relative mt-2">
                      <Input
                        id="verify_token"
                        type={showKeys.verify_token ? "text" : "password"}
                        value={formData.verify_token}
                        onChange={(e) => setFormData({ ...formData, verify_token: e.target.value })}
                        className="glass-strong pr-10"
                        placeholder="your_custom_verify_token"
                        disabled={isUpdating}
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        className="absolute right-0 top-0"
                        onClick={() => toggleKeyVisibility('verify_token')}
                      >
                        {showKeys.verify_token ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Custom string to verify webhook requests from WhatsApp
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="webhook_url">Webhook URL</Label>
                    <Input
                      id="webhook_url"
                      value={formData.webhook_url}
                      onChange={(e) => setFormData({ ...formData, webhook_url: e.target.value })}
                      className="glass-strong mt-2"
                      placeholder="https://your-domain.com/api/v1/webhook/sms"
                      disabled={isUpdating}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Configure this URL in your WhatsApp webhook settings
                    </p>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <p className="text-sm text-blue-600 dark:text-blue-400">
                    <strong>Setup Guide:</strong> Follow the{' '}
                    <a 
                      href="https://developers.facebook.com/docs/whatsapp/cloud-api/get-started" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="underline hover:no-underline"
                    >
                      WhatsApp Cloud API documentation
                    </a>
                    {' '}to create a business account and get your credentials.
                  </p>
                </div>
              </>
            )}
          </div>

          {/* Save Button */}
          <div className="max-w-3xl">
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
                    Save WhatsApp Configuration
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

          {/* Warning */}
          <div className="glass rounded-lg p-4 max-w-3xl mt-6 border border-yellow-500/20">
            <p className="text-sm text-yellow-600 dark:text-yellow-400">
              ⚠️ <strong>Security Note:</strong> Access tokens are sensitive credentials. Never share them publicly or commit them to version control.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default IntegrationsSettings;
