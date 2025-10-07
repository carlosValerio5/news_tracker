import { render, screen } from '@testing-library/react';
import * as mockApi from '../__mocks__/services/api';

// Tell Jest to use the manual mock for ../services/api
jest.mock('../services/api', () => mockApi);

import NewsCardsSection from '../core/NewsCardsSection';

// NewsCardsSection will call the mocked apiClient in __mocks__/services/api.ts
// which returns two sample articles. We expect at least one card to render.

test('NewsCardsSection renders mocked articles', async () => {
  render(<NewsCardsSection />);
  const cards = await screen.findAllByText(/Headline/i);
  expect(cards.length).toBeGreaterThanOrEqual(1);
});
