import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Create mock references
const mockTitleBar = jest.fn();
const mockCustomGoogleLogin = jest.fn();

jest.mock('../components/TitleBar', () => ({
  __esModule: true,
  default: mockTitleBar
}));

jest.mock('../components/CustomGoogleLogin', () => ({
  __esModule: true,
  default: mockCustomGoogleLogin
}));



import LoginPage from '../core/LoginPage';

describe('LoginPage', () => {
    beforeEach(() => {
        // Reset and set default implementations
        mockTitleBar.mockImplementation(() => <div data-testid="mock-titlebar">TitleBar</div>);
        mockCustomGoogleLogin.mockImplementation(() => <button data-testid="mock-google-login">Sign in</button>);
    });

  test('renders heading, description, mocked TitleBar and Google login, and register link', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    // Heading
    expect(screen.getByRole('heading', { name: /Login/i })).toBeInTheDocument();

    // Description
    expect(screen.getByText(/Welcome back! Please login with your Google account./i)).toBeInTheDocument();

    // TitleBar mock
    expect(screen.getByTestId('mock-titlebar')).toBeInTheDocument();

    // Google login mock
    expect(screen.getByTestId('mock-google-login')).toBeInTheDocument();

    // Register link
    const link = screen.getByRole('link', { name: /Register/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/register');
  });

  test('renders without Google login (edge case: component returns null)', async () => {
      mockCustomGoogleLogin.mockImplementation(() => null);


      render(
          <MemoryRouter>
              <LoginPage />
          </MemoryRouter>
      );

      // Heading and paragraph should still render
      expect(screen.getByRole('heading', { name: /Login/i })).toBeInTheDocument();
      expect(screen.getByText(/Welcome back! Please login with your Google account./i)).toBeInTheDocument();

      // The google login mock returns null so it should not be in the document
      expect(screen.queryByTestId('mock-google-login')).not.toBeInTheDocument();
    });
});
