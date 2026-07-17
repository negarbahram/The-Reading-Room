import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { API_BASE, client } from '../../api/client';
import { Button, Card, EmptyState, inputClass } from '../../components/ui';

interface PopularBook { book_id: number; title: string; author: string; loan_count: number }
interface MemberPerf { user_id: number; email: string; total_loans: number; returned_loans: number; on_time_return_rate: number | null }
interface OverdueRow { loan_id: number; member_email: string; book_title: string; due_at: string; days_overdue: number }
interface FineUser { user_id: number; email: string; outstanding_total: number }

async function downloadCsv(url: string, filename: string) {
  const token = localStorage.getItem('authToken');
  const res = await fetch(`${API_BASE}${url}`, { headers: token ? { Authorization: `Token ${token}` } : {} });
  const blob = await res.blob();
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

export default function AdminReports() {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const params = { date_from: dateFrom || undefined, date_to: dateTo || undefined };

  const { data: popular } = useQuery({
    queryKey: ['reports', 'popular', dateFrom, dateTo],
    queryFn: async () => (await client.get<PopularBook[]>('/dashboard/admin/popular-books/', { params })).data,
  });
  const { data: performance } = useQuery({
    queryKey: ['reports', 'performance', dateFrom, dateTo],
    queryFn: async () => (await client.get<MemberPerf[]>('/dashboard/admin/member-performance/', { params })).data,
  });
  const { data: overdue } = useQuery({
    queryKey: ['reports', 'overdue'],
    queryFn: async () => (await client.get<OverdueRow[]>('/dashboard/admin/overdue/')).data,
  });
  const { data: usersWithFines } = useQuery({
    queryKey: ['reports', 'fines-users'],
    queryFn: async () => (await client.get<FineUser[]>('/dashboard/admin/users-with-fines/')).data,
  });

  return (
    <div className="space-y-10">
      <h1 className="font-serif text-3xl">Reports</h1>

      <div className="flex items-end gap-3 flex-wrap">
        <label className="text-sm">
          <span className="block font-semibold mb-1">From</span>
          <input type="date" className={inputClass} value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
        </label>
        <label className="text-sm">
          <span className="block font-semibold mb-1">To</span>
          <input type="date" className={inputClass} value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
        </label>
      </div>

      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-serif text-2xl">Popular books</h2>
          <Button variant="secondary" onClick={() => downloadCsv(`/dashboard/admin/popular-books/?format=csv&date_from=${dateFrom}&date_to=${dateTo}`, 'popular_books.csv')}>
            Export CSV
          </Button>
        </div>
        {!popular?.length ? <EmptyState title="No loan activity in range" /> : (
          <Card>
            <table className="w-full text-sm">
              <thead><tr className="text-left border-b border-parchment-300"><th className="py-1">Title</th><th>Author</th><th>Loans</th></tr></thead>
              <tbody>
                {popular.map((b) => (
                  <tr key={b.book_id} className="border-b border-parchment-200">
                    <td className="py-1 font-serif">{b.title}</td><td>{b.author}</td><td>{b.loan_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </section>

      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-serif text-2xl">Member performance</h2>
          <Button variant="secondary" onClick={() => downloadCsv(`/dashboard/admin/member-performance/?format=csv&date_from=${dateFrom}&date_to=${dateTo}`, 'member_performance.csv')}>
            Export CSV
          </Button>
        </div>
        {!performance?.length ? <EmptyState title="No member activity in range" /> : (
          <Card>
            <table className="w-full text-sm">
              <thead><tr className="text-left border-b border-parchment-300"><th className="py-1">Member</th><th>Total loans</th><th>Returned</th><th>On-time rate</th></tr></thead>
              <tbody>
                {performance.map((m) => (
                  <tr key={m.user_id} className="border-b border-parchment-200">
                    <td className="py-1">{m.email}</td><td>{m.total_loans}</td><td>{m.returned_loans}</td>
                    <td>{m.on_time_return_rate !== null ? `${Math.round(m.on_time_return_rate * 100)}%` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </section>

      <section>
        <h2 className="font-serif text-2xl mb-3">Overdue activity</h2>
        {!overdue?.length ? <EmptyState title="Nothing overdue" /> : (
          <Card>
            <table className="w-full text-sm">
              <thead><tr className="text-left border-b border-parchment-300"><th className="py-1">Member</th><th>Book</th><th>Due</th><th>Days overdue</th></tr></thead>
              <tbody>
                {overdue.map((o) => (
                  <tr key={o.loan_id} className="border-b border-parchment-200">
                    <td className="py-1">{o.member_email}</td><td>{o.book_title}</td>
                    <td>{new Date(o.due_at).toLocaleDateString()}</td><td>{o.days_overdue}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </section>

      <section>
        <h2 className="font-serif text-2xl mb-3">Users with fines</h2>
        {!usersWithFines?.length ? <EmptyState title="No outstanding fines" /> : (
          <Card>
            <table className="w-full text-sm">
              <thead><tr className="text-left border-b border-parchment-300"><th className="py-1">Member</th><th>Outstanding total</th></tr></thead>
              <tbody>
                {usersWithFines.map((u) => (
                  <tr key={u.user_id} className="border-b border-parchment-200">
                    <td className="py-1">{u.email}</td><td>${u.outstanding_total}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </section>
    </div>
  );
}
