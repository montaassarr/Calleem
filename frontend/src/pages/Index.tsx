import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { StatCard } from "@/components/StatCard";
import { CallAnalytics } from "@/components/CallAnalytics";
import { AgentPerformance } from "@/components/AgentPerformance";
import { RecentActivities } from "@/components/RecentActivities";
import { SupportProgress } from "@/components/SupportProgress";
import { TicketList } from "@/components/TicketList";
import { LiveCallStatus } from "@/components/LiveCallStatus";
import { Phone, CheckCircle2, Clock, TrendingUp, Plus, Upload, Calendar, MessageSquare, Scissors } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

const Index = () => {
  // Fetch appointments
  const { data: appointments = [] } = useQuery({
    queryKey: ["appointments"],
    queryFn: async () => {
      const response = await api.get("/appointments");
      return response.data;
    },
  });

  // Fetch conversations
  const { data: conversations = [] } = useQuery({
    queryKey: ["conversations"],
    queryFn: async () => {
      const response = await api.get("/conversations");
      return response.data;
    },
  });

  // Fetch services
  const { data: services = [] } = useQuery({
    queryKey: ["services"],
    queryFn: async () => {
      const response = await api.get("/services");
      return response.data;
    },
  });

  const now = new Date();
  const upcomingAppointments = appointments.filter(
    (apt: any) => new Date(apt.datetime) > now
  ).length;
  const completedConversations = conversations.filter(
    (conv: any) => conv.status === "completed"
  ).length;
  const activeServices = services.filter((s: any) => s.active !== false).length;

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 ml-64">
        <DashboardHeader />
        
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">Royal Fade Dashboard</h1>
              <p className="text-muted-foreground">Monitor your AI receptionist and business operations.</p>
            </div>
            <div className="flex gap-3">
              <Button className="gap-2 bg-gradient-to-r from-primary to-accent hover:opacity-90">
                <Plus className="w-4 h-4" />
                New Appointment
              </Button>
              <Button variant="outline" className="gap-2">
                <Upload className="w-4 h-4" />
                Export Data
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <StatCard
              title="Total Appointments"
              value={appointments.length.toString()}
              icon={Calendar}
              trend={{ value: "All time bookings", isPositive: true }}
              variant="primary"
            />
            <StatCard
              title="Upcoming"
              value={upcomingAppointments.toString()}
              icon={CheckCircle2}
              trend={{ value: "Scheduled ahead", isPositive: true }}
            />
            <StatCard
              title="Conversations"
              value={conversations.length.toString()}
              icon={MessageSquare}
              trend={{ value: `${completedConversations} completed`, isPositive: true }}
            />
            <StatCard
              title="Active Services"
              value={activeServices.toString()}
              icon={Scissors}
              status="On menu"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <div className="lg:col-span-2">
              <CallAnalytics />
            </div>
            <RecentActivities />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <AgentPerformance />
            <SupportProgress />
            <div className="space-y-6">
              <TicketList />
              <LiveCallStatus />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
