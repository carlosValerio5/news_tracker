import { useState, useEffect } from "react";
import { apiClient } from "../services/api";
import type { Metrics } from "../types/stats";
import type { Stat } from "../types/stats";

export function useAdminMetrics() {
  const [data, setData] = useState<Metrics>({
    activeUsers: null,
    newSignups: null,
    reportsGenerated: null,
  });

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ctrl = new AbortController();
    setLoading(true);
    setError(null);

    const fetchJson = async (url: string) => {
      const res = await apiClient.get(url, { signal: ctrl.signal });
      if (!res.ok) setError("Failed to fetch data");
      return res.data as Stat | null;
    };

    (async () => {
      try {
        // run in parallel
        const [activeUsers, newSignups, reportsGenerated] = await Promise.all([
          fetchJson("/admin/active-users"),
          fetchJson("/admin/new-signups"),
          fetchJson("/admin/reports-generated"),
        ]);
        setData({ activeUsers, newSignups, reportsGenerated });
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") return;
        if (err instanceof Error) setError(err.message);
        setError("Failed to load admin metrics");
      } finally {
        setLoading(false);
      }
    })();

    return () => ctrl.abort();
  }, []); // add deps if apiClient or base changes

  return { data, loading, error };
}
