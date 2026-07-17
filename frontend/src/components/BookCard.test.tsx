import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { BookCard } from './BookCard';
import type { Book } from '../api/types';

const book: Book = {
  id: 1, title: 'Test Title', author: 1, author_name: 'Test Author', genre: 1, genre_name: 'Fiction',
  publication_year: 2020, cover_url: '', language: 'EN', is_archived: false,
  available_copies: 0, total_copies: 2, average_rating: null,
};

describe('BookCard', () => {
  it('renders title and author', () => {
    render(<MemoryRouter><BookCard book={book} /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: 'Test Title' })).toBeInTheDocument();
    expect(screen.getByText('Test Author')).toBeInTheDocument();
  });

  it('shows an "all copies out" badge when no copies are available', () => {
    render(<MemoryRouter><BookCard book={book} /></MemoryRouter>);
    expect(screen.getByText('All copies out')).toBeInTheDocument();
  });

  it('does not show the badge when copies are available', () => {
    render(<MemoryRouter><BookCard book={{ ...book, available_copies: 1 }} /></MemoryRouter>);
    expect(screen.queryByText('All copies out')).not.toBeInTheDocument();
  });
});
