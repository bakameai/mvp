
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./components/theme/ThemeProvider";
import { AnalyticsProvider } from "./components/analytics/AnalyticsProvider";
import IVR from "./pages/IVR";
import NotFound from "./pages/NotFound";
import AdminDashboard from "./pages/AdminDashboard";
import TelephonyAdminDashboard from "./pages/TelephonyAdminDashboard";
import LearningModules from "./pages/LearningModules";
import IVRInterface from "./pages/IVRInterface";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <TooltipProvider>
        <AnalyticsProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<AdminDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin-dashboard" element={<AdminDashboard />} />
              <Route path="/telephony-admin" element={<TelephonyAdminDashboard />} />
              <Route path="/learning-modules" element={<LearningModules />} />
              <Route path="/ivr" element={<IVR />} />
              <Route path="/ivr-interface" element={<IVRInterface />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </AnalyticsProvider>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
