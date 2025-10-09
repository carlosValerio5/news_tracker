// Use the manual mock in src/__mocks__/services/api.ts
jest.mock('../services/api');
import * as api from '../services/api';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AddEmailRecipient from '../components/admin/AddEmailRecipient';

describe('AddEmailRecipient', () => {
  beforeEach(() => {
    (api.apiClient.post as jest.Mock).mockReset();
  });

  it('validates email before submitting', async () => {
    render(<AddEmailRecipient isActive={true} />);
    const input = screen.getByPlaceholderText('email@example.com');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'invalid' } });
    fireEvent.click(button);

    expect(await screen.findByText(/Please enter a valid email address/i)).toBeInTheDocument();
  expect((api.apiClient.post as jest.Mock)).not.toHaveBeenCalled();
  });

  it('submits successfully and shows success message', async () => {
    (api.apiClient.post as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ detail: 'ok' }) });
    render(<AddEmailRecipient isActive={true} />);
    const input = screen.getByPlaceholderText('email@example.com');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'email@example.com' } });
    fireEvent.click(button);

  await waitFor(() => expect((api.apiClient.post as jest.Mock)).toHaveBeenCalled());
  expect(await screen.findByText(/Registration request submitted|ok/)).toBeInTheDocument();
  });

  it('shows server error when response not ok', async () => {
    (api.apiClient.post as jest.Mock).mockResolvedValue({ ok: false, status: 500, json: async () => ({ detail: 'nope' }) });
    render(<AddEmailRecipient isActive={true} />);
    const input = screen.getByPlaceholderText('email@example.com');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'email@example.com' } });
    fireEvent.click(button);

    expect(await screen.findByText(/nope|Server returned 500/)).toBeInTheDocument();
  });

  it('handles network errors gracefully', async () => {
    (api.apiClient.post as jest.Mock).mockRejectedValue(new Error('network lost'));
    render(<AddEmailRecipient isActive={true} />);
    const input = screen.getByPlaceholderText('email@example.com');
    const button = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'email@example.com' } });
    fireEvent.click(button);

    expect(await screen.findByText(/network lost/i)).toBeInTheDocument();
  });

  it('allows changing the summary time select', () => {
    render(<AddEmailRecipient isActive={true} />);
    const select = screen.getByLabelText(/Summary send time/i) as HTMLSelectElement;
    expect(select.value).toBe('08:00');
    fireEvent.change(select, { target: { value: '14:00' } });
    expect(select.value).toBe('14:00');
  });
});
