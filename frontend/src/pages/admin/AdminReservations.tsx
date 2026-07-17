import { useQuery } from '@tanstack/react-query';
import { client } from '../../api/client';
import type { Paginated, Reservation } from '../../api/types';
import { Card, EmptyState, StatusBadge } from '../../components/ui';

export default function AdminReservations() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'reservations'],
    queryFn: async () => (await client.get<Paginated<Reservation>>('/reservations/')).data,
  });

  const grouped = (data?.results ?? []).reduce<Record<string, Reservation[]>>((acc, r) => {
    acc[r.book_detail.title] = acc[r.book_detail.title] ?? [];
    acc[r.book_detail.title].push(r);
    return acc;
  }, {});

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Reservations &amp; Waitlist</h1>
      {isLoading && <p className="text-ink-700">Loading…</p>}
      {data && data.results.length === 0 && <EmptyState title="No reservations" />}
      <div className="space-y-6">
        {Object.entries(grouped).map(([title, reservations]) => (
          <div key={title}>
            <h2 className="font-serif text-lg mb-2">{title}</h2>
            <ul className="space-y-2">
              {reservations
                .slice()
                .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
                .map((r, idx) => (
                  <li key={r.id}>
                    <Card className="flex items-center justify-between">
                      <span className="text-sm">#{idx + 1} — {r.member_email}</span>
                      <StatusBadge status={r.status} />
                    </Card>
                  </li>
                ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
