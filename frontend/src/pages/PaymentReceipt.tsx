import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { client } from '../api/client';
import type { Payment } from '../api/types';
import { Card, EmptyState } from '../components/ui';

export default function PaymentReceipt() {
  const { paymentId } = useParams();
  const { data: payment, isLoading, isError } = useQuery({
    queryKey: ['payment', paymentId, 'receipt'],
    queryFn: async () => (await client.get<Payment>(`/payments/${paymentId}/receipt/`)).data,
  });

  if (isLoading) return <p className="text-center py-16 text-ink-700">Loading…</p>;
  if (isError || !payment) return <EmptyState title="Receipt unavailable" hint="Only successful payments have a receipt." />;

  return (
    <div className="max-w-md mx-auto">
      <h1 className="font-serif text-2xl text-center mb-6">Receipt</h1>
      <Card>
        <dl className="grid grid-cols-2 gap-y-2 text-sm">
          <dt className="font-semibold">Receipt for</dt><dd>{payment.fine_reason}</dd>
          <dt className="font-semibold">Amount</dt><dd>${payment.amount}</dd>
          <dt className="font-semibold">Status</dt><dd>{payment.status}</dd>
          <dt className="font-semibold">Session ID</dt><dd className="break-all">{payment.session_id}</dd>
          <dt className="font-semibold">Date</dt><dd>{new Date(payment.updated_at).toLocaleString()}</dd>
        </dl>
        <div className="mt-4 pt-4 border-t border-parchment-300">
          <p className="text-xs font-semibold text-ink-700 mb-2">Audit trail</p>
          <ul className="text-xs text-ink-700 space-y-1">
            {payment.events.map((e) => (
              <li key={e.id}>{new Date(e.created_at).toLocaleString()} — {e.event_type}</li>
            ))}
          </ul>
        </div>
      </Card>
    </div>
  );
}
