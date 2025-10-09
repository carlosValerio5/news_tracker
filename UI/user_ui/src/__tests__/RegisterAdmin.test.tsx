// Use the manual mock in src/__mocks__/services/api.ts
jest.mock('../services/api');
import * as api from '../services/api';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RegisterAdmin from '../components/admin/RegisterAdmin';

describe('RegisterAdmin', () => {
  beforeEach(() => {
    (api.apiClient.post as jest.Mock).mockReset();
  });

  it('renders and respects isActive prop', () => {
    const { rerender } = render(<RegisterAdmin isActive={false} />);
    // when inactive, the input should be hidden
    expect(screen.queryByPlaceholderText('admin@example.com')).not.toBeInTheDocument();

    rerender(<RegisterAdmin isActive={true} />);
    expect(screen.getByPlaceholderText('admin@example.com')).toBeInTheDocument();
  });

  it('validates email before submitting', async () => {
    render(<RegisterAdmin isActive={true} />);
    const input = screen.getByPlaceholderText('admin@example.com');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'invalid' } });
    fireEvent.click(button);

    expect(await screen.findByText(/Please enter a valid email address/i)).toBeInTheDocument();
    expect((api.apiClient.post as jest.Mock)).not.toHaveBeenCalled();
  });

  it('submits successfully and clears input/shows success', async () => {
    (api.apiClient.post as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ detail: 'ok' }) });
    render(<RegisterAdmin isActive={true} />);
    const input = screen.getByPlaceholderText('admin@example.com');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'admin@example.com' } });
    fireEvent.click(button);

    await waitFor(() => expect((api.apiClient.post as jest.Mock)).toHaveBeenCalled());
    expect(await screen.findByText(/Registration request submitted|ok/)).toBeInTheDocument();
    expect((screen.getByPlaceholderText('admin@example.com') as HTMLInputElement).value).toBe('');
  });

  it('shows server error when response not ok', async () => {
    (api.apiClient.post as jest.Mock).mockResolvedValue({ ok: false, status: 500, json: async () => ({ detail: 'nope' }) });
    render(<RegisterAdmin isActive={true} />);
    const input = screen.getByPlaceholderText('admin@example.com');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'admin@example.com' } });
    fireEvent.click(button);

    expect(await screen.findByText(/nope|Server returned 500/)).toBeInTheDocument();
  });

  it('handles network error gracefully', async () => {
    (api.apiClient.post as jest.Mock).mockRejectedValue(new Error('network error'));
    render(<RegisterAdmin isActive={true} />);
    const input = screen.getByPlaceholderText('admin@example.com');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'admin@example.com' } });
    fireEvent.click(button);

    expect(await screen.findByText(/network error/i)).toBeInTheDocument();
  });
});
