import { useState, useEffect } from "react";
import { apiClient } from "../services/api";

export type Stat = { value_daily: number | string; value_weekly?: number | string; diff?: number, label?: string };

type Metrics = {
  activeUsers: Stat | null;
  newSignups: Stat | null;
  reportsGenerated: Stat | null;
};


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
        if (!res || !res.ok) {
            let msg = `Request failed: ${res?.status ?? "no response"}`;
            try {
                const body = await res?.json();
                if (body?.detail) msg = String(body.detail);
                } catch {
                    setError("Failed to parse error response");
                }
            throw new Error(msg);
        }
        return res.json();
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

