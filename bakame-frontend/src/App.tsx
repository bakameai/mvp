import React from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./components/theme/ThemeProvider";
import { AnalyticsProvider } from "./components/analytics/AnalyticsProvider";
import Index from "./pages/Index";
import About from "./pages/About";
import Team from "./pages/Team";
import Contact from "./pages/Contact";
import GovernmentSolution from "./pages/GovernmentSolution";
import EnterpriseSolution from "./pages/EnterpriseSolution";
import EducationSolution from "./pages/EducationSolution";
import GovernmentDemo from "./pages/GovernmentDemo";
import IVR from "./pages/IVR";
import Blog from "./pages/Blog";
import Support from "./pages/Support";
import Privacy from "./pages/Privacy";
import Terms from "./pages/Terms";
import NotFound from "./pages/NotFound";
import EarlyAccess from "./pages/EarlyAccess";
import Signup from "./pages/Signup";
import AdminDashboard from "./pages/AdminDashboard";
import TelephonyAdminDashboard from "./pages/TelephonyAdminDashboard";
import LearningModules from "./pages/LearningModules";
import IVRInterface from "./pages/IVRInterface";
import AdminSimple from "./pages/AdminSimple";

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
              <Route path="/" element={<AdminSimple />} />
              <Route path="/about" element={<About />} />
              <Route path="/team" element={<Team />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/government-solution" element={<GovernmentSolution />} />
              <Route path="/enterprise-solution" element={<EnterpriseSolution />} />
              <Route path="/education-solution" element={<EducationSolution />} />
              <Route path="/government-demo" element={<GovernmentDemo />} />
              <Route path="/ivr" element={<IVR />} />
              <Route path="/blog" element={<Blog />} />
              <Route path="/support" element={<Support />} />
              <Route path="/privacy" element={<Privacy />} />
              <Route path="/terms" element={<Terms />} />
              <Route path="/early-access" element={<EarlyAccess />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin-dashboard" element={<AdminDashboard />} />
              <Route path="/telephony-admin" element={<TelephonyAdminDashboard />} />
              <Route path="/learning-modules" element={<LearningModules />} />
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
