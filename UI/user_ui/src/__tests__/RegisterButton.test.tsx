import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// keep API mock available for consistency
import * as mockApi from '../__mocks__/services/api';
jest.mock('../services/api', () => mockApi);

import RegisterButton, { ButtonType } from '../components/RegisterButton';

describe('RegisterButton', () => {
  test('renders default primary button as link to /register with default text', () => {
    render(
      <MemoryRouter>
        <RegisterButton />
      </MemoryRouter>
    );

    const link = screen.getByRole('link', { name: /Register/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/register');
    // primary default should include p-3
    expect(link.className).toContain('p-3');
  });

  test('renders secondary variant with smaller styles', () => {
    render(
      <MemoryRouter>
        <RegisterButton type={ButtonType.SECONDARY} />
      </MemoryRouter>
    );

    const link = screen.getByRole('link');
    // secondary should use text-sm and p-2.5 according to component
    expect(link.className).toContain('text-sm');
    expect(link.className).toContain('p-2.5');
  });

  test('accepts custom text and className props', () => {
    render(
      <MemoryRouter>
        <RegisterButton text="Join" className="custom-class" />
      </MemoryRouter>
    );

    const link = screen.getByRole('link', { name: /Join/i });
    expect(link).toBeInTheDocument();
    expect(link.className).toContain('custom-class');
  });
});
