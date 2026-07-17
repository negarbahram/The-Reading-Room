import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { client } from '../api/client';
import type { Paginated, Book } from '../api/types';
import { BookCard } from '../components/BookCard';
import { CardSkeletonGrid, EmptyState, Pagination, inputClass } from '../components/ui';

export default function Catalog() {
  const [filters, setFilters] = useState({ title: '', author: '', genre: '', publication_year: '' });
  const [page, setPage] = useState(1);

  const params: Record<string, string | number> = { page };
  if (filters.title) params.title = filters.title;
  if (filters.author) params.author = filters.author;
  if (filters.genre) params.genre = filters.genre;
  if (filters.publication_year) params.publication_year = filters.publication_year;

  const { data, isLoading, isError } = useQuery({
    queryKey: ['books', filters, page],
    queryFn: async () => (await client.get<Paginated<Book>>('/books/', { params })).data,
  });

  const updateFilter = (key: keyof typeof filters, value: string) => {
    setFilters((f) => ({ ...f, [key]: value }));
    setPage(1);
  };

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Catalog</h1>
      <form
        className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8 bg-parchment-50 border border-parchment-300 rounded-lg p-4"
        onSubmit={(e) => e.preventDefault()}
        role="search"
        aria-label="Book search and filters"
      >
        <label className="block">
          <span className="text-xs font-semibold text-ink-800">Title</span>
          <input className={inputClass} value={filters.title} onChange={(e) => updateFilter('title', e.target.value)} />
        </label>
        <label className="block">
          <span className="text-xs font-semibold text-ink-800">Author</span>
          <input className={inputClass} value={filters.author} onChange={(e) => updateFilter('author', e.target.value)} />
        </label>
        <label className="block">
          <span className="text-xs font-semibold text-ink-800">Genre</span>
          <input className={inputClass} value={filters.genre} onChange={(e) => updateFilter('genre', e.target.value)} />
        </label>
        <label className="block">
          <span className="text-xs font-semibold text-ink-800">Publication year</span>
          <input type="number" className={inputClass} value={filters.publication_year}
            onChange={(e) => updateFilter('publication_year', e.target.value)} />
        </label>
      </form>

      {isLoading && <CardSkeletonGrid count={8} />}
      {isError && <EmptyState title="Could not load the catalog" hint="Please try again shortly." />}
      {data && data.results.length === 0 && (
        <EmptyState title="No books match your search" hint="Try broadening your filters." />
      )}
      {data && data.results.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {data.results.map((book) => <BookCard key={book.id} book={book} />)}
        </div>
      )}
      {data && (
        <Pagination
          count={data.count} next={data.next} previous={data.previous}
          onNext={() => setPage((p) => p + 1)} onPrevious={() => setPage((p) => Math.max(1, p - 1))}
        />
      )}
    </div>
  );
}
