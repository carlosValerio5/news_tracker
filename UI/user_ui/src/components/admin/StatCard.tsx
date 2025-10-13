import { useState } from "react";
import type { Stat } from "../../types/stats";

export default function StatCard({
  s,
  weekAndDay,
}: {
  s: Stat;
  weekAndDay: boolean;
}) {
  const [activeIndex, setActiveIndex] = useState<number>(1);

  const trendColor =
    s.diff === undefined ? "" : s.diff >= 0 ? "text-green-600" : "text-red-600";
  const sign = s.diff && s.diff > 0 ? "+" : "";
  return (
    <div className="h-full w-full rounded-lg border border-border-color bg-gradient-to-b from-normal/95 to-light p-4 shadow-default flex flex-col gap-1 hover:from-normal/5 hover:to-light transition-colors">
      <span className="text-xs uppercase tracking-wide text-text-secondary">
        {s.label}
      </span>
      <div className="flex gap-2">
        <button
          className={`${weekAndDay ? "block" : "hidden"} ${activeIndex === 0 ? "bg-black text-white" : ""} text-xs p-2 border rounded-xl border-black/30 hover:text-text-secondary`}
          onClick={() => setActiveIndex(0)}
        >
          7 Days
        </button>
        <button
          className={`${activeIndex === 1 ? "bg-black text-white" : ""} text-xs p-2 border rounded-xl border-black/30 hover:text-text-secondary`}
          onClick={() => setActiveIndex(1)}
        >
          1 Day
        </button>
      </div>
      <span
        className={`text-2xl font-semibold text-text-principal  ${activeIndex === 0 ? "" : "hidden"}`}
      >
        {s.value_weekly}
      </span>
      <span
        className={`text-2xl font-semibold text-text-principal  ${activeIndex === 1 ? "" : "hidden"}`}
      >
        {s.value_daily}
      </span>
      {s.diff !== undefined && s.diff !== null && (
        <div>
          <span
            className={`text-xs font-medium ${trendColor} ${activeIndex === 0 ? "" : "hidden"}`}
          >
            {sign}
            {s.diff}%
          </span>
        </div>
      )}
    </div>
  );
}
