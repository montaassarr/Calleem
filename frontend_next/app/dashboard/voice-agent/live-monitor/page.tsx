"use client";

import LiveCallMonitor from "@/components/dashboard/LiveCallMonitor";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity } from "lucide-react";

export default function LiveMonitorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Activity className="h-8 w-8" />
          Live Call Monitor
        </h1>
        <p className="text-muted-foreground mt-2">
          Real-time monitoring of active voice calls with transcript streaming
        </p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>📡 Real-Time Call Activity</CardTitle>
            <CardDescription>
              Monitor live calls, view transcripts as they happen, and track tool executions.
              This monitor receives real-time updates via WebSocket for instant visibility.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LiveCallMonitor />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>ℹ️ How It Works</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div>
              <strong className="text-primary">Real-Time Transcripts:</strong>
              <p className="text-muted-foreground">
                As your AI assistant talks with callers, every message is captured and displayed
                instantly. You'll see both assistant responses and user messages in real-time.
              </p>
            </div>
            <div>
              <strong className="text-primary">Call Status Updates:</strong>
              <p className="text-muted-foreground">
                Track call lifecycle events: when calls start, their current status, and when they end.
                All status changes are broadcast immediately via WebSocket.
              </p>
            </div>
            <div>
              <strong className="text-primary">Tool Execution Tracking:</strong>
              <p className="text-muted-foreground">
                See when your assistant uses tools like checkAvailability or bookAppointment.
                Monitor what actions are being taken during each call.
              </p>
            </div>
            <div>
              <strong className="text-primary">Persistent History:</strong>
              <p className="text-muted-foreground">
                All transcript data is automatically saved to your conversation history.
                Review past calls anytime in the Conversations section.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
