import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../../api/client';
import type { Fine, Paginated } from '../../api/types';
import { Button, EmptyState, StatusBadge } from '../../components/ui';
import { useToast } from '../../components/Toast';

export default function AdminFines() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const [reasonById, setReasonById] = useState<Record<number, string>>({});

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'fines'],
    queryFn: async () => (await client.get<Paginated<Fine>>('/fines/')).data,
  });

  const waive = useMutation({
    mutationFn: async (id: number) => client.post(`/fines/${id}/adjust/`, {
      action: 'waive', reason: reasonById[id] || 'Waived by administrator',
    }),
    onSuccess: () => {
      showToast('Fine waived.', 'success');
      qc.invalidateQueries({ queryKey: ['admin', 'fines'] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Fines &amp; Payments</h1>
      {isLoading && <p className="text-ink-700">Loading…</p>}
      {data && data.results.length === 0 && <EmptyState title="No fines on record" />}
      {data && data.results.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-parchment-300">
                <th className="py-2 pr-4">Member</th>
                <th className="py-2 pr-4">Book</th>
                <th className="py-2 pr-4">Amount</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2 pr-4">Waive reason</th>
                <th className="py-2 pr-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((fine) => (
                <tr key={fine.id} className="border-b border-parchment-200">
                  <td className="py-2 pr-4">{fine.member_email}</td>
                  <td className="py-2 pr-4 font-serif">{fine.book_title}</td>
                  <td className="py-2 pr-4">${fine.amount}</td>
                  <td className="py-2 pr-4"><StatusBadge status={fine.status} /></td>
                  <td className="py-2 pr-4">
                    {(fine.status === 'UNPAID' || fine.status === 'PENDING_PAYMENT') && (
                      <input
                        className="border border-parchment-300 rounded px-2 py-1 text-xs w-40"
                        placeholder="Reason"
                        value={reasonById[fine.id] ?? ''}
                        onChange={(e) => setReasonById((prev) => ({ ...prev, [fine.id]: e.target.value }))}
                      />
                    )}
                  </td>
                  <td className="py-2 pr-4">
                    {(fine.status === 'UNPAID' || fine.status === 'PENDING_PAYMENT') && (
                      <Button variant="secondary" className="!px-2 !py-1 text-xs" onClick={() => waive.mutate(fine.id)} disabled={waive.isPending}>
                        Waive
                      </Button>
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
