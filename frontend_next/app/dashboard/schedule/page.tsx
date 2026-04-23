"use client";

import { Plus, ChevronLeft, ChevronRight, Calendar as CalendarIcon } from "lucide-react";
import { useState, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { appointmentsApi } from "@/lib/api-endpoints";
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import type { CalendarEvent } from "@/lib/types";
import { Sparkles, Scissors, User, SprayCan, Phone } from "lucide-react";

export default function SchedulePage() {
    const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([]);

    const { data: appointments = [] } = useQuery({
        queryKey: ["appointments"],
        queryFn: () => appointmentsApi.list(),
    });

    useEffect(() => {
        const events: CalendarEvent[] = appointments.map((apt: any) => {
            const start = new Date(apt.datetime);
            const end = new Date(start.getTime() + apt.duration_minutes * 60000);

            const colors: Record<string, { bg: string; border: string }> = {
                confirmed: { bg: '#187848', border: '#0a4c2f' },
                completed: { bg: '#5b8eff', border: '#3b6fdf' },
                cancelled: { bg: '#ef4444', border: '#dc2626' },
                no_show: { bg: '#9ca3af', border: '#6b7280' },
            };

            const color = colors[apt.status] || colors.confirmed;

            return {
                id: apt.id,
                title: `${apt.client_name} - ${apt.service}`,
                start,
                end,
                backgroundColor: 'transparent',
                borderColor: 'transparent',
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
        console.log('Date clicked:', arg.dateStr);
    };

    const handleEventClick = (info: any) => {
        console.log('Event clicked:', info.event);
    };

    const renderEventContent = (eventInfo: any) => {
        const { event } = eventInfo;
        const status = event.extendedProps.status || 'confirmed';
        const service = event.extendedProps.service || '';

        // Match colors/icons from AppointmentsTimeline
        let color = "bg-[#b6f09c]";
        let textColor = "text-[#0a4c2f]";
        let iconBg = "bg-[#0a4c2f] text-white";
        let icon = <Scissors className="w-3.5 h-3.5" />;

        if (service.toLowerCase().includes("color")) {
            color = "bg-[#ff9f2d]";
            textColor = "text-white";
            iconBg = "bg-black text-white";
            icon = <Sparkles className="w-3.5 h-3.5" />;
        } else if (service.toLowerCase().includes("consult")) {
            color = "bg-[#5b8eff]";
            textColor = "text-white";
            iconBg = "bg-white text-[#5b8eff]";
            icon = <User className="w-3.5 h-3.5" />;
        }

        const isCancelled = status === 'cancelled';

        return (
            <div className={`w-full h-full min-h-[30px] rounded-full flex items-center px-1 shadow-sm transition-transform hover:scale-[1.01] cursor-pointer overflow-hidden ${color} ${isCancelled ? 'opacity-50 grayscale' : ''}`}>
                <div className={`w-[24px] h-[24px] rounded-full flex items-center justify-center shrink-0 shadow-sm ${iconBg}`}>
                    {icon}
                </div>
                <span className={`ml-2 text-[11.5px] font-bold truncate pr-2 ${textColor}`}>
                    {event.title}
                </span>
            </div>
        );
    };

    return (
        <div>
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Schedule</h1>
                    <p className="text-[14px] text-gray-500 font-medium">View and manage appointments in calendar view.</p>
                </div>
                <button className="px-5 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-[20px] font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] flex items-center gap-2 relative overflow-hidden">
                    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                    <Plus className="w-4 h-4 relative z-10" />
                    <span className="relative z-10">New Appointment</span>
                </button>
            </div>

            {/* Legend */}
            <div className="bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-5 mb-6">
                <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
                    {[
                        { label: "Confirmed", color: "border-[#187848]" },
                        { label: "Completed", color: "border-[#5b8eff]" },
                        { label: "Cancelled", color: "border-red-500" },
                        { label: "No Show", color: "border-gray-400" },
                    ].map((item) => (
                        <div key={item.label} className="flex items-center gap-2">
                            <div className={`w-3 h-3 rounded-full border-2 ${item.color} bg-white`}></div>
                            <span className="text-[12px] font-bold text-gray-500">{item.label}</span>
                        </div>
                    ))}
                    <div className="ml-auto text-[12px] font-bold text-gray-400">
                        {calendarEvents.length} Booking{calendarEvents.length !== 1 ? 's' : ''}
                    </div>
                </div>
            </div>

            {/* Calendar Card */}
            <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                <style>{`
                    /* Callem Calendar Styles */
                    .fc {
                        --fc-border-color: #e5e7eb;
                        --fc-button-bg-color: #fff;
                        --fc-button-border-color: #e5e7eb;
                        --fc-button-text-color: #374151;
                        --fc-button-hover-bg-color: #f9fafb;
                        --fc-button-hover-border-color: #d1d5db;
                        --fc-button-active-bg-color: #0a4c2f;
                        --fc-button-active-border-color: #0a4c2f;
                        --fc-today-bg-color: #f0fdf4;
                        --fc-event-border-color: transparent;
                        --fc-page-bg-color: transparent;
                        font-family: 'Inter', sans-serif;
                    }
                    .fc .fc-toolbar-title {
                        font-size: 1.25rem;
                        font-weight: 700;
                        color: #111827;
                    }
                    .fc .fc-button {
                        border-radius: 12px !important;
                        font-weight: 600;
                        font-size: 13px;
                        padding: 6px 14px;
                        box-shadow: none !important;
                        transition: all 0.15s ease;
                    }
                    .fc .fc-button-group > .fc-button {
                        border-radius: 0 !important;
                    }
                    .fc .fc-button-group > .fc-button:first-child {
                        border-radius: 12px 0 0 12px !important;
                    }
                    .fc .fc-button-group > .fc-button:last-child {
                        border-radius: 0 12px 12px 0 !important;
                    }
                    .fc .fc-button-primary:not(:disabled).fc-button-active,
                    .fc .fc-button-primary:not(:disabled):active {
                        background: linear-gradient(to bottom, #187848, #0a4c2f);
                        border-color: #0a4c2f;
                        color: #fff;
                    }
                    .fc .fc-col-header-cell-cushion {
                        font-weight: 700;
                        color: #6b7280;
                        font-size: 12px;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                        padding: 10px 0;
                    }
                    .fc .fc-daygrid-day-number {
                        font-weight: 600;
                        color: #374151;
                        font-size: 13px;
                        padding: 6px 8px;
                    }
                    .fc .fc-timegrid-slot-label-cushion {
                        font-weight: 600;
                        color: #9ca3af;
                        font-size: 11px;
                    }
                    .fc td, .fc th {
                        border-color: #f3f4f6;
                    }
                    .fc .fc-scrollgrid {
                        border-radius: 16px;
                        overflow: hidden;
                        border: 1px solid #f3f4f6;
                    }
                    .fc .fc-event {
                        border: none !important;
                        border-radius: 24px;
                        font-weight: 600;
                        font-size: 12px;
                        padding: 0 !important;
                        background: transparent !important;
                        box-shadow: none !important;
                    }
                    .fc .fc-timegrid-event .fc-event-main {
                        padding: 0 !important;
                    }
                    .fc .fc-day-today .fc-daygrid-day-number {
                        color: #0a4c2f;
                    }
                    .fc .fc-highlight {
                        background: rgba(10, 76, 47, 0.08);
                    }
                    .fc .fc-daygrid-day.fc-day-today {
                        background: #f0fdf4;
                    }
                    .fc .fc-timegrid-col.fc-day-today {
                        background: #f0fdf4;
                    }
                    .fc .fc-prev-button, .fc .fc-next-button {
                        border-radius: 12px !important;
                    }
                `}</style>

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
                    eventContent={renderEventContent}
                    eventTimeFormat={{
                        hour: '2-digit',
                        minute: '2-digit',
                        meridiem: 'short'
                    }}
                />
            </div>
        </div>
    );
}
