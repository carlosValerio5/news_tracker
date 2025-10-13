import StatCard from "../components/admin/StatCard";
import RecentActivity from "../components/admin/RecentActivity";
import AdminActions from "../components/admin/AdminActions";
import RegisterAdmin from "../components/admin/RegisterAdmin";
import AddEmailRecipient from "../components/admin/AddEmailRecipient";
import { useState } from "react";
import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiClient } from "../services/api";
import { useAdminMetrics } from "../hooks/useAdminMetrics";
import type { Stat } from "../hooks/useAdminMetrics";


function AdminDashboard() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [adminAuthenticated, setAdminAuthenticated] = useState<boolean | null>(
    null,
  );
  const navigate = useNavigate();

  const { data, loading: metricsLoading, error } = useAdminMetrics();

  const activeUsers: Stat = {
    value_daily: metricsLoading ? "Loading..." : data.activeUsers?.value_daily ?? "—",
    value_weekly: metricsLoading ? "Loading..." : data.activeUsers?.value_weekly ?? "—",
    diff: metricsLoading ? undefined : data.activeUsers?.diff,
    label: "Active Users"
  }

  const newSignups: Stat = {
    value_daily: metricsLoading ? "Loading..." : data.newSignups?.value_daily ?? "—",
    value_weekly: metricsLoading ? "Loading..." : data.newSignups?.value_weekly ?? "—",
    diff: metricsLoading ? undefined : data.newSignups?.diff,
    label: "New Signups"
  }

  const reportsGenerated: Stat = {
    value_daily: metricsLoading ? "Loading..." : data.reportsGenerated?.value_daily ?? "—",
    value_weekly: metricsLoading ? "Loading..." : data.reportsGenerated?.value_weekly ?? "—",
    diff: metricsLoading ? undefined : data.reportsGenerated?.diff,
    label: "Reports Generated"
  }

  useEffect(() => {
    let mounted = true;

    const check = async () => {
      try {
        const response = await apiClient.get("/admin");
        if (!mounted) return;
        setAdminAuthenticated(response?.status === 200);
      } catch {
        if (!mounted) return;
        setAdminAuthenticated(false);
      }
    };

    // initial check
    check();
    // Interval set to 1 hour (3,600,000 ms)
    const id = setInterval(check, 3_600_000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []); // keep empty if apiClient is stable; otherwise include stable deps

  // navigate only after we've completed the auth check
  useEffect(() => {
    if (adminAuthenticated === false) {
      navigate("/auth-failed", { replace: true });
    }
  }, [adminAuthenticated, navigate]);

  // render a simple loading state while we don't know auth status
  if (adminAuthenticated === null) {
    return (
      <div className="h-screen w-screen flex items-center justify-center">
        Checking authentication…
      </div>
    );
  }

  return (
    <main className="h-screen w-screen bg-light text-text-principal flex flex-col">
      {/* Top Bar */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border-color backdrop-blur-sm bg-light/70 shadow-default/5">
        <Link to="/" className="text-xl font-semibold tracking-tight">
          Admin Dashboard
        </Link>
        <div className="flex items-center gap-3 text-sm text-text-secondary">
          <span className="hidden sm:inline">System Healthy</span>
          <span
            className="w-2 h-2 rounded-full bg-green-500 inline-block"
            aria-label="system healthy"
          />
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 h-full w-full max-w-7xl mx-auto px-6 py-8 flex flex-col gap-8 overflow-auto">
        {/* Stats Grid */}
        <section
          aria-labelledby="stats-heading"
          className="grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-3"
        >
          <h2 id="stats-heading" className="sr-only">
            Key Metrics
          </h2>
          {error ? (
            <div className="text-red-600">
              Error loading metrics: {error}
            </div>
          ) : (
            <>
              <StatCard s={activeUsers} weekAndDay={true}/>
              <StatCard s={newSignups} weekAndDay={true}/>
              <StatCard s={reportsGenerated} weekAndDay={false}/>
            </>
          )}
        </section>

        {/* Two Column Layout */}
        <div className="grid gap-6 grid-cols-1 lg:grid-cols-3 h-full">
          <div className="lg:col-span-2 flex flex-col gap-6 h-full">
            <RecentActivity />
          </div>
          <div className="flex flex-col gap-6 h-full">
            <AdminActions setVisible={setActiveIndex} />
            <RegisterAdmin isActive={activeIndex === 0} />
            <AddEmailRecipient isActive={activeIndex === 1} />
          </div>
        </div>
      </div>
    </main>
  );
}

export default AdminDashboard;
