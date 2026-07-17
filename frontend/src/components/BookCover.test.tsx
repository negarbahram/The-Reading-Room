import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { BookCover } from './BookCover';

describe('BookCover', () => {
  it('renders the image when a cover URL is present', () => {
    render(<BookCover coverUrl="https://covers.openlibrary.org/b/id/12345-L.jpg" title="Test Book" />);
    const img = screen.getByRole('img', { name: 'Cover of Test Book' });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', 'https://covers.openlibrary.org/b/id/12345-L.jpg');
  });

  it('shows a typographic fallback when cover_url is empty', () => {
    render(<BookCover coverUrl="" title="Test Book" />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(screen.getByText('Test Book')).toBeInTheDocument();
  });

  it('falls back to the title when the remote image fails to load', () => {
    render(<BookCover coverUrl="https://broken.example/cover.jpg" title="Test Book" />);
    const img = screen.getByRole('img', { name: 'Cover of Test Book' });
    fireEvent.error(img);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
    expect(screen.getByText('Test Book')).toBeInTheDocument();
  });
});
