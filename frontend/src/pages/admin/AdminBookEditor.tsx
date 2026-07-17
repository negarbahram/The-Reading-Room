import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../../api/client';
import type { Author, BookCopy, BookDetail, CopyStatus, Genre, Paginated } from '../../api/types';
import { BookCover } from '../../components/BookCover';
import { Button, Card, Field, StatusBadge, inputClass } from '../../components/ui';
import { useToast } from '../../components/Toast';

const COPY_STATUSES: CopyStatus[] = ['AVAILABLE', 'ON_LOAN', 'HELD', 'LOST', 'DAMAGED', 'ARCHIVED'];

const emptyForm = {
  title: '', author: '', genre: '', publication_year: new Date().getFullYear(),
  isbn: '', publisher: '', description: '', language: 'EN', cover_url: '', shelf_location: '',
};

export default function AdminBookEditor() {
  const { id } = useParams();
  const isNew = !id || id === 'new';
  const navigate = useNavigate();
  const { showToast } = useToast();
  const qc = useQueryClient();
  const [form, setForm] = useState(emptyForm);

  const { data: book } = useQuery({
    queryKey: ['admin', 'book', id],
    queryFn: async () => (await client.get<BookDetail>(`/books/${id}/`)).data,
    enabled: !isNew,
  });

  const { data: genres } = useQuery({
    queryKey: ['genres'],
    queryFn: async () => (await client.get<Paginated<Genre> | Genre[]>('/genres/')).data,
  });
  const { data: authors } = useQuery({
    queryKey: ['authors'],
    queryFn: async () => (await client.get<Paginated<Author> | Author[]>('/authors/')).data,
  });
  const genreList = Array.isArray(genres) ? genres : genres?.results ?? [];
  const authorList = Array.isArray(authors) ? authors : authors?.results ?? [];

  useEffect(() => {
    if (book) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- syncing the form when a different book loads
      setForm({
        title: book.title, author: String(book.author), genre: String(book.genre),
        publication_year: book.publication_year, isbn: book.isbn ?? '', publisher: book.publisher,
        description: book.description, language: book.language, cover_url: book.cover_url,
        shelf_location: book.shelf_location,
      });
    }
  }, [book]);

  const save = useMutation({
    mutationFn: async () => {
      const payload = { ...form, author: Number(form.author), genre: Number(form.genre) };
      if (isNew) return client.post<BookDetail>('/books/', payload);
      return client.patch<BookDetail>(`/books/${id}/`, payload);
    },
    onSuccess: (res) => {
      showToast('Book saved.', 'success');
      qc.invalidateQueries({ queryKey: ['admin', 'books'] });
      if (isNew) navigate(`/admin/books/${res.data.id}`, { replace: true });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div className="max-w-3xl">
      <h1 className="font-serif text-3xl mb-6">{isNew ? 'Add book' : 'Edit book'}</h1>
      <Card className="mb-8">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Title"><input className={inputClass} value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></Field>
          <Field label="Publication year">
            <input type="number" className={inputClass} value={form.publication_year}
              onChange={(e) => setForm({ ...form, publication_year: Number(e.target.value) })} />
          </Field>
          <Field label="Author">
            <select className={inputClass} value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })}>
              <option value="">Select…</option>
              {authorList.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </Field>
          <Field label="Genre">
            <select className={inputClass} value={form.genre} onChange={(e) => setForm({ ...form, genre: e.target.value })}>
              <option value="">Select…</option>
              {genreList.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
            </select>
          </Field>
          <Field label="ISBN"><input className={inputClass} value={form.isbn} onChange={(e) => setForm({ ...form, isbn: e.target.value })} /></Field>
          <Field label="Publisher"><input className={inputClass} value={form.publisher} onChange={(e) => setForm({ ...form, publisher: e.target.value })} /></Field>
          <Field label="Language">
            <select className={inputClass} value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })}>
              <option value="EN">English</option><option value="FR">French</option>
              <option value="ES">Spanish</option><option value="AR">Arabic</option><option value="OTHER">Other</option>
            </select>
          </Field>
          <Field label="Shelf location"><input className={inputClass} value={form.shelf_location} onChange={(e) => setForm({ ...form, shelf_location: e.target.value })} /></Field>
          <Field label="Cover URL">
            <div className="flex items-center gap-3">
              <input className={inputClass} value={form.cover_url} onChange={(e) => setForm({ ...form, cover_url: e.target.value })} />
              <div className="w-12 h-16 shrink-0 bg-walnut-700 rounded overflow-hidden flex items-center justify-center">
                <BookCover coverUrl={form.cover_url} title={form.title || '—'} className="text-[8px]" />
              </div>
            </div>
          </Field>
        </div>
        <Field label="Description">
          <textarea className={inputClass} rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </Field>
        <Button onClick={() => save.mutate()} disabled={save.isPending || !form.title || !form.author || !form.genre}>
          {save.isPending ? 'Saving…' : 'Save book'}
        </Button>
      </Card>

      {!isNew && book && <CopiesManager bookId={book.id} copies={book.copies} />}
    </div>
  );
}

function CopiesManager({ bookId, copies }: { bookId: number; copies: BookCopy[] }) {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const [barcode, setBarcode] = useState('');

  const addCopy = useMutation({
    mutationFn: async () => client.post(`/books/${bookId}/copies/`, { barcode, status: 'AVAILABLE' }),
    onSuccess: () => {
      setBarcode('');
      qc.invalidateQueries({ queryKey: ['admin', 'book', String(bookId)] });
      showToast('Copy added.', 'success');
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  const updateCopy = useMutation({
    mutationFn: async ({ copyId, status }: { copyId: number; status: CopyStatus }) =>
      client.patch(`/book-copies/${copyId}/`, { status }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin', 'book', String(bookId)] });
      showToast('Copy updated.', 'success');
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div>
      <h2 className="font-serif text-2xl mb-4">Physical copies</h2>
      <Card>
        <div className="flex gap-2 mb-4">
          <input className={inputClass} placeholder="Barcode" value={barcode} onChange={(e) => setBarcode(e.target.value)} />
          <Button variant="secondary" disabled={!barcode || addCopy.isPending} onClick={() => addCopy.mutate()}>
            Add copy
          </Button>
        </div>
        <ul className="divide-y divide-parchment-200">
          {copies.map((copy) => (
            <li key={copy.id} className="py-2 flex items-center justify-between gap-3 flex-wrap">
              <span className="font-mono text-sm">{copy.barcode}</span>
              <div className="flex items-center gap-2">
                <StatusBadge status={copy.status} />
                <select
                  className={`${inputClass} !w-auto text-xs py-1`}
                  value={copy.status}
                  onChange={(e) => updateCopy.mutate({ copyId: copy.id, status: e.target.value as CopyStatus })}
                >
                  {COPY_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </li>
          ))}
          {copies.length === 0 && <p className="text-sm text-ink-700 py-2">No physical copies yet.</p>}
        </ul>
      </Card>
    </div>
  );
}
