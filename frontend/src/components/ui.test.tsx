import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StarRating, StatusBadge } from './ui';

describe('StatusBadge', () => {
  it('renders the status text with underscores replaced', () => {
    render(<StatusBadge status="PENDING_PAYMENT" />);
    expect(screen.getByText('PENDING PAYMENT')).toBeInTheDocument();
  });
});

describe('StarRating', () => {
  it('shows a fallback message when there is no rating', () => {
    render(<StarRating rating={null} />);
    expect(screen.getByText('No ratings yet')).toBeInTheDocument();
  });

  it('shows the numeric rating when present', () => {
    render(<StarRating rating={4.2} />);
    expect(screen.getByText('(4.2)')).toBeInTheDocument();
  });
});
