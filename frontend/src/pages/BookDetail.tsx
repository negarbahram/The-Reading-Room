import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../api/client';
import type { BookDetail as BookDetailType, RecommendedBook, Review } from '../api/types';
import { Button, Card, EmptyState, StarRating, StatusBadge, inputClass } from '../components/ui';
import { BookCard } from '../components/BookCard';
import { BookCover } from '../components/BookCover';
import { useAuth } from '../auth/AuthContext';
import { useToast } from '../components/Toast';

export default function BookDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data: book, isLoading } = useQuery({
    queryKey: ['book', id],
    queryFn: async () => (await client.get<BookDetailType>(`/books/${id}/`)).data,
  });

  const { data: related } = useQuery({
    queryKey: ['book', id, 'related'],
    queryFn: async () => (await client.get<RecommendedBook[]>(`/books/${id}/related/`)).data,
    enabled: !!id,
  });

  const { data: reviews } = useQuery({
    queryKey: ['reviews', id],
    queryFn: async () => (await client.get<{ results: Review[] }>('/reviews/', { params: { book: id } })).data.results,
    enabled: !!id && !!user,
  });

  const requestLoan = useMutation({
    mutationFn: async () => client.post('/loan-requests/', { book: id }),
    onSuccess: () => {
      showToast('Loan request submitted. An admin will review it.', 'success');
      qc.invalidateQueries({ queryKey: ['book', id] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  const reserve = useMutation({
    mutationFn: async () => client.post('/reservations/', { book: id }),
    onSuccess: () => showToast('You have been added to the waitlist.', 'success'),
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  if (isLoading) return <p className="text-center py-16 text-ink-700">Loading…</p>;
  if (!book) return <EmptyState title="Book not found" />;

  return (
    <div className="space-y-10">
      <div className="grid md:grid-cols-[280px_1fr] gap-8">
        <div className="aspect-[2/3] bg-walnut-700 rounded-lg flex items-center justify-center shadow-book overflow-hidden">
          <BookCover coverUrl={book.cover_url} title={book.title} className="rounded-lg" />
        </div>
        <div>
          <h1 className="font-serif text-3xl mb-1">{book.title}</h1>
          <p className="text-ink-700 mb-2">by {book.author_name} · {book.genre_name} · {book.publication_year}</p>
          <StarRating rating={book.average_rating} />
          {book.description && <p className="mt-4 text-ink-800 leading-relaxed">{book.description}</p>}
          <dl className="grid grid-cols-2 gap-2 mt-4 text-sm text-ink-700">
            {book.isbn && <><dt className="font-semibold">ISBN</dt><dd>{book.isbn}</dd></>}
            {book.publisher && <><dt className="font-semibold">Publisher</dt><dd>{book.publisher}</dd></>}
            <dt className="font-semibold">Language</dt><dd>{book.language}</dd>
            <dt className="font-semibold">Availability</dt>
            <dd>{book.available_copies} of {book.total_copies} copies available</dd>
          </dl>

          <div className="mt-6 flex gap-3">
            {!user && (
              <Link to="/login" className="px-4 py-2 rounded-md bg-forest-700 text-parchment-50 font-semibold">
                Log in to borrow
              </Link>
            )}
            {user && book.available_copies > 0 && (
              <Button onClick={() => requestLoan.mutate()} disabled={requestLoan.isPending}>
                {requestLoan.isPending ? 'Submitting…' : 'Request to borrow'}
              </Button>
            )}
            {user && book.available_copies === 0 && (
              <Button variant="secondary" onClick={() => reserve.mutate()} disabled={reserve.isPending}>
                {reserve.isPending ? 'Joining waitlist…' : 'Join waitlist'}
              </Button>
            )}
          </div>
        </div>
      </div>

      {related && related.length > 0 && (
        <section>
          <h2 className="font-serif text-2xl mb-4">You might also like</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {related.map((b) => (
              <div key={b.id}>
                <BookCard book={b} />
                <p className="text-xs text-ink-700 mt-1 italic">{b.reason}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="font-serif text-2xl mb-4">Reviews</h2>
        {!user && <p className="text-ink-700">Log in to read and write reviews.</p>}
        {user && <ReviewsSection bookId={book.id} reviews={reviews ?? []} />}
      </section>
    </div>
  );
}

function ReviewsSection({ bookId, reviews }: { bookId: number; reviews: Review[] }) {
  const { user } = useAuth();
  const { showToast } = useToast();
  const qc = useQueryClient();
  const myReview = reviews.find((r) => r.member === user?.id);
  const [rating, setRating] = useState(myReview?.rating ?? 5);
  const [comment, setComment] = useState(myReview?.comment ?? '');
  const [showForm, setShowForm] = useState(false);

  const saveReview = useMutation({
    mutationFn: async () => {
      if (myReview) {
        return client.patch(`/reviews/${myReview.id}/`, { rating, comment });
      }
      return client.post('/reviews/', { book: bookId, rating, comment });
    },
    onSuccess: () => {
      showToast('Review saved.', 'success');
      setShowForm(false);
      qc.invalidateQueries({ queryKey: ['reviews', String(bookId)] });
      qc.invalidateQueries({ queryKey: ['book', String(bookId)] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  const otherReviews = reviews.filter((r) => r.member !== user?.id);

  return (
    <div className="space-y-4">
      {!myReview && !showForm && (
        <Button variant="secondary" onClick={() => setShowForm(true)}>Write a review</Button>
      )}
      {myReview && !showForm && (
        <Card>
          <p className="text-xs uppercase tracking-wide text-ink-700 mb-1">Your review</p>
          <StarRating rating={myReview.rating} />
          <p className="mt-2">{myReview.comment}</p>
          {!myReview.is_approved && <p className="text-xs text-brass-600 mt-1">Pending moderation</p>}
          <Button variant="secondary" className="mt-3" onClick={() => setShowForm(true)}>Edit review</Button>
        </Card>
      )}
      {showForm && (
        <Card>
          <label className="block mb-3">
            <span className="text-sm font-semibold">Rating</span>
            <select className={inputClass} value={rating} onChange={(e) => setRating(Number(e.target.value))}>
              {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{n} star{n > 1 ? 's' : ''}</option>)}
            </select>
          </label>
          <label className="block mb-3">
            <span className="text-sm font-semibold">Comment</span>
            <textarea className={inputClass} rows={3} value={comment} onChange={(e) => setComment(e.target.value)} />
          </label>
          <div className="flex gap-2">
            <Button onClick={() => saveReview.mutate()} disabled={saveReview.isPending}>
              {saveReview.isPending ? 'Saving…' : 'Save review'}
            </Button>
            <Button variant="secondary" onClick={() => setShowForm(false)}>Cancel</Button>
          </div>
          <p className="text-xs text-ink-700 mt-2">
            Note: you can only review books you have borrowed.
          </p>
        </Card>
      )}

      {otherReviews.length === 0 ? (
        <p className="text-ink-700 text-sm">No other reviews yet.</p>
      ) : (
        <ul className="space-y-3">
          {otherReviews.map((r) => (
            <li key={r.id} className="border-b border-parchment-300 pb-3">
              <div className="flex items-center gap-2">
                <StarRating rating={r.rating} />
                <span className="text-xs text-ink-700">{r.member_email}</span>
                {!r.is_approved && <StatusBadge status="PENDING" />}
              </div>
              {r.comment && <p className="text-sm text-ink-800 mt-1">{r.comment}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
