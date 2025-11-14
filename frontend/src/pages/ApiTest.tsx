import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { appointmentsApi } from "@/api";
import { toast } from "sonner";

const ApiTest = () => {
  const [testDate, setTestDate] = useState("2025-11-15");
  const [testTime, setTestTime] = useState("15:00");
  const [availabilityResult, setAvailabilityResult] = useState<any>(null);
  const [statsResult, setStatsResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleCheckAvailability = async () => {
    setLoading(true);
    try {
      const result = await appointmentsApi.checkAvailability(testDate, testTime, 30);
      setAvailabilityResult(result);
      if (result.available) {
        toast.success("Time slot is available!");
      } else {
        toast.error(result.reason);
      }
    } catch (error: any) {
      toast.error("Failed to check availability");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleGetStats = async () => {
    setLoading(true);
    try {
      const result = await appointmentsApi.getStats();
      setStatsResult(result);
      toast.success("Stats loaded successfully");
    } catch (error: any) {
      toast.error("Failed to get stats");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardHeader />
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold">API Testing</h1>
        </div>
        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Availability Check */}
            <Card>
              <CardHeader>
                <CardTitle>Check Availability</CardTitle>
                <CardDescription>
                  Test the availability checking endpoint
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Date</label>
                    <Input
                      type="date"
                      value={testDate}
                      onChange={(e) => setTestDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Time</label>
                    <Input
                      type="time"
                      value={testTime}
                      onChange={(e) => setTestTime(e.target.value)}
                    />
                  </div>
                </div>
                <Button onClick={handleCheckAvailability} disabled={loading}>
                  Check Availability
                </Button>
                
                {availabilityResult && (
                  <div className="mt-4 p-4 bg-gray-100 rounded-lg">
                    <pre className="text-sm">
                      {JSON.stringify(availabilityResult, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Statistics */}
            <Card>
              <CardHeader>
                <CardTitle>Appointment Statistics</CardTitle>
                <CardDescription>
                  Get overall appointment stats
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={handleGetStats} disabled={loading}>
                  Get Statistics
                </Button>
                
                {statsResult && (
                  <div className="mt-4 p-4 bg-gray-100 rounded-lg">
                    <pre className="text-sm">
                      {JSON.stringify(statsResult, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* API Endpoints Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Available API Endpoints</CardTitle>
                <CardDescription>
                  Complete list of appointment endpoints
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm font-mono">
                  <div className="flex items-center gap-2">
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded">GET</span>
                    <span>/api/v1/appointments</span>
                    <span className="text-gray-500">- List all appointments</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded">GET</span>
                    <span>/api/v1/appointments/:id</span>
                    <span className="text-gray-500">- Get one appointment</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">POST</span>
                    <span>/api/v1/appointments</span>
                    <span className="text-gray-500">- Create appointment</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded">PUT</span>
                    <span>/api/v1/appointments/:id</span>
                    <span className="text-gray-500">- Update appointment</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-red-100 text-red-800 px-2 py-1 rounded">DELETE</span>
                    <span>/api/v1/appointments/:id</span>
                    <span className="text-gray-500">- Delete permanently</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">POST</span>
                    <span>/api/v1/appointments/:id/cancel</span>
                    <span className="text-gray-500">- Cancel (set status)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded">GET</span>
                    <span>/api/v1/appointments/availability/check</span>
                    <span className="text-gray-500">- Check availability</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded">GET</span>
                    <span>/api/v1/appointments/stats/summary</span>
                    <span className="text-gray-500">- Get statistics</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ApiTest;
