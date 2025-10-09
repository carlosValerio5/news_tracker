// Use the manual mock in src/__mocks__/services/api.ts
jest.mock('../services/api');
import * as api from '../services/api';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import AdminDashboard from '../core/AdminDashboard';

describe('AdminDashboard', () => {
  beforeEach(() => {
    (api.apiClient.get as jest.Mock).mockReset();
  });

  it('shows loading while checking auth and renders dashboard on success', async () => {
    (api.apiClient.get as jest.Mock).mockResolvedValue({ status: 200 });
    render(
      <MemoryRouter>
        <AdminDashboard />
      </MemoryRouter>,
    );

    expect(screen.getByText(/Checking authentication/i)).toBeInTheDocument();

    await waitFor(() => expect((api.apiClient.get as jest.Mock)).toHaveBeenCalled());
    // after auth success the dashboard heading should be present
    expect(await screen.findByText(/Admin Dashboard/i)).toBeInTheDocument();
  });

  it('redirects to auth-failed on auth failure', async () => {
    (api.apiClient.get as jest.Mock).mockResolvedValue({ status: 401 });

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/dashboard" element={<AdminDashboard />} />
          <Route path="/auth-failed" element={<div>auth-failed</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => expect((api.apiClient.get as jest.Mock)).toHaveBeenCalled());
    expect(await screen.findByText(/auth-failed/i)).toBeInTheDocument();
  });
});
