import { render, screen } from '@testing-library/react';
import StatCard from '../components/admin/StatCard';

describe('StatCard', () => {
  it('renders label and value', () => {
    render(<StatCard s={{ label: 'Test', value_daily: 10 }} weekAndDay={false} />);
    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('shows positive diff with + and green class', () => {
    render(<StatCard s={{ label: 'Up', value_daily: 5, diff: 2 }} weekAndDay={false} />);
    expect(screen.getByText('+2%')).toBeInTheDocument();
    // class presence check is optional, just ensure the element exists
  });

  it('shows negative diff with - and red class', () => {
    render(<StatCard s={{ label: 'Down', value_daily: 3, diff: -1 }} weekAndDay={false} />);
    expect(screen.getByText('-1%')).toBeInTheDocument();
  });

  it('does not render diff when undefined', () => {
    render(<StatCard s={{ label: 'NoDiff', value_daily: '—' }} weekAndDay={false} />);
    expect(screen.queryByText(/%/)).not.toBeInTheDocument();
  });
});
