import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../api/client';
import type { Paginated, Reservation } from '../api/types';
import { Button, Card, EmptyState, StatusBadge } from '../components/ui';
import { useToast } from '../components/Toast';

export default function Reservations() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['reservations', 'mine'],
    queryFn: async () => (await client.get<Paginated<Reservation>>('/reservations/')).data,
  });

  const cancel = useMutation({
    mutationFn: async (id: number) => client.post(`/reservations/${id}/cancel/`),
    onSuccess: () => {
      showToast('Reservation cancelled.', 'success');
      qc.invalidateQueries({ queryKey: ['reservations', 'mine'] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Reservations</h1>
      {isLoading && <p className="text-ink-700">Loading…</p>}
      {data && data.results.length === 0 && (
        <EmptyState title="No reservations" hint="When a book is fully checked out, you can join its waitlist from the book page." />
      )}
      {data && data.results.length > 0 && (
        <ul className="space-y-3">
          {data.results.map((r) => (
            <li key={r.id}>
              <Card className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <p className="font-serif">{r.book_detail.title}</p>
                  <p className="text-sm text-ink-700">
                    Joined {new Date(r.created_at).toLocaleDateString()}
                    {r.expires_at && ` · Hold expires ${new Date(r.expires_at).toLocaleDateString()}`}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={r.status} />
                  {(r.status === 'WAITING' || r.status === 'READY') && (
                    <Button variant="secondary" onClick={() => cancel.mutate(r.id)} disabled={cancel.isPending}>
                      Cancel
                    </Button>
                  )}
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
