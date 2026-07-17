import { Link } from 'react-router-dom';
import type { Book } from '../api/types';
import { BookCover } from './BookCover';
import { StarRating } from './ui';

export function BookCard({ book }: { book: Book }) {
  return (
    <Link
      to={`/catalog/${book.id}`}
      className="group flex flex-col rounded-lg overflow-hidden border border-parchment-300 bg-parchment-50 shadow-book hover:-translate-y-1 transition-transform duration-200"
    >
      <div className="aspect-[2/3] bg-walnut-700 flex items-center justify-center relative overflow-hidden">
        <BookCover coverUrl={book.cover_url} title={book.title} />
        {book.available_copies === 0 && (
          <span className="absolute top-2 right-2 bg-red-800 text-parchment-50 text-xs px-2 py-0.5 rounded font-semibold">
            All copies out
          </span>
        )}
      </div>
      <div className="p-3 flex-1 flex flex-col gap-1">
        <h3 className="font-serif text-base leading-tight group-hover:underline">{book.title}</h3>
        <p className="text-sm text-ink-700">{book.author_name}</p>
        <p className="text-xs text-ink-700">{book.genre_name} · {book.publication_year}</p>
        <div className="mt-auto pt-2 flex flex-col gap-1">
          <StarRating rating={book.average_rating} />
          <span className="text-xs text-ink-700">{book.available_copies}/{book.total_copies} available</span>
        </div>
      </div>
    </Link>
  );
}
