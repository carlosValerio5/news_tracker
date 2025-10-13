import type { Article } from "../../types/news";

// Local ApiResponse shape to mirror the real client used in the app
type ApiResponse<T> = {
  status: number;
  data: T | null;
  ok: boolean;
};

export const API_BASE = "";

const sampleArticles: Article[] = [
  {
    headline: "Headline 1",
    summary: "Summary of the first news article.",
    url: "https://example.com/news1",
    peak_interest: 100,
    current_interest: 80,
    news_section: "World",
  },
  {
    headline: "Headline 2",
    summary: "Summary of the second news article.",
    url: "https://example.com/news2",
    peak_interest: 80,
    current_interest: 50,
    news_section: "Tech",
  },
];

const makeResponseLike = <T>(payload: T, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: async () => payload,
});

export const apiClient = {
  // get returns a typed ApiResponse<T> in the real client
  get: jest.fn(async (endpoint: string): Promise<ApiResponse<unknown>> => {
    if (endpoint === "/news-report") {
      return { ok: true, status: 200, data: sampleArticles };
    }

    if (endpoint === "/admin/recent-activities") {
      return {
        ok: true,
        status: 200,
        data: {
          activities: [
            { description: "promoted to admin" },
            { description: "Daily trends job completed successfully" },
          ],
        },
      };
    }

    return { ok: true, status: 200, data: [] };
  }),

  // post/put/delete return fetch Response-like objects in many tests
  post: jest.fn(async () =>
    Promise.resolve(makeResponseLike({ ok: true, status: 200, data: null })),
  ),
  put: jest.fn(async () =>
    Promise.resolve(makeResponseLike({ ok: true, status: 200, data: null })),
  ),
  delete: jest.fn(async () =>
    Promise.resolve(makeResponseLike({ ok: true, status: 200, data: null })),
  ),
};
