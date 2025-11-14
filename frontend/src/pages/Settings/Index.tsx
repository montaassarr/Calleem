import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Building, Users, Bot, Key, Clock } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";

const Settings = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const sections = [
    {
      title: "Business Profile",
      description: "Manage your business information and hours",
      icon: Building,
      path: "/settings/business",
      color: "from-blue-500 to-cyan-500",
    },
    {
      title: "Team Members",
      description: "Add and manage dashboard users",
      icon: Users,
      path: "/settings/team",
      color: "from-purple-500 to-pink-500",
    },
    {
      title: "AI Configuration",
      description: "Configure AI behavior and prompts",
      icon: Bot,
      path: "/settings/ai",
      color: "from-green-500 to-emerald-500",
    },
    {
      title: "Integrations",
      description: "API keys and third-party services",
      icon: Key,
      path: "/settings/integrations",
      color: "from-orange-500 to-red-500",
    },
  ];

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold mb-2">Settings</h1>
            <p className="text-muted-foreground">
              Configure your AI receptionist and business settings
            </p>
          </div>

          {/* Settings Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {sections.map((section) => (
              <div
                key={section.path}
                onClick={() => navigate(section.path)}
                className="glass rounded-2xl p-6 hover:shadow-lg transition-all cursor-pointer group"
              >
                <div className="flex items-start gap-4">
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${section.color} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                    <section.icon className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold mb-1">{section.title}</h3>
                    <p className="text-sm text-muted-foreground">{section.description}</p>
                  </div>
                  <div className="text-muted-foreground group-hover:translate-x-1 transition-transform">
                    →
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Info */}
          <div className="mt-6 glass rounded-2xl p-6">
            <h3 className="text-lg font-semibold mb-4">System Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Version</p>
                <p className="font-semibold">1.0.0</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Last Updated</p>
                <p className="font-semibold">{new Date().toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Environment</p>
                <p className="font-semibold">Development</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Settings;
