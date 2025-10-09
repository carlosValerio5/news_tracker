import { render, screen } from '@testing-library/react';
import RecentActivity from '../components/admin/RecentActivity';

describe('RecentActivity', () => {
  it('renders heading and list items', () => {
    render(<RecentActivity />);
    expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    expect(screen.getByText(/promoted to admin/i)).toBeInTheDocument();
    expect(screen.getByText(/Daily trends job completed successfully/i)).toBeInTheDocument();
  });
});
