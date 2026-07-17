import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../../api/client';
import type { LoanRequest, Paginated } from '../../api/types';
import { Button, Card, EmptyState, StatusBadge } from '../../components/ui';
import { useToast } from '../../components/Toast';

export default function AdminLoanRequests() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'loan-requests'],
    queryFn: async () => (await client.get<Paginated<LoanRequest>>('/loan-requests/', { params: { status: 'PENDING' } })).data,
  });

  const approve = useMutation({
    mutationFn: async (id: number) => client.post(`/loan-requests/${id}/approve/`),
    onSuccess: () => {
      showToast('Request approved and copy allocated.', 'success');
      qc.invalidateQueries({ queryKey: ['admin', 'loan-requests'] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  const reject = useMutation({
    mutationFn: async (id: number) => client.post(`/loan-requests/${id}/reject/`, { reason: 'Not available at this time' }),
    onSuccess: () => {
      showToast('Request rejected.', 'success');
      qc.invalidateQueries({ queryKey: ['admin', 'loan-requests'] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Loan Requests</h1>
      {isLoading && <p className="text-ink-700">Loading…</p>}
      {data && data.results.length === 0 && <EmptyState title="No pending requests" />}
      {data && data.results.length > 0 && (
        <ul className="space-y-3">
          {data.results.map((r) => (
            <li key={r.id}>
              <Card className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <p className="font-serif">{r.book_detail.title}</p>
                  <p className="text-sm text-ink-700">{r.member_email} · requested {new Date(r.requested_at).toLocaleDateString()}</p>
                  <p className="text-xs text-ink-700">{r.book_detail.available_copies} of {r.book_detail.total_copies} copies available</p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={r.status} />
                  <Button onClick={() => approve.mutate(r.id)} disabled={approve.isPending}>Approve</Button>
                  <Button variant="danger" onClick={() => reject.mutate(r.id)} disabled={reject.isPending}>Reject</Button>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
