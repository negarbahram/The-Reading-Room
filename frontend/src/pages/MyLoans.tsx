import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../api/client';
import type { Loan, LoanRequest, Paginated } from '../api/types';
import { Button, Card, EmptyState, StatusBadge } from '../components/ui';
import { useToast } from '../components/Toast';

const TABS = ['Active loans', 'Requests', 'History'] as const;

export default function MyLoans() {
  const [tab, setTab] = useState<(typeof TABS)[number]>('Active loans');

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">My Loans</h1>
      <div role="tablist" className="flex gap-1 mb-6 border-b border-parchment-300">
        {TABS.map((t) => (
          <button
            key={t} role="tab" aria-selected={tab === t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-semibold border-b-2 -mb-px ${
              tab === t ? 'border-forest-700 text-forest-800' : 'border-transparent text-ink-700'
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      {tab === 'Active loans' && <ActiveLoans />}
      {tab === 'Requests' && <Requests />}
      {tab === 'History' && <History />}
    </div>
  );
}

function ActiveLoans() {
  const { data, isLoading } = useQuery({
    queryKey: ['loans', 'active'],
    queryFn: async () => (await client.get<Loan[]>('/dashboard/member/active-loans/')).data,
  });
  if (isLoading) return <p className="text-ink-700">Loading…</p>;
  if (!data || data.length === 0) return <EmptyState title="No active loans" hint="Browse the catalog to borrow a book." />;
  return (
    <ul className="space-y-3">
      {data.map((loan) => (
        <li key={loan.id}>
          <Card className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <p className="font-serif">{loan.book_detail.title}</p>
              <p className="text-sm text-ink-700">Due {new Date(loan.due_at).toLocaleDateString()}</p>
            </div>
            <StatusBadge status={loan.status} />
          </Card>
        </li>
      ))}
    </ul>
  );
}

function Requests() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['loan-requests', 'mine'],
    queryFn: async () => (await client.get<Paginated<LoanRequest>>('/loan-requests/')).data,
  });

  const cancel = useMutation({
    mutationFn: async (id: number) => client.post(`/loan-requests/${id}/cancel/`),
    onSuccess: () => {
      showToast('Request cancelled.', 'success');
      qc.invalidateQueries({ queryKey: ['loan-requests', 'mine'] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  if (isLoading) return <p className="text-ink-700">Loading…</p>;
  const results = data?.results ?? [];
  if (results.length === 0) return <EmptyState title="No loan requests" />;
  return (
    <ul className="space-y-3">
      {results.map((r) => (
        <li key={r.id}>
          <Card className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <p className="font-serif">{r.book_detail.title}</p>
              <p className="text-sm text-ink-700">Requested {new Date(r.requested_at).toLocaleDateString()}</p>
              {r.decision_reason && <p className="text-sm text-red-700">{r.decision_reason}</p>}
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={r.status} />
              {r.status === 'PENDING' && (
                <Button variant="secondary" onClick={() => cancel.mutate(r.id)} disabled={cancel.isPending}>
                  Cancel
                </Button>
              )}
            </div>
          </Card>
        </li>
      ))}
    </ul>
  );
}

function History() {
  const { data, isLoading } = useQuery({
    queryKey: ['loans', 'history'],
    queryFn: async () => (await client.get<Paginated<Loan>>('/users/me/history/')).data,
  });
  if (isLoading) return <p className="text-ink-700">Loading…</p>;
  const results = data?.results ?? [];
  if (results.length === 0) return <EmptyState title="No borrowing history yet" />;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left border-b border-parchment-300">
            <th className="py-2 pr-4">Book</th>
            <th className="py-2 pr-4">Borrowed</th>
            <th className="py-2 pr-4">Due</th>
            <th className="py-2 pr-4">Returned</th>
            <th className="py-2 pr-4">Status</th>
          </tr>
        </thead>
        <tbody>
          {results.map((loan) => (
            <tr key={loan.id} className="border-b border-parchment-200">
              <td className="py-2 pr-4 font-serif">{loan.book_detail.title}</td>
              <td className="py-2 pr-4">{new Date(loan.borrowed_at).toLocaleDateString()}</td>
              <td className="py-2 pr-4">{new Date(loan.due_at).toLocaleDateString()}</td>
              <td className="py-2 pr-4">{loan.returned_at ? new Date(loan.returned_at).toLocaleDateString() : '—'}</td>
              <td className="py-2 pr-4"><StatusBadge status={loan.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
