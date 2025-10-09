export default function RecentActivity() {
  return (
    <div className="h-full w-full rounded-lg border border-border-color bg-normal backdrop-blur-sm p-4 shadow-default flex flex-col gap-3">
      <h2 className="text-sm font-semibold text-text-principal">
        Recent Activity
      </h2>
      <ul className="text-sm text-text-secondary space-y-1 list-disc list-inside">
        <li>User john@example.com promoted to admin</li>
        <li>Daily trends job completed successfully</li>
        <li>Queued 24 new articles for NLP pipeline</li>
      </ul>
    </div>
  );
}
