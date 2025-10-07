export const API_BASE = '';

const sampleArticles = [
  {
    headline: 'Headline 1',
    summary: 'Summary of the first news article.',
    url: 'https://example.com/news1',
    peak_interest: 100,
    current_interest: 80,
    news_section: 'World'
  },
  {
    headline: 'Headline 2',
    summary: 'Summary of the second news article.',
    url: 'https://example.com/news2',
    peak_interest: 80,
    current_interest: 50,
    news_section: 'Tech'
  }
];

const makeResponse = (payload: any) => ({
  ok: true,
  status: 200,
  json: async () => payload,
});

export const apiClient = {
  get: jest.fn((endpoint: string) => {
    if (endpoint === '/news-report') {
      return Promise.resolve(makeResponse(sampleArticles));
    }
    return Promise.resolve(makeResponse({}));
  }),
  post: jest.fn(() => Promise.resolve(makeResponse({}))),
  put: jest.fn(() => Promise.resolve(makeResponse({}))),
  delete: jest.fn(() => Promise.resolve(makeResponse({}))),
};
