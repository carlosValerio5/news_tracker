import { render, screen } from '@testing-library/react';
import LatestNewsSection from '../core/LatestNewsSection';

// Mock Card so LatestNewsSection only tests mapping behavior
jest.mock('../components/Card', () => ({
  __esModule: true,
  default: ({ newsEntry }: any) => <div data-testid="card">{newsEntry.headline}</div>
}));

test('renders three news cards', () => {
  render(<LatestNewsSection />);
  const cards = screen.getAllByTestId('card');
  expect(cards.length).toBe(3);
});
