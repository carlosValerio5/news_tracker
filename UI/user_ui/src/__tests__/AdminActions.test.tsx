import { render, screen } from '@testing-library/react';
import AdminActions from '../components/admin/AdminActions';

describe('AdminActions', () => {
  it('renders action buttons and RegisterAdmin placeholder', () => {
    render(<AdminActions setVisible={() => {}} />);
    expect(screen.getByText(/Admin Actions/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Register Admin/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Add Email Recipient/i })).toBeInTheDocument();
  });
});
