import { Avatar, AvatarFallback } from "./ui/avatar";
import { Button } from "./ui/button";
import { UserPlus } from "lucide-react";

const agents = [
  {
    name: "Emma Wilson",
    task: "Handling Enterprise Client Call",
    status: "Active",
    statusColor: "bg-success",
    initials: "EW",
    avatar: "from-primary to-accent",
  },
  {
    name: "Michael Chen",
    task: "Resolving Technical Support Ticket",
    status: "On Break",
    statusColor: "bg-warning",
    initials: "MC",
    avatar: "from-success to-success/80",
  },
  {
    name: "Sofia Rodriguez",
    task: "Customer Onboarding Session",
    status: "Active",
    statusColor: "bg-success",
    initials: "SR",
    avatar: "from-accent to-primary",
  },
  {
    name: "James Anderson",
    task: "Feedback Collection and Analysis",
    status: "Idle",
    statusColor: "bg-muted",
    initials: "JA",
    avatar: "from-warning to-warning/80",
  },
];

export const AgentPerformance = () => {
  return (
    <div className="glass-card rounded-2xl p-6 shine">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Agent Performance</h3>
        <Button variant="outline" size="sm" className="gap-2">
          <UserPlus className="w-4 h-4" />
          Add Agent
        </Button>
      </div>

      <div className="space-y-4">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/40 transition-all hover:shadow-md"
          >
            <Avatar className="h-12 w-12">
              <AvatarFallback className={`bg-gradient-to-br ${agent.avatar} text-white font-semibold`}>
                {agent.initials}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h4 className="font-medium text-sm">{agent.name}</h4>
              <p className="text-xs text-muted-foreground">{agent.task}</p>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-medium ${agent.statusColor} ${
                agent.statusColor === "bg-muted" ? "text-foreground" : "text-white"
              }`}
            >
              {agent.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
