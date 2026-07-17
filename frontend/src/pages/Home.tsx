import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { client } from '../api/client';
import type { Paginated, Book } from '../api/types';
import { BookCard } from '../components/BookCard';
import { CardSkeletonGrid } from '../components/ui';
import { useAuth } from '../auth/AuthContext';

export default function Home() {
  const { user } = useAuth();
  const { data, isLoading } = useQuery({
    queryKey: ['books', 'home'],
    queryFn: async () => (await client.get<Paginated<Book>>('/books/', { params: { ordering: '-created_at' } })).data,
  });

  return (
    <div className="space-y-12">
      <section className="text-center py-12 border-b border-parchment-300">
        <p className="uppercase tracking-[0.3em] text-brass-600 text-xs mb-3">Est. in code, open to all</p>
        <h1 className="font-serif text-5xl text-ink-900 mb-4">The Reading Room</h1>
        <p className="text-ink-700 max-w-xl mx-auto mb-6">
          Browse the stacks, reserve a hold, and keep track of everything you borrow — a quiet
          corner of the internet for people who love books.
        </p>
        <div className="flex justify-center gap-3">
          <Link to="/catalog" className="px-5 py-2.5 rounded-md bg-forest-700 text-parchment-50 font-semibold hover:bg-forest-800">
            Browse the catalog
          </Link>
          {!user && (
            <Link to="/register" className="px-5 py-2.5 rounded-md bg-parchment-200 text-ink-800 font-semibold border border-parchment-300 hover:bg-parchment-300">
              Become a member
            </Link>
          )}
        </div>
      </section>

      <section>
        <h2 className="font-serif text-2xl mb-4">Newest arrivals</h2>
        {isLoading ? (
          <CardSkeletonGrid />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {data?.results.slice(0, 8).map((book) => <BookCard key={book.id} book={book} />)}
          </div>
        )}
      </section>
    </div>
  );
}
