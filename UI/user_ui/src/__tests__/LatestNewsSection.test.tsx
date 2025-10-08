import { render, screen } from "@testing-library/react";
import LatestNewsSection from "../core/LatestNewsSection";
import type { NewsEntry } from "../components/Card";

// Mock Card so LatestNewsSection only tests mapping behavior
jest.mock("../components/Card", () => ({
  __esModule: true,
  default: ({ newsEntry }: { newsEntry: NewsEntry }) => (
    <div data-testid="card">{newsEntry.headline}</div>
  ),
}));

test("renders three news cards", () => {
  render(<LatestNewsSection />);
  const cards = screen.getAllByTestId("card");
  expect(cards.length).toBe(3);
});
