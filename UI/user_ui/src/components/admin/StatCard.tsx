type Stat = { label: string; value: string | number; diff?: number };

export default function StatCard({ s }: { s: Stat }) {
  const trendColor =
    s.diff === undefined ? "" : s.diff >= 0 ? "text-green-600" : "text-red-600";
  const sign = s.diff && s.diff > 0 ? "+" : "";
  return (
    <div className="h-full w-full rounded-lg border border-border-color bg-gradient-to-b from-normal/95 to-light p-4 shadow-default flex flex-col gap-1 hover:from-normal/5 hover:to-light transition-colors">
      <span className="text-xs uppercase tracking-wide text-text-secondary">
        {s.label}
      </span>
      <span className="text-2xl font-semibold text-text-principal">
        {s.value}
      </span>
      {s.diff !== undefined && (
        <span className={`text-xs font-medium ${trendColor}`}>
          {sign}
          {s.diff}%
        </span>
      )}
    </div>
  );
}
