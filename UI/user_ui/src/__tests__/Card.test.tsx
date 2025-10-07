import { render, screen } from '@testing-library/react';
import Card from '../components/Card';

const sample = {
  headline: 'Test Headline',
  url: 'https://example.com',
  news_section: 'Tech',
  published_at: new Date().toISOString(),
  summary: 'A short summary'
};

test('Card renders headline and link', () => {
  render(<Card newsEntry={sample as any} />);
  expect(screen.getByText(/Test Headline/i)).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /Read more/i })).toHaveAttribute('href', 'https://example.com');
});
