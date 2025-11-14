import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { StatCard } from "@/components/StatCard";
import { RecentActivities } from "@/components/RecentActivities";
import { LiveCallStatus } from "@/components/LiveCallStatus";
import { Phone, CheckCircle2, Clock, TrendingUp, Plus, Upload, Calendar, MessageSquare, Scissors } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import { appointmentsApi, conversationsApi, servicesApi, webhookApi } from "@/api";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();

  // Fetch appointments
  const { data: appointments = [], isLoading: appointmentsLoading } = useQuery({
    queryKey: ["appointments"],
    queryFn: () => appointmentsApi.list(),
  });

  // Fetch conversations
  const { data: conversations = [], isLoading: conversationsLoading } = useQuery({
    queryKey: ["conversations"],
    queryFn: () => conversationsApi.list({ limit: 100 }),
  });

  // Fetch services
  const { data: services = [], isLoading: servicesLoading } = useQuery({
    queryKey: ["services"],
    queryFn: () => servicesApi.list({ active_only: false }),
  });

  // Fetch webhook status
  const { data: webhookStatus } = useQuery({
    queryKey: ["webhook-status"],
    queryFn: () => webhookApi.getStatus(),
  });

  const now = new Date();
  const upcomingAppointments = appointments.filter(
    (apt: any) => new Date(apt.datetime) > now && apt.status === 'confirmed'
  ).length;
  
  const completedToday = appointments.filter((apt: any) => {
    const aptDate = new Date(apt.datetime);
    return aptDate.toDateString() === now.toDateString() && apt.status === 'completed';
  }).length;
  
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
              <Button 
                className="gap-2 bg-gradient-to-r from-primary to-accent hover:opacity-90"
                onClick={() => navigate('/appointments/new')}
              >
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
              value={appointmentsLoading ? "..." : appointments.length.toString()}
              icon={Calendar}
              trend={{ value: "All time bookings", isPositive: true }}
              variant="primary"
            />
            <StatCard
              title="Upcoming"
              value={appointmentsLoading ? "..." : upcomingAppointments.toString()}
              icon={CheckCircle2}
              trend={{ value: "Scheduled ahead", isPositive: true }}
            />
            <StatCard
              title="Conversations"
              value={conversationsLoading ? "..." : conversations.length.toString()}
              icon={MessageSquare}
              trend={{ value: `${completedToday} completed today`, isPositive: true }}
            />
            <StatCard
              title="Active Services"
              value={servicesLoading ? "..." : activeServices.toString()}
              icon={Scissors}
              status="On menu"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <div className="lg:col-span-2 glass rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Appointments</h3>
              {appointmentsLoading ? (
                <p className="text-muted-foreground">Loading...</p>
              ) : appointments.length === 0 ? (
                <p className="text-muted-foreground">No appointments yet</p>
              ) : (
                <div className="space-y-3">
                  {appointments.slice(0, 5).map((apt: any) => (
                    <div key={apt.id} className="flex items-center justify-between p-3 glass-strong rounded-lg">
                      <div>
                        <p className="font-medium">{apt.client_name}</p>
                        <p className="text-sm text-muted-foreground">{apt.service}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm">{new Date(apt.datetime).toLocaleDateString()}</p>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          apt.status === 'confirmed' ? 'bg-green-100 text-green-700' :
                          apt.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                          apt.status === 'cancelled' ? 'bg-red-100 text-red-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {apt.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <RecentActivities />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-4">AI Receptionist Status</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Webhook Status</span>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    webhookStatus?.status === 'active' 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {webhookStatus?.status || 'Unknown'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Conversations Handled</span>
                  <span className="font-semibold">{conversations.length}</span>
                </div>
                <Button 
                  className="w-full gap-2"
                  onClick={() => navigate('/ai-receptionist/test')}
                >
                  <Phone className="w-4 h-4" />
                  Test AI Chat
                </Button>
              </div>
            </div>
            <LiveCallStatus />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
