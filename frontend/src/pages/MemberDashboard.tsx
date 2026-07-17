import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { client } from '../api/client';
import type { MemberSummary, RecommendedBook } from '../api/types';
import { Card, CardSkeletonGrid } from '../components/ui';
import { BookCard } from '../components/BookCard';
import { useAuth } from '../auth/AuthContext';

function StatTile({ label, value, to }: { label: string; value: string | number; to?: string }) {
  const inner = (
    <Card className="text-center hover:shadow-lg transition-shadow">
      <p className="text-3xl font-serif text-forest-700">{value}</p>
      <p className="text-sm text-ink-700 mt-1">{label}</p>
    </Card>
  );
  return to ? <Link to={to}>{inner}</Link> : inner;
}

export default function MemberDashboard() {
  const { user } = useAuth();
  const { data: summary, isLoading } = useQuery({
    queryKey: ['dashboard', 'member', 'summary'],
    queryFn: async () => (await client.get<MemberSummary>('/dashboard/member/summary/')).data,
  });
  const { data: recommendations, isLoading: loadingRecs } = useQuery({
    queryKey: ['dashboard', 'member', 'recommendations'],
    queryFn: async () => (await client.get<RecommendedBook[]>('/dashboard/member/recommendations/')).data,
  });

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-serif text-3xl mb-1">Welcome back, {user?.first_name || user?.email}</h1>
        <p className="text-ink-700">Here is what's happening with your account.</p>
      </div>

      {isLoading || !summary ? (
        <CardSkeletonGrid count={6} />
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatTile label="Active loans" value={summary.active_loans} to="/loans" />
          <StatTile label="Overdue" value={summary.overdue_loans} to="/loans" />
          <StatTile label="Pending requests" value={summary.pending_requests} to="/loans" />
          <StatTile label="Reservations" value={summary.active_reservations} to="/reservations" />
          <StatTile label="Outstanding fines" value={`$${summary.outstanding_fines_total}`} to="/fines" />
          <StatTile label="Unread notifications" value={summary.unread_notifications} to="/notifications" />
        </div>
      )}

      <section>
        <h2 className="font-serif text-2xl mb-4">Recommended for you</h2>
        {loadingRecs ? (
          <CardSkeletonGrid />
        ) : recommendations && recommendations.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {recommendations.map((b) => (
              <div key={b.id}>
                <BookCard book={b} />
                <p className="text-xs text-ink-700 mt-1 italic">{b.reason}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-ink-700">Borrow or rate a few books to see personalized picks here.</p>
        )}
      </section>
    </div>
  );
}
