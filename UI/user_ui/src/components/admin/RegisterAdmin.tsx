import { useState } from "react";
import { apiClient } from "../../services/api";
import type { RegisterAdminResponse } from "../../types/admin";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function RegisterAdmin({
  isActive,
}: {
  isActive: boolean;
}): JSX.Element {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function validate(value: string) {
    return EMAIL_REGEX.test(value);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!validate(email)) {
      setError("Please enter a valid email address");
      return;
    }

    setLoading(true);
    try {
      const res = await apiClient.post("/admin", { email });
      // try to parse JSON when available
      let payload: RegisterAdminResponse | null = null;
      try {
        payload = (await res.json()) as RegisterAdminResponse;
      } catch {
        // ignore JSON parse errors
      }

      if (!res.ok) {
        const message = payload?.detail || `Server returned ${res.status}`;
        setError(String(message));
      } else {
        setSuccess(payload?.detail || "Registration request submitted");
        setEmail("");
      }
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError("Network error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`w-full max-w-md ${isActive ? "block" : "hidden"} bg-normal p-4 rounded-xl border-border-color`}
    >
      <label
        htmlFor="admin-email"
        className="block text-sm font-medium text-text-principal mb-2"
      >
        Promote to admin
      </label>

      <div className="flex items-center gap-2">
        <input
          id="admin-email"
          name="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="admin@example.com"
          aria-invalid={error ? "true" : "false"}
          className={`flex-1 px-3 py-2 rounded-md border border-border-color bg-light text-text-principal placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-dark/30`}
        />

        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center px-4 py-2 rounded-md bg-dark text-text-secondary text-sm font-medium hover:bg-dark/80 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? "Sending…" : "Send"}
        </button>
      </div>

      <p className="mt-2 text-sm">
        {error && <span className="text-red-600">{error}</span>}
        {success && <span className="text-green-600">{success}</span>}
      </p>
    </form>
  );
}
