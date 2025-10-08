import { render, screen } from "@testing-library/react";
import Card from "../components/Card";
import type { NewsEntry } from "../components/Card";

const sample = {
  headline: "Test Headline",
  url: "https://example.com",
  summary: "A short summary",
  peak_interest: 100,
  current_interest: 20,
};

test("Card renders headline and link", () => {
  render(<Card newsEntry={sample as NewsEntry} />);
  expect(screen.getByText(/Test Headline/i)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Read more/i })).toHaveAttribute(
    "href",
    "https://example.com",
  );
});
