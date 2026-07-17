import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { client } from '../api/client';
import type { Fine, Paginated } from '../api/types';
import { Card, EmptyState, StatusBadge } from '../components/ui';

export default function Fines() {
  const { data, isLoading } = useQuery({
    queryKey: ['fines', 'mine'],
    queryFn: async () => (await client.get<Paginated<Fine>>('/fines/')).data,
  });

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Fines</h1>
      {isLoading && <p className="text-ink-700">Loading…</p>}
      {data && data.results.length === 0 && <EmptyState title="No fines on your account" hint="Nicely done." />}
      {data && data.results.length > 0 && (
        <ul className="space-y-3">
          {data.results.map((fine) => (
            <li key={fine.id}>
              <Card className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <p className="font-serif">{fine.book_title}</p>
                  <p className="text-sm text-ink-700">{fine.reason} · ${fine.amount}</p>
                  {fine.waived_reason && <p className="text-xs text-ink-700">Waived: {fine.waived_reason}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={fine.status} />
                  {(fine.status === 'UNPAID' || fine.status === 'PENDING_PAYMENT') && (
                    <Link
                      to={`/pay/${fine.id}`}
                      className="px-4 py-2 rounded-md bg-forest-700 text-parchment-50 font-semibold text-sm hover:bg-forest-800"
                    >
                      Pay now
                    </Link>
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
