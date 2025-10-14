import { render, screen } from "@testing-library/react";
import LatestNewsSection from "../core/LatestNewsSection";
import type { NewsEntry } from "../components/Card";
import type { ApiResponse } from "../services/api";

// mock the api module (hoisted) and the Card component
jest.mock("../services/api");
jest.mock("../components/Card", () => ({
  __esModule: true,
  default: ({ newsEntry }: { newsEntry: NewsEntry }) => (
    <div data-testid="card">{newsEntry.headline}</div>
  ),
}));

import * as api from "../services/api";

const sampleNews: NewsEntry[] = [
  {
    url: "url-1",
    headline: "One",
    summary: "s1",
    peak_interest: 10,
    current_interest: 5,
  },
  {
    url: "url-2",
    headline: "Two",
    summary: "s2",
    peak_interest: 8,
    current_interest: 3,
  },
  {
    url: "url-3",
    headline: "Three",
    summary: "s3",
    peak_interest: 6,
    current_interest: 2,
  },
];

beforeEach(() => {
  jest.resetAllMocks();

  // strongly-typed mock for apiClient.get
  const mockedGet = api.apiClient.get as jest.MockedFunction<
    (endpoint: string, init?: RequestInit) => Promise<ApiResponse<NewsEntry[]>>
  >;

  mockedGet.mockResolvedValue({
    ok: true,
    status: 200,
    data: sampleNews,
  });
});

test("renders three news cards", async () => {
  render(<LatestNewsSection />);
  const cards = await screen.findAllByTestId("card");
  expect(cards.length).toBe(3);
});
