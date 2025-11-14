import { Plus } from "lucide-react";
import { Button } from "./ui/button";

const tickets = [
  {
    title: "API Integration Support",
    dueDate: "Due: Dec 28, 2024",
    icon: "⚡",
    color: "from-primary to-accent",
  },
  {
    title: "Account Verification Issue",
    dueDate: "Due: Dec 29, 2024",
    icon: "🔐",
    color: "from-accent to-accent/80",
  },
  {
    title: "Performance Optimization",
    dueDate: "Due: Dec 30, 2024",
    icon: "🎯",
    color: "from-success to-success/80",
  },
  {
    title: "UI/UX Feedback Review",
    dueDate: "Due: Jan 2, 2025",
    icon: "🎨",
    color: "from-warning to-warning/80",
  },
  {
    title: "Security Audit Request",
    dueDate: "Due: Jan 5, 2025",
    icon: "🛡️",
    color: "from-destructive to-destructive/80",
  },
];

export const TicketList = () => {
  return (
    <div className="glass-card rounded-2xl p-6 shine">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Active Tickets</h3>
        <Button variant="ghost" size="sm" className="gap-2">
          <Plus className="w-4 h-4" />
          New
        </Button>
      </div>

      <div className="space-y-3">
        {tickets.map((ticket, index) => (
          <div
            key={index}
            className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/40 transition-all cursor-pointer group hover:shadow-md"
          >
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${ticket.color} flex items-center justify-center text-xl`}>
              {ticket.icon}
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-sm group-hover:text-primary transition-colors">
                {ticket.title}
              </h4>
              <p className="text-xs text-muted-foreground">{ticket.dueDate}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
