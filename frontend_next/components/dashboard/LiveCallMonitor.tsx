"use client";

import React, { useEffect, useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Activity } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

interface CallEvent {
    type: string;
    [key: string]: any;
}

interface LogItem {
    time: string;
    message: string;
    type: 'info' | 'transcript' | 'tool';
    role?: 'assistant' | 'user';
}

export default function LiveCallMonitor() {
    const [connected, setConnected] = useState(false);
    const [status, setStatus] = useState<'idle' | 'active'>('idle');
    const [logs, setLogs] = useState<LogItem[]>([]);
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll logs
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    // Initialize WebSocket
    useEffect(() => {
        const connectWs = () => {
            const userStr = localStorage.getItem('user');
            if (!userStr) return;

            try {
                const user = JSON.parse(userStr);
                const tenantId = user.tenant_id;
                const token = localStorage.getItem('token');

                if (!tenantId || !token) return;

                const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/${tenantId}?token=${token}`;

                const ws = new WebSocket(wsUrl);

                ws.onopen = () => {
                    setConnected(true);
                    addLog("Connected to Live Monitor", 'info');
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        handleEvent(data);
                    } catch (e) {
                        console.error("WS Parse error", e);
                    }
                };

                ws.onclose = () => {
                    setConnected(false);
                    setStatus('idle');
                    addLog("Disconnected from Live Monitor", 'info');
                };

                setSocket(ws);
            } catch (e) {
                console.error("Auth parse error", e);
            }
        };

        connectWs();

        return () => {
            if (socket) socket.close();
        };
    }, []);

    const addLog = (message: string, type: 'info' | 'transcript' | 'tool', role?: 'assistant' | 'user') => {
        const time = new Date().toLocaleTimeString();
        setLogs(prev => [...prev.slice(-49), { time, message, type, role }]);
    };

    const handleEvent = (event: CallEvent) => {
        switch (event.type) {
            case 'call_started':
            case 'call-start':
                setStatus('active');
                addLog(`📞 Call Started (ID: ${event.call_id?.slice(0, 8) || 'N/A'}...)`, 'info');
                if (event.phone_number) {
                    addLog(`Caller: ${event.phone_number}`, 'info');
                }
                break;

            case 'transcript':
                const role = event.role || 'unknown';
                const text = event.transcript || event.text || event.message || '';
                if (text) {
                    addLog(text, 'transcript', role as 'assistant' | 'user');
                }
                break;

            case 'status-update':
            case 'status_update':
                if (event.status) {
                    addLog(`Status: ${event.status}`, 'info');
                    if (event.status === 'ended') {
                        setStatus('idle');
                    }
                }
                break;

            case 'call_ended':
            case 'end-of-call-report':
                setStatus('idle');
                addLog(`📵 Call Ended`, 'info');
                if (event.duration) {
                    addLog(`Duration: ${Math.round(event.duration / 60)} minutes`, 'info');
                }
                break;

            case 'tool_usage':
            case 'tool-calls':
            case 'function-call':
                const toolName = event.tool_name || event.function_name || event.name || 'Unknown';
                addLog(`🔧 Tool: ${toolName}`, 'tool');
                break;

            default:
                console.log('Unhandled event type:', event.type, event);
                break;
        }
    };

    return (
        <Card className="h-[600px] flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div>
                    <CardTitle>Live Call Monitor</CardTitle>
                    <CardDescription>Real-time transcription and status</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                    {connected ? (
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Online</Badge>
                    ) : (
                        <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Offline</Badge>
                    )}
                    {status === 'active' && (
                        <span className="relative flex h-3 w-3">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                        </span>
                    )}
                </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden p-0">
                <ScrollArea className="h-full p-4" ref={scrollRef}>
                    {logs.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-gray-400 mt-20">
                            <Activity className="h-12 w-12 mb-2 opacity-20" />
                            <p>Waiting for calls...</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {logs.map((log, i) => (
                                <div key={i} className={`flex flex-col gap-1 ${
                                    log.type === 'transcript' 
                                        ? (log.role === 'user' ? 'items-end' : 'items-start') 
                                        : 'items-center'
                                }`}>
                                    {log.type === 'info' && (
                                        <div className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-full my-1">
                                            {log.message}
                                        </div>
                                    )}

                                    {log.type === 'tool' && (
                                        <div className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-100 font-mono my-1">
                                            ⚡ {log.message}
                                        </div>
                                    )}

                                    {log.type === 'transcript' && (
                                        <>
                                            <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                                                log.role === 'user'
                                                    ? 'bg-blue-600 text-white rounded-br-none'
                                                    : 'bg-gray-100 text-gray-800 rounded-bl-none'
                                            }`}>
                                                <p>{log.message}</p>
                                            </div>
                                            <span className="text-[10px] text-gray-300 px-1">
                                                {log.role === 'user' ? 'Anonymous' : 'AI Assistant'} • {log.time}
                                            </span>
                                        </>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </ScrollArea>
            </CardContent>
        </Card>
    );
}
