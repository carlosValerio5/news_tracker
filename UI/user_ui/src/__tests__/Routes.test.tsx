import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import * as mockApi from '../__mocks__/services/api'; // import the mocked apiClient
jest.mock('../services/api', () => mockApi);

jest.mock('../core/NewsCardsSection', () => ({
  __esModule: true,
  default: () => <h1 className='text-3xl font-bold ml-5 md:ml-10 lg:ml-15'>Explore</h1>
}));
jest.mock('../components/NewsReport', () => ({
  __esModule: true,
  default: () => <div data-testid="news-report-mock">news-report-mock</div>
}));

test('navigates to news page', async () => {
  const { router: appRouter } = await import('../routes/routes');
  const memoryRouter = createMemoryRouter(appRouter.routes, { initialEntries: ['/news'] });
  render(<RouterProvider router={memoryRouter} />);
  const newsHeader = await screen.findByRole('heading', { name: /Explore/i });
  expect(newsHeader).toBeInTheDocument();
});
