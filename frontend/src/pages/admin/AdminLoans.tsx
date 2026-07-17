import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../../api/client';
import type { Loan, Paginated } from '../../api/types';
import { Button, EmptyState, StatusBadge, inputClass } from '../../components/ui';
import { useToast } from '../../components/Toast';

export default function AdminLoans() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const [status, setStatus] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'loans', status],
    queryFn: async () => (await client.get<Paginated<Loan>>('/loans/', { params: status ? { status } : {} })).data,
  });

  const returnLoan = useMutation({
    mutationFn: async (id: number) => client.post(`/loans/${id}/return/`),
    onSuccess: () => {
      showToast('Book returned. Inventory and reservations updated.', 'success');
      qc.invalidateQueries({ queryKey: ['admin', 'loans'] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  const markLost = useMutation({
    mutationFn: async (id: number) => client.post(`/loans/${id}/mark_lost/`),
    onSuccess: () => {
      showToast('Loan marked as lost.', 'success');
      qc.invalidateQueries({ queryKey: ['admin', 'loans'] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Active Loans &amp; Returns</h1>
      <select className={`${inputClass} max-w-xs mb-4`} value={status} onChange={(e) => setStatus(e.target.value)}>
        <option value="">All loans</option>
        <option value="ACTIVE">Active</option>
        <option value="OVERDUE">Overdue</option>
        <option value="RETURNED">Returned</option>
        <option value="LOST">Lost</option>
      </select>
      {isLoading && <p className="text-ink-700">Loading…</p>}
      {data && data.results.length === 0 && <EmptyState title="No loans found" />}
      {data && data.results.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-parchment-300">
                <th className="py-2 pr-4">Book</th>
                <th className="py-2 pr-4">Member</th>
                <th className="py-2 pr-4">Due</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2 pr-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((loan) => (
                <tr key={loan.id} className="border-b border-parchment-200">
                  <td className="py-2 pr-4 font-serif">{loan.book_detail.title}</td>
                  <td className="py-2 pr-4">{loan.member_email}</td>
                  <td className="py-2 pr-4">{new Date(loan.due_at).toLocaleDateString()}</td>
                  <td className="py-2 pr-4"><StatusBadge status={loan.status} /></td>
                  <td className="py-2 pr-4 flex gap-2">
                    {(loan.status === 'ACTIVE' || loan.status === 'OVERDUE') && (
                      <>
                        <Button className="!px-2 !py-1 text-xs" onClick={() => returnLoan.mutate(loan.id)} disabled={returnLoan.isPending}>
                          Return
                        </Button>
                        <Button variant="danger" className="!px-2 !py-1 text-xs" onClick={() => markLost.mutate(loan.id)} disabled={markLost.isPending}>
                          Mark lost
                        </Button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
