import { useQuery } from '@tanstack/react-query';
import { client } from '../../api/client';
import type { AdminKPIs } from '../../api/types';
import { Card, CardSkeletonGrid } from '../../components/ui';

const LABELS: Record<keyof AdminKPIs, string> = {
  total_books: 'Total books',
  total_copies: 'Total copies',
  available_copies: 'Available copies',
  loaned_books: 'Currently loaned',
  overdue_loans: 'Overdue loans',
  pending_requests: 'Pending requests',
  active_reservations: 'Active reservations',
  total_members: 'Total members',
  outstanding_fines_total: 'Outstanding fines ($)',
};

export default function AdminDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', 'admin', 'kpis'],
    queryFn: async () => (await client.get<AdminKPIs>('/dashboard/admin/kpis/')).data,
  });

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Librarian Dashboard</h1>
      {isLoading || !data ? (
        <CardSkeletonGrid count={9} />
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {(Object.keys(LABELS) as (keyof AdminKPIs)[]).map((key) => (
            <Card key={key} className="text-center">
              <p className="text-3xl font-serif text-forest-700">{data[key]}</p>
              <p className="text-sm text-ink-700 mt-1">{LABELS[key]}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
