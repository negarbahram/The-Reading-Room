import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../../api/client';
import type { Book, Paginated } from '../../api/types';
import { Button, EmptyState, Pagination, StatusBadge, inputClass } from '../../components/ui';
import { useToast } from '../../components/Toast';

export default function AdminBooks() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const { showToast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'books', search, page],
    queryFn: async () => (await client.get<Paginated<Book>>('/books/', { params: { title: search, page } })).data,
  });

  const archive = useMutation({
    mutationFn: async (id: number) => client.delete(`/books/${id}/`),
    onSuccess: () => {
      showToast('Book archived.', 'success');
      qc.invalidateQueries({ queryKey: ['admin', 'books'] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <h1 className="font-serif text-3xl">Books</h1>
        <Link to="/admin/books/new" className="px-4 py-2 rounded-md bg-forest-700 text-parchment-50 font-semibold text-sm">
          + Add book
        </Link>
      </div>
      <input
        className={`${inputClass} max-w-xs mb-4`} placeholder="Search by title…"
        value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
      />
      {isLoading && <p className="text-ink-700">Loading…</p>}
      {data && data.results.length === 0 && <EmptyState title="No books found" />}
      {data && data.results.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-parchment-300">
                <th className="py-2 pr-4">Title</th>
                <th className="py-2 pr-4">Author</th>
                <th className="py-2 pr-4">Genre</th>
                <th className="py-2 pr-4">Copies</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2 pr-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((book) => (
                <tr key={book.id} className="border-b border-parchment-200">
                  <td className="py-2 pr-4 font-serif">{book.title}</td>
                  <td className="py-2 pr-4">{book.author_name}</td>
                  <td className="py-2 pr-4">{book.genre_name}</td>
                  <td className="py-2 pr-4">{book.available_copies}/{book.total_copies}</td>
                  <td className="py-2 pr-4"><StatusBadge status={book.is_archived ? 'ARCHIVED' : 'AVAILABLE'} /></td>
                  <td className="py-2 pr-4 flex gap-2">
                    <Link to={`/admin/books/${book.id}`} className="text-forest-700 font-semibold underline">Edit</Link>
                    {!book.is_archived && (
                      <Button variant="danger" onClick={() => archive.mutate(book.id)} className="!px-2 !py-1 text-xs">
                        Archive
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {data && (
        <Pagination count={data.count} next={data.next} previous={data.previous}
          onNext={() => setPage((p) => p + 1)} onPrevious={() => setPage((p) => Math.max(1, p - 1))} />
      )}
    </div>
  );
}
