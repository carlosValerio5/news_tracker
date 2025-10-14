jest.mock("../services/api");

import { render, screen } from "@testing-library/react";
import { apiClient } from "../services/api";
import RecentActivity from "../components/admin/RecentActivity";

describe("RecentActivity", () => {
  beforeEach(() => {
    // Ensure the mocked apiClient returns the shape RecentActivity expects
    (apiClient.get as jest.Mock).mockResolvedValue({
      status: 200,
      ok: true,
      data: {
        activities: [
          { description: "promoted to admin" },
          { description: "Daily trends job completed successfully" },
        ],
      },
    });
  });

  it("renders heading and list items", async () => {
    render(<RecentActivity />);

    // Wait for the async effect to update state and render the items
    expect(await screen.findByText("Recent Activity")).toBeInTheDocument();
    expect(await screen.findByText(/promoted to admin/i)).toBeInTheDocument();
    expect(
      await screen.findByText(/Daily trends job completed successfully/i),
    ).toBeInTheDocument();
  });
});
