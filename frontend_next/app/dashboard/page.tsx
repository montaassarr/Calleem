"use client";

import { StatCard } from "@/components/dashboard/widgets/StatCard";
import { RecentActivities } from "@/components/dashboard/widgets/RecentActivities";
import { LiveCallStatus } from "@/components/dashboard/widgets/LiveCallStatus";
import { Phone, CheckCircle2, Calendar, MessageSquare, Scissors, Plus, Upload, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useTenant } from "@/contexts/TenantContext";
import { useDashboardStats } from "@/hooks/domain/useDashboardStats";

export default function DashboardPage() {
    const { config } = useTenant();
    const router = useRouter();
    const { data, isLoading } = useDashboardStats();

    const {
        appointments = [],
        conversations = [],
        metrics = {
            totalAppointments: 0,
            upcomingAppointments: 0,
            completedToday: 0,
            activeServices: 0
        },
        webhookStatus
    } = data || {};

    return (
        <div className="p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">{config?.business_name || 'Donezo'} Dashboard</h1>
                    <p className="text-muted-foreground">Monitor your AI receptionist and business operations.</p>
                </div>
                <div className="flex gap-3">
                    <Button
                        className="gap-2 bg-gradient-to-r from-primary to-accent hover:opacity-90"
                        onClick={() => router.push('/dashboard/appointments/new')}
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
                    title="Revenue"
                    value="$12,450"
                    icon={DollarSign}
                    trend={{ value: "+12% from last month", isPositive: true }}
                    variant="primary"
                />
                <StatCard
                    title="Total Appointments"
                    value={isLoading ? "..." : metrics.totalAppointments.toString()}
                    icon={Calendar}
                    trend={{ value: "All time bookings", isPositive: true }}
                    variant="primary"
                />
                <StatCard
                    title="Upcoming"
                    value={isLoading ? "..." : metrics.upcomingAppointments.toString()}
                    icon={CheckCircle2}
                    trend={{ value: "Scheduled ahead", isPositive: true }}
                    variant="primary"
                />
                <StatCard
                    title="Conversations"
                    value={isLoading ? "..." : (conversations.length || 0).toString()}
                    icon={MessageSquare}
                    trend={{ value: `${metrics.completedToday} completed today`, isPositive: true }}
                    variant="primary"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="lg:col-span-2 bg-white border border-slate-200 shadow-sm rounded-2xl p-6">
                    <h3 className="text-lg font-semibold mb-4">Recent Appointments</h3>
                    {isLoading ? (
                        <p className="text-muted-foreground">Loading...</p>
                    ) : appointments.length === 0 ? (
                        <p className="text-muted-foreground">No appointments yet</p>
                    ) : (
                        <div className="space-y-3">
                            {appointments.slice(0, 5).map((apt: any) => (
                                <div key={apt.id} className="flex items-center justify-between p-3 bg-white border border-slate-200 shadow-sm rounded-lg">
                                    <div>
                                        <p className="font-medium">{apt.client_name}</p>
                                        <p className="text-sm text-muted-foreground">{apt.service}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm">{new Date(apt.datetime).toLocaleDateString()}</p>
                                        <span className={`text-xs px-2 py-1 rounded-full ${apt.status === 'confirmed' ? 'bg-green-100 text-green-700' :
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
                <div className="bg-white border border-slate-200 shadow-sm rounded-2xl p-6">
                    <h3 className="text-lg font-semibold mb-4">AI Receptionist Status</h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-muted-foreground">Webhook Status</span>
                            <span className={`px-3 py-1 rounded-full text-sm ${webhookStatus?.status === 'active'
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
                            onClick={() => router.push('/dashboard/voice-agent/test')}
                        >
                            <Phone className="w-4 h-4" />
                            Test AI Chat
                        </Button>
                    </div>
                </div>
                <LiveCallStatus />
            </div>
        </div >
    );
};
