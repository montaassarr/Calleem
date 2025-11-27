import { Phone, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";

export const RecentActivities = () => {
    return (
        <div className="glass-card rounded-2xl p-6 shine">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>

            <div className="bg-gradient-to-br from-primary/20 to-accent/20 backdrop-blur-xl rounded-xl p-4 mb-4 border border-primary/30 shadow-lg shine">
                <div className="flex items-start justify-between mb-3">
                    <div>
                        <h4 className="font-semibold text-foreground mb-1">Priority Support Call</h4>
                        <p className="text-sm text-muted-foreground">Enterprise client escalation</p>
                    </div>
                    <Phone className="w-5 h-5 text-primary" />
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                    <Clock className="w-4 h-4" />
                    <span>Starting in 15 minutes</span>
                </div>
                <Button className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90">
                    Join Call
                </Button>
            </div>

            <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 rounded-full bg-success" />
                    <span className="text-muted-foreground">Ticket #2847 resolved</span>
                    <span className="ml-auto text-xs text-muted-foreground">2m ago</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 rounded-full bg-warning" />
                    <span className="text-muted-foreground">New escalation assigned</span>
                    <span className="ml-auto text-xs text-muted-foreground">5m ago</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 rounded-full bg-accent" />
                    <span className="text-muted-foreground">Call with Tech Corp ended</span>
                    <span className="ml-auto text-xs text-muted-foreground">12m ago</span>
                </div>
            </div>
        </div>
    );
};
