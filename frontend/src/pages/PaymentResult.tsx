import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { client } from '../api/client';
import type { Payment } from '../api/types';
import { Card } from '../components/ui';

export default function PaymentResult() {
  const { paymentId } = useParams();
  const { data: payment, isLoading } = useQuery({
    queryKey: ['payment', paymentId],
    queryFn: async () => (await client.get<Payment>(`/payments/${paymentId}/`)).data,
  });

  if (isLoading || !payment) return <p className="text-center py-16 text-ink-700">Loading…</p>;

  const succeeded = payment.status === 'SUCCEEDED';

  return (
    <div className="max-w-sm mx-auto text-center">
      <Card>
        <p className={`text-5xl mb-4 ${succeeded ? 'text-forest-700' : 'text-red-700'}`}>
          {succeeded ? '✓' : '✕'}
        </p>
        <h1 className="font-serif text-2xl mb-2">
          {succeeded ? 'Payment successful' : 'Payment failed'}
        </h1>
        <p className="text-ink-700 mb-6">
          {succeeded
            ? `Your payment of $${payment.amount} was received.`
            : 'Your payment could not be processed. Your fine remains unpaid and you can try again.'}
        </p>
        <div className="flex justify-center gap-3">
          {succeeded && (
            <Link to={`/pay/receipt/${payment.id}`} className="px-4 py-2 rounded-md bg-forest-700 text-parchment-50 font-semibold text-sm">
              View receipt
            </Link>
          )}
          <Link to="/fines" className="px-4 py-2 rounded-md bg-parchment-200 border border-parchment-300 text-ink-800 font-semibold text-sm">
            Back to fines
          </Link>
        </div>
      </Card>
    </div>
  );
}
