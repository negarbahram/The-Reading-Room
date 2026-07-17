import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../api/client';
import type { Payment } from '../api/types';
import { Button, Card } from '../components/ui';
import { useToast } from '../components/Toast';

/** Mock payment page — stands in for a real provider's hosted checkout.
 * No card data is collected or stored; this only demonstrates the
 * checkout-session → confirm → reconciliation flow end to end. */
export default function PaymentCheckout() {
  const { fineId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [payment, setPayment] = useState<Payment | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    client.post<Payment>('/payments/checkout/', { fine: Number(fineId) })
      .then((res) => setPayment(res.data))
      .catch((err) => setError(friendlyErrorMessage(err)));
  }, [fineId]);

  const confirm = useMutation({
    mutationFn: async (outcome: 'success' | 'fail') =>
      client.post<Payment>(`/payments/${payment!.id}/confirm/`, { outcome }),
    onSuccess: (res) => navigate(`/pay/result/${res.data.id}`, { replace: true }),
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  if (error) return <p role="alert" className="text-red-700 text-center py-16">{error}</p>;
  if (!payment) return <p className="text-center py-16 text-ink-700">Preparing checkout…</p>;

  return (
    <div className="max-w-sm mx-auto">
      <h1 className="font-serif text-2xl text-center mb-6">Mock Checkout</h1>
      <Card>
        <p className="text-sm text-ink-700 mb-1">You are paying a library fine for</p>
        <p className="font-serif text-lg mb-4">{payment.fine_reason}</p>
        <p className="text-3xl font-serif text-forest-700 mb-6">${payment.amount}</p>
        <p className="text-xs text-ink-700 mb-6">
          This is a simulated payment screen for demonstration purposes. No real card
          information is collected or stored.
        </p>
        <div className="flex flex-col gap-2">
          <Button onClick={() => confirm.mutate('success')} disabled={confirm.isPending}>
            {confirm.isPending ? 'Processing…' : 'Simulate successful payment'}
          </Button>
          <Button variant="danger" onClick={() => confirm.mutate('fail')} disabled={confirm.isPending}>
            Simulate failed payment
          </Button>
        </div>
      </Card>
    </div>
  );
}
