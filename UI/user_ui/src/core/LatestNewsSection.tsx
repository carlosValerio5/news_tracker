import { useEffect, useState } from "react";
import Card from "../components/Card";
import { apiClient } from "../services/api";
import type { ApiResponse } from "../services/api";
import type { NewsEntry } from "../components/Card";

const DEFAULT_COUNT = 3;

function LatestNewsSection() {
  const [items, setItems] = useState<NewsEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const ctrl = new AbortController();

    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res: ApiResponse<NewsEntry[]> = await apiClient.get<NewsEntry[]>(
          "/news-report",
          { signal: ctrl.signal },
        );

        if (!mounted) return;

        if (res.ok && Array.isArray(res.data)) {
          setItems(res.data.slice(0, DEFAULT_COUNT));
        } else {
          setItems([]);
        }
      } catch (err) {
        if (!mounted) return;
        if (err instanceof Error && err.name === "AbortError") return;
        console.error("Failed to load latest news", err);
        setError("Failed to load latest news");
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
      ctrl.abort();
    };
  }, []);

  return (
    <div className="w-full lg:p-5 sm:mt-10 mb-10 gap-4">
      <h1 className="ml-3 text-2xl font-bold col-span-3">Latest News</h1>

      {loading ? (
        <div className="pl-3 py-5">Loading latest news...</div>
      ) : error ? (
        <div className="pl-3 py-5 text-red-600">{error}</div>
      ) : (
        <div className="pl-3 py-5 flex flex-row overflow-x-auto gap-4 lg:grid lg:grid-cols-3 lg:grid-rows-1 lg:gap-2 lg:overflow-x-visible">
          {items.map((item: NewsEntry) => (
            <Card key={item.url} newsEntry={item} />
          ))}
        </div>
      )}
    </div>
  );
}

export default LatestNewsSection;
