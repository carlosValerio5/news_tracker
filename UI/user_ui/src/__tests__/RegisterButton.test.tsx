import React from 'react';
import { render, screen } from '@testing-library/react';
import RegisterButton from '../components/RegisterButton';
import { BrowserRouter } from 'react-router-dom';

const renderWithRouter = (ui: React.ReactElement) => render(<BrowserRouter>{ui}</BrowserRouter>);

test('renders register button with default text and link', () => {
  renderWithRouter(<RegisterButton />);
  const btn = screen.getByRole('link', { name: /Register/i });
  expect(btn).toBeInTheDocument();
  expect(btn).toHaveAttribute('href', '/register');
});
