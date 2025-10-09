import { useState } from "react";
import { apiClient } from "../../services/api";
import type { AdminConfigResponse } from "../../types/admin";
import type { AdminConfig } from "../../types/admin";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function AddEmailRecipient({
  isActive,
}: {
  isActive: boolean;
}): JSX.Element {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [summarySendTime, setSummarySendTime] = useState("08:00");
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const emailRecipient = {
    target_email: email,
    summary_send_time: summarySendTime,
    last_updated: new Date(),
  };

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
      emailRecipient.last_updated = new Date();
      const res = await apiClient.post(
        "/admin/admin-config",
        emailRecipient as AdminConfig,
      );
      // try to parse JSON when available
      let payload: AdminConfigResponse | null = null;
      try {
        payload = (await res.json()) as AdminConfigResponse;
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
        htmlFor="email-recipient"
        className="block text-sm font-medium text-text-principal mb-2"
      >
        Add Email Recipient
      </label>

      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <input
            id="email-recipient"
            name="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="email@example.com"
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

        <div className="flex flex-col">
          <label
            htmlFor="summary-send-time"
            className="block text-xs text-text-secondary mb-1"
          >
            Summary send time
          </label>
          <select
            id="summary-send-time"
            value={summarySendTime}
            onChange={(e) => setSummarySendTime(e.target.value)}
            className="px-3 py-2 rounded-md border border-border-color bg-light text-text-principal placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-dark/30"
          >
            <option value="08:00">08:00</option>
            <option value="14:00">14:00</option>
            <option value="20:00">20:00</option>
          </select>
        </div>
      </div>

      <p className="mt-2 text-sm">
        {error && <span className="text-red-600">{error}</span>}
        {success && <span className="text-green-600">{success}</span>}
      </p>
    </form>
  );
}
