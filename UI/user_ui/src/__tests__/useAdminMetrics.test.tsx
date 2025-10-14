import { render, screen, waitFor, cleanup } from "@testing-library/react";

// Use the manual mock so tests are consistent
jest.mock("../services/api");
import * as api from "../services/api";

import { useAdminMetrics } from "../hooks/useAdminMetrics";

function Harness() {
  const { data, loading, error } = useAdminMetrics();
  return (
    <div>
      <div data-testid="loading">{String(loading)}</div>
      <div data-testid="error">{error ?? ""}</div>
      <pre data-testid="data">{JSON.stringify(data)}</pre>
    </div>
  );
}

describe("useAdminMetrics", () => {
  afterEach(() => {
    cleanup();
    (api.apiClient.get as jest.Mock).mockReset();
  });

  it("loads metrics successfully", async () => {
    const a = { label: "Active", value_daily: 10, value_weekly: 70, diff: 5 };
    const b = { label: "Signups", value_daily: 3, value_weekly: 20, diff: 2 };
    const c = { label: "Reports", value_daily: 4, value_weekly: 25, diff: 1 };

    (api.apiClient.get as jest.Mock)
      .mockResolvedValueOnce({ ok: true, data: a, status: 200 })
      .mockResolvedValueOnce({ ok: true, data: b, status: 200 })
      .mockResolvedValueOnce({ ok: true, data: c, status: 200 });

    render(<Harness />);

    await waitFor(() =>
      expect(screen.getByTestId("loading").textContent).toBe("false"),
    );

    const json = JSON.parse(screen.getByTestId("data").textContent || "{}");
    expect(json.activeUsers).toEqual(a);
    expect(json.newSignups).toEqual(b);
    expect(json.reportsGenerated).toEqual(c);
    expect(screen.getByTestId("error").textContent).toBe("");
  });

  it("handles a partial (non-ok) response and sets error", async () => {
    const a = { label: "Active", value_daily: 10, value_weekly: 70, diff: 5 };
    const b = { label: "Signups", value_daily: 3, value_weekly: 20, diff: 2 };

    (api.apiClient.get as jest.Mock)
      .mockResolvedValueOnce({ ok: true, data: a, status: 200 })
      .mockResolvedValueOnce({ ok: true, data: b, status: 200 })
      .mockResolvedValueOnce({ ok: false, data: null, status: 500 });

    render(<Harness />);

    await waitFor(() =>
      expect(screen.getByTestId("loading").textContent).toBe("false"),
    );

    const json = JSON.parse(screen.getByTestId("data").textContent || "{}");
    expect(json.activeUsers).toEqual(a);
    expect(json.newSignups).toEqual(b);
    expect(json.reportsGenerated).toBeNull();
    expect(screen.getByTestId("error").textContent).toBe(
      "Failed to fetch data",
    );
  });

  it("handles network errors and reports a failure", async () => {
    (api.apiClient.get as jest.Mock).mockRejectedValueOnce(
      new Error("network fail"),
    );

    render(<Harness />);

    await waitFor(() =>
      expect(screen.getByTestId("loading").textContent).toBe("false"),
    );
    // hook sets a generic final error message
    expect(screen.getByTestId("error").textContent).toBe(
      "Failed to load admin metrics",
    );
  });

  it("ignores AbortError and does not set an error", async () => {
    const abortErr = new Error("aborted");
    abortErr.name = "AbortError";
    (api.apiClient.get as jest.Mock)
      .mockRejectedValueOnce(abortErr)
      .mockRejectedValueOnce(abortErr)
      .mockRejectedValueOnce(abortErr);

    render(<Harness />);

    await waitFor(() =>
      expect(screen.getByTestId("loading").textContent).toBe("false"),
    );
    expect(screen.getByTestId("error").textContent).toBe("");
  });
});
