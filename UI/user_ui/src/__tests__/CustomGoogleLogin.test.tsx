import { render, screen, fireEvent, waitFor } from '@testing-library/react';

// Mock the api module if tests rely on it elsewhere (keeps consistency)
import * as mockApi from '../__mocks__/services/api';
jest.mock('../services/api', () => mockApi);

// Mock react-router's useNavigate so we can assert navigation
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock the Google hook to capture provided callbacks and simulate user action
jest.mock('@react-oauth/google', () => ({
  useGoogleLogin: (opts: any) => {
    // return a function that simulates the login flow by calling onSuccess
    return () => opts.onSuccess({ code: 'test-code' });
  }
}));

import CustomGoogleLogin from '../components/CustomGoogleLogin';

describe('CustomGoogleLogin', () => {
  const origFetch = globalThis.fetch;
  let setItemSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.resetAllMocks();
    // default backend url for tests
    (globalThis as any).__VITE_BACKEND_URL__ = 'http://localhost:9999';
    setItemSpy = jest.spyOn(Storage.prototype, 'setItem');
  });

  afterEach(() => {
  globalThis.fetch = origFetch;
    setItemSpy.mockRestore();
    mockNavigate.mockClear();
  });

  test('successful login posts code, stores token and navigates', async () => {
  globalThis.fetch = jest.fn().mockResolvedValue({ json: async () => ({ token: 'tok-123' }) });

    render(<CustomGoogleLogin />);

    const btn = screen.getByRole('button');
    fireEvent.click(btn);

    // wait for the async code to run
  await waitFor(() => expect(globalThis.fetch).toHaveBeenCalled());

  expect((globalThis.fetch as jest.Mock).mock.calls[0][0]).toBe('http://localhost:9999/auth/google/callback');
    // assert localStorage was set with the returned token
    expect(setItemSpy).toHaveBeenCalledWith('auth_token', 'tok-123');
    // assert navigation to root
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  test('response missing token still attempts to set localStorage and does not crash', async () => {
  globalThis.fetch = jest.fn().mockResolvedValue({ json: async () => ({}) });

    render(<CustomGoogleLogin />);
    fireEvent.click(screen.getByRole('button'));

  await waitFor(() => expect(globalThis.fetch).toHaveBeenCalled());

    // localStorage.setItem should be called with undefined token value
    expect(setItemSpy).toHaveBeenCalledWith('auth_token', undefined);
    // navigation still runs because code calls navigate after setItem
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  test('fetch throws error -> login fails gracefully (no setItem, no navigate)', async () => {
  globalThis.fetch = jest.fn().mockRejectedValue(new Error('network error'));

    render(<CustomGoogleLogin />);
    fireEvent.click(screen.getByRole('button'));

    // wait a tick to allow promise to reject
  await waitFor(() => expect(globalThis.fetch).toHaveBeenCalled());

    // should not set token or navigate
    expect(setItemSpy).not.toHaveBeenCalled();
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
