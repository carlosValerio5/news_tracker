import { apiClient } from "../../services/api";
import { useState, useEffect } from "react";
import type { RecentActivitiesResponse } from "../../types/activities";

export default function RecentActivity() {
  const [activities, setActivities] = useState<RecentActivitiesResponse | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0); // to trigger reloads

  function getErrorMessage(err: unknown) {
    if (typeof err === "string") return err;
    if (err instanceof Error) return err.message;
    try {
      return JSON.stringify(err);
    } catch {
      return String(err);
    }
  }

  useEffect(() => {
    let mounted = true;
    const ctrl = new AbortController();

    (async () => {
      try {
        const res = await apiClient.get("/admin/recent-activities", {
          signal: ctrl.signal,
        });
        if (!mounted) return;
        if (res.ok && res.data) {
          setActivities(res.data as RecentActivitiesResponse);
        } else setError("Failed to fetch recent activities");
      } catch (err) {
        if (!mounted) return;
        if (typeof err === "string" && err === "AbortError") return;
        if (err instanceof Error && err.name === "AbortError") return;
        const errorMessage = getErrorMessage(err);
        setError(errorMessage);
      }
    })();

    return () => {
      mounted = false;
      ctrl.abort();
    };
  }, [reloadKey]);

  if (error) {
    return (
      <div className="h-full w-full rounded-lg border border-border-color bg-normal p-4 shadow-default flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-text-principal">
          Recent Activity
        </h2>
        <div className="text-sm text-red-600">Error: {error}</div>
        <div>
          <button
            onClick={() => setReloadKey((k) => k + 1)}
            className="mt-2 px-3 py-1 rounded bg-dark text-white"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full rounded-lg border border-border-color bg-normal backdrop-blur-sm p-4 shadow-default flex flex-col gap-3">
      <h2 className="text-sm font-semibold text-text-principal">
        Recent Activity
      </h2>
      <ul className="text-sm text-text-secondary space-y-1 list-disc list-inside">
        {activities && activities.activities.length > 0 ? (
          activities.activities.map((activity, index) => (
            <li key={index}>{activity.description}</li>
          ))
        ) : (
          <li>No recent activity</li>
        )}
      </ul>
    </div>
  );
}
