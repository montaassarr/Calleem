"use client";

import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { appointmentsApi } from "@/lib/api-endpoints";
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import type { CalendarEvent, AppointmentResponse } from "@/lib/types";
import AppointmentFormModal from "@/components/dashboard/appointments/AppointmentFormModal";

export default function SchedulePage() {
    const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<"create" | "edit">("create");
    const [selectedAppointment, setSelectedAppointment] = useState<AppointmentResponse | null>(null);
    const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);

    const { data: appointments = [] } = useQuery({
        queryKey: ["appointments"],
        queryFn: () => appointmentsApi.list(),
    });

    // Convert appointments to calendar events
    useEffect(() => {
        const events: CalendarEvent[] = appointments.map((apt: any) => {
            const start = new Date(apt.datetime);
            const end = new Date(start.getTime() + apt.duration_minutes * 60000);

            const colors: Record<string, { bg: string; border: string }> = {
                confirmed: { bg: '#10b981', border: '#059669' },
                completed: { bg: '#3b82f6', border: '#2563eb' },
                cancelled: { bg: '#ef4444', border: '#dc2626' },
                no_show: { bg: '#6b7280', border: '#4b5563' },
            };

            const color = colors[apt.status] || colors.confirmed;

            return {
                id: apt.id,
                title: `${apt.client_name} - ${apt.service}`,
                start,
                end,
                backgroundColor: color.bg,
                borderColor: color.border,
                extendedProps: {
                    client_phone: apt.client_phone,
                    service: apt.service,
                    status: apt.status,
                    notes: apt.notes,
                },
            };
        });

        setCalendarEvents(events);
    }, [appointments]);

    const handleDateClick = (arg: any) => {
        setSelectedDate(new Date(arg.date));
        setSelectedAppointment(null);
        setModalMode("create");
        setIsModalOpen(true);
    };

    const handleEventClick = (info: any) => {
        const appointment = appointments.find((a: AppointmentResponse) => a.id === info.event.id);
        if (appointment) {
            setSelectedAppointment(appointment);
            setModalMode("edit");
            setIsModalOpen(true);
        }
    };

    const handleNewAppointment = () => {
        setSelectedDate(undefined);
        setSelectedAppointment(null);
        setModalMode("create");
        setIsModalOpen(true);
    };

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Schedule</h1>
                    <p className="text-muted-foreground">
                        View and manage appointments in calendar view
                    </p>
                </div>
                <Button
                    className="gap-2 bg-gradient-to-r from-primary to-accent"
                    onClick={handleNewAppointment}
                >
                    <Plus className="w-4 h-4" />
                    New Appointment
                </Button>
            </div>

            {/* Legend */}
            <div className="bg-white border border-slate-200 shadow-sm rounded-lg p-4 mb-6">
                <div className="flex flex-wrap gap-4">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-green-500"></div>
                        <span className="text-sm">Confirmed</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-blue-500"></div>
                        <span className="text-sm">Completed</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-red-500"></div>
                        <span className="text-sm">Cancelled</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-gray-500"></div>
                        <span className="text-sm">No Show</span>
                    </div>
                </div>
            </div>

            {/* Calendar */}
            <div className="bg-white border border-slate-200 shadow-sm rounded-2xl p-6">
                <FullCalendar
                    plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
                    initialView="timeGridWeek"
                    headerToolbar={{
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth,timeGridWeek,timeGridDay'
                    }}
                    events={calendarEvents}
                    dateClick={handleDateClick}
                    eventClick={handleEventClick}
                    editable={true}
                    selectable={true}
                    selectMirror={true}
                    dayMaxEvents={true}
                    weekends={true}
                    slotMinTime="08:00:00"
                    slotMaxTime="21:00:00"
                    height="auto"
                    eventTimeFormat={{
                        hour: '2-digit',
                        minute: '2-digit',
                        meridiem: 'short'
                    }}
                />
            </div>

            <AppointmentFormModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                mode={modalMode}
                appointment={selectedAppointment}
                initialDate={selectedDate}
            />
        </div>
    );
}
