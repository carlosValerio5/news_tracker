import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import * as mockApi from "../__mocks__/services/api"; // import the mocked apiClient
import type { Article } from "../types/news";
jest.mock("../services/api", () => mockApi);

import Footer from "../components/Footer";
import SearchBar from "../components/SearchBar";
import SubscribeStrip from "../components/SubscribeStrip";
import NewsReport from "../components/NewsReport";
import CustomGoogleLogin from "../components/CustomGoogleLogin";

// mock google login hook
jest.mock("@react-oauth/google", () => ({
  useGoogleLogin: () => jest.fn(),
}));

test("Footer renders copyright text", () => {
  render(<Footer />);
  expect(screen.getByText(/© 2025 News Tracker/i)).toBeInTheDocument();
});

test("SearchBar input accepts text", () => {
  render(<SearchBar />);
  const input = screen.getByPlaceholderText(/Search news.../i);
  fireEvent.change(input, { target: { value: "test" } });
  expect((input as HTMLInputElement).value).toBe("test");
});

test("SubscribeStrip shows register link", () => {
  render(
    <MemoryRouter>
      <SubscribeStrip />
    </MemoryRouter>,
  );
  const links = screen.getAllByRole("link", { name: /Subscribe/i });
  expect(links.length).toBeGreaterThan(0);
});

test("NewsReport mock renders", () => {
  const sample = [
    {
      headline: "H1",
      summary: "S1",
      url: "https://x",
      peak_interest: 10,
      current_interest: 5,
    },
  ];
  render(<NewsReport news={sample as Article[]} />);
  expect(screen.getByText("H1")).toBeInTheDocument();
  expect(screen.getByText("S1")).toBeInTheDocument();
  expect(
    screen.getByText(/Peak Interest: 10 \| Current Interest: 5/i),
  ).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Read more/i })).toHaveAttribute(
    "href",
    "https://x",
  );
});

test("CustomGoogleLogin renders button", () => {
  render(
    <MemoryRouter>
      <CustomGoogleLogin />
    </MemoryRouter>,
  );
  expect(screen.getByRole("button")).toBeInTheDocument();
});
