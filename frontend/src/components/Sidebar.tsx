import { LayoutDashboard, Phone, Calendar, BarChart3, Users, Settings, HelpCircle, LogOut, Scissors, MessageSquare, Bot, Smartphone } from "lucide-react";
import { cn } from "@/lib/utils";
import { NavLink } from "./NavLink";
import { useNavigate } from "react-router-dom";

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/" },
  { icon: Bot, label: "AI Receptionist", path: "/ai-receptionist" },
  { icon: Calendar, label: "Appointments", path: "/appointments" },
  { icon: MessageSquare, label: "Conversations", path: "/conversations" },
  { icon: Scissors, label: "Services", path: "/services" },
  { icon: Smartphone, label: "WhatsApp", path: "/whatsapp" },
];

const generalItems = [
  { icon: Settings, label: "Settings", path: "/settings" },
  { icon: HelpCircle, label: "Help", path: "/help" },
];

export const Sidebar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    navigate("/login");
  };

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 glass-strong flex flex-col z-50">
      <div className="p-6">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Scissors className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Royal Fade
          </span>
        </div>
      </div>

      <nav className="flex-1 px-3">
        <div className="mb-6">
          <p className="px-3 text-xs font-semibold text-muted-foreground mb-2">MENU</p>
          <div className="space-y-1">
            {menuItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all hover:bg-white/50 hover:shadow-md group"
                activeClassName="bg-gradient-to-r from-primary to-accent text-white shadow-lg shadow-primary/30"
              >
                <item.icon className="w-5 h-5" />
                <span className="flex-1">{item.label}</span>
              </NavLink>
            ))}
          </div>
        </div>

        <div>
          <p className="px-3 text-xs font-semibold text-muted-foreground mb-2">GENERAL</p>
          <div className="space-y-1">
            {generalItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all hover:bg-white/50 hover:shadow-md"
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            ))}
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all hover:bg-white/50 hover:shadow-md w-full text-left"
            >
              <LogOut className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </nav>

      <div className="p-4 m-4 bg-gradient-to-br from-primary via-accent to-primary/90 rounded-2xl text-white shadow-xl shadow-primary/20 shine">
        <div className="flex items-center gap-2 mb-2">
          <Phone className="w-5 h-5" />
          <p className="font-semibold text-sm">AI Receptionist</p>
        </div>
        <p className="text-xs text-white/90 mb-4">Ava is taking calls 24/7</p>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-300 rounded-full animate-pulse" />
          <span className="text-xs">Active</span>
        </div>
      </div>
    </aside>
  );
};
