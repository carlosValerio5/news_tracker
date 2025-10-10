export default function AdminActions({
  setVisible,
}: {
  setVisible: (index: number) => void;
}) {
  return (
    <div className="h-fit w-full rounded-lg border border-border-color bg-gradient-to-b from-light to-normal p-5 shadow-default flex flex-col gap-4">
      <h2 className="text-sm font-semibold text-text-principal">
        Admin Actions
      </h2>
      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => setVisible(0)}
          className="px-4 py-2 text-sm rounded-md bg-light text-text-principal hover:bg-dark/80 focus:outline-none focus:ring-2 focus:ring-dark/40 shadow-default"
        >
          Register Admin
        </button>
        <button
          onClick={() => setVisible(1)}
          className="px-4 py-2 text-sm rounded-md bg-light text-text-light hover:bg-dark/80 focus:outline-none focus:ring-2 focus:ring-dark/40 shadow-default"
        >
          Add Email Recipient
        </button>
      </div>
    </div>
  );
}
