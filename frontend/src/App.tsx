import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { DataRefreshProvider } from "./contexts/DataRefreshContext";
import { ConfigProvider } from "./contexts/ConfigContext";
import Index from "./pages/Index";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import Appointments from "./pages/Appointments";
import Conversations from "./pages/Conversations";
import Services from "./pages/Services";
import WhatsApp from "./pages/WhatsApp";
import AIReceptionist from "./pages/AIReceptionist";
import AIReceptionistTest from "./pages/AIReceptionist/Test";
import Schedule from "./pages/Schedule";
import Settings from "./pages/Settings";
import BusinessSettings from "./pages/Settings/Business";
import TeamSettings from "./pages/Settings/Team";
import AISettings from "./pages/Settings/AI";
import IntegrationsSettings from "./pages/Settings/Integrations";
import ServicesSettings from "./pages/Settings/Services";
import HoursSettings from "./pages/Settings/Hours";
import Help from "./pages/Help";
import ApiTest from "./pages/ApiTest";
import VoiceAgent from "./pages/VoiceAgent";
import VoiceTest from "./pages/VoiceAgent/Test";
import VoiceSettings from "./pages/VoiceAgent/Settings";
import VoiceChat from "./pages/VoiceAgent/VoiceChatVapi";

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: true,
            refetchOnMount: true,
            refetchOnReconnect: true,
            staleTime: 30000, // Data stays fresh for 30 seconds
            retry: 1,
            refetchInterval: 30000, // Poll every 30 seconds (balanced for real-time without excessive load)
        },
    },
});

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const token = localStorage.getItem("access_token");
    if (!token) {
        return <Navigate to="/login" replace />;
    }
    return <>{children}</>;
};

const App = () => (
    <QueryClientProvider client={queryClient}>
        <DataRefreshProvider>
            <ConfigProvider>
                <TooltipProvider>
                    <Toaster />
                    <Sonner />
                    <BrowserRouter
                        future={{
                            v7_startTransition: true,
                            v7_relativeSplatPath: true,
                        }}
                    >
                        <Routes>
                            <Route path="/login" element={<Login />} />

                            {/* Dashboard */}
                            <Route
                                path="/"
                                element={
                                    <ProtectedRoute>
                                        <Index />
                                    </ProtectedRoute>
                                }
                            />

                            {/* Appointments */}
                            <Route
                                path="/appointments"
                                element={
                                    <ProtectedRoute>
                                        <Appointments />
                                    </ProtectedRoute>
                                }
                            />

                            {/* Conversations */}
                            <Route
                                path="/conversations"
                                element={
                                    <ProtectedRoute>
                                        <Conversations />
                                    </ProtectedRoute>
                                }
                            />

                            {/* Services */}
                            <Route
                                path="/services"
                                element={
                                    <ProtectedRoute>
                                        <Services />
                                    </ProtectedRoute>
                                }
                            />

                            {/* AI Receptionist */}
                            <Route
                                path="/ai-receptionist"
                                element={
                                    <ProtectedRoute>
                                        <AIReceptionist />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/ai-receptionist/test"
                                element={
                                    <ProtectedRoute>
                                        <AIReceptionistTest />
                                    </ProtectedRoute>
                                }
                            />

                            {/* Schedule/Calendar */}
                            <Route
                                path="/schedule"
                                element={
                                    <ProtectedRoute>
                                        <Schedule />
                                    </ProtectedRoute>
                                }
                            />

                            {/* WhatsApp */}
                            <Route
                                path="/whatsapp"
                                element={
                                    <ProtectedRoute>
                                        <WhatsApp />
                                    </ProtectedRoute>
                                }
                            />

                            {/* Voice Agent */}
                            <Route
                                path="/voice-agent"
                                element={
                                    <ProtectedRoute>
                                        <VoiceAgent />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/voice-agent/test"
                                element={
                                    <ProtectedRoute>
                                        <VoiceTest />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/voice-agent/settings"
                                element={
                                    <ProtectedRoute>
                                        <VoiceSettings />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/voice-agent/chat"
                                element={
                                    <ProtectedRoute>
                                        <VoiceChat />
                                    </ProtectedRoute>
                                }
                            />

                            {/* Settings */}
                            <Route
                                path="/settings"
                                element={
                                    <ProtectedRoute>
                                        <Settings />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/settings/business"
                                element={
                                    <ProtectedRoute>
                                        <BusinessSettings />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/settings/team"
                                element={
                                    <ProtectedRoute>
                                        <TeamSettings />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/settings/ai"
                                element={
                                    <ProtectedRoute>
                                        <AISettings />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/settings/integrations"
                                element={
                                    <ProtectedRoute>
                                        <IntegrationsSettings />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/settings/services"
                                element={
                                    <ProtectedRoute>
                                        <ServicesSettings />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/settings/hours"
                                element={
                                    <ProtectedRoute>
                                        <HoursSettings />
                                    </ProtectedRoute>
                                }
                            />

                            {/* Help */}
                            <Route
                                path="/help"
                                element={
                                    <ProtectedRoute>
                                        <Help />
                                    </ProtectedRoute>
                                }
                            />

                            {/* API Testing */}
                            <Route
                                path="/api-test"
                                element={
                                    <ProtectedRoute>
                                        <ApiTest />
                                    </ProtectedRoute>
                                }
                            />

                            {/* Catch-all 404 */}
                            <Route path="*" element={<NotFound />} />
                        </Routes>
                    </BrowserRouter>
                </TooltipProvider>
            </ConfigProvider>
        </DataRefreshProvider>
    </QueryClientProvider>
);

export default App;
