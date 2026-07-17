import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../api/client';
import type { Author, Genre, MemberInterest, Paginated } from '../api/types';
import { useAuth } from '../auth/AuthContext';
import { Button, Card, Field, inputClass } from '../components/ui';
import { useToast } from '../components/Toast';

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const { showToast } = useToast();
  const [form, setForm] = useState({ first_name: user?.first_name ?? '', last_name: user?.last_name ?? '', phone_number: user?.phone_number ?? '' });

  const saveProfile = useMutation({
    mutationFn: async () => client.patch('/users/me/', form),
    onSuccess: async () => {
      await refreshUser();
      showToast('Profile updated.', 'success');
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div className="max-w-2xl space-y-10">
      <div>
        <h1 className="font-serif text-3xl mb-6">Profile</h1>
        <Card>
          <div className="grid grid-cols-2 gap-3">
            <Field label="First name">
              <input className={inputClass} value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            </Field>
            <Field label="Last name">
              <input className={inputClass} value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            </Field>
          </div>
          <Field label="Phone number">
            <input className={inputClass} value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
          </Field>
          <Field label="Email">
            <input className={`${inputClass} bg-parchment-100`} value={user?.email} disabled />
          </Field>
          <Button onClick={() => saveProfile.mutate()} disabled={saveProfile.isPending}>
            {saveProfile.isPending ? 'Saving…' : 'Save profile'}
          </Button>
        </Card>
      </div>

      <InterestsSection />
    </div>
  );
}

function InterestsSection() {
  const qc = useQueryClient();
  const { showToast } = useToast();
  const [genreId, setGenreId] = useState('');
  const [authorId, setAuthorId] = useState('');

  const { data: interestsPage } = useQuery({
    queryKey: ['interests'],
    queryFn: async () => (await client.get<Paginated<MemberInterest>>('/users/me/interests/')).data,
  });
  const interests = interestsPage?.results ?? [];
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

  const addInterest = useMutation({
    mutationFn: async (payload: { genre?: number; author?: number }) => client.post('/users/me/interests/', payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['interests'] });
      setGenreId('');
      setAuthorId('');
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  const removeInterest = useMutation({
    mutationFn: async (id: number) => client.delete(`/users/me/interests/${id}/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['interests'] }),
  });

  return (
    <div>
      <h2 className="font-serif text-2xl mb-4">My Interests</h2>
      <p className="text-sm text-ink-700 mb-4">
        Tell us what you like and we'll tailor your recommendations.
      </p>
      <Card>
        <div className="flex flex-wrap gap-2 mb-4">
          {interests.map((i) => (
            <span key={i.id} className="inline-flex items-center gap-2 bg-parchment-200 border border-parchment-300 rounded-full px-3 py-1 text-sm">
              {i.genre_name ?? i.author_name}
              <button onClick={() => removeInterest.mutate(i.id)} aria-label="Remove interest" className="text-ink-700 hover:text-red-700">×</button>
            </span>
          ))}
          {interests.length === 0 && <p className="text-sm text-ink-700">No interests added yet.</p>}
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="flex gap-2">
            <select className={inputClass} value={genreId} onChange={(e) => setGenreId(e.target.value)}>
              <option value="">Add a genre…</option>
              {genreList.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
            </select>
            <Button
              variant="secondary"
              disabled={!genreId}
              onClick={() => addInterest.mutate({ genre: Number(genreId) })}
            >
              Add
            </Button>
          </div>
          <div className="flex gap-2">
            <select className={inputClass} value={authorId} onChange={(e) => setAuthorId(e.target.value)}>
              <option value="">Add an author…</option>
              {authorList.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
            <Button
              variant="secondary"
              disabled={!authorId}
              onClick={() => addInterest.mutate({ author: Number(authorId) })}
            >
              Add
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
