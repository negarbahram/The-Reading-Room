import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../../api/client';
import type { Paginated, Review } from '../../api/types';
import { Button, Card, EmptyState, StarRating, StatusBadge } from '../../components/ui';
import { useToast } from '../../components/Toast';

export default function AdminReviewModeration() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'reviews'],
    queryFn: async () => (await client.get<Paginated<Review>>('/reviews/')).data,
  });

  const moderate = useMutation({
    mutationFn: async ({ id, is_approved }: { id: number; is_approved: boolean }) =>
      client.post(`/reviews/${id}/moderate/`, { is_approved }),
    onSuccess: () => {
      showToast('Review updated.', 'success');
      qc.invalidateQueries({ queryKey: ['admin', 'reviews'] });
    },
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Review Moderation</h1>
      {isLoading && <p className="text-ink-700">Loading…</p>}
      {data && data.results.length === 0 && <EmptyState title="No reviews yet" />}
      <ul className="space-y-3">
        {data?.results.map((r) => (
          <li key={r.id}>
            <Card className="flex items-center justify-between flex-wrap gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <StarRating rating={r.rating} />
                  <span className="text-xs text-ink-700">{r.member_email}</span>
                  <StatusBadge status={r.is_approved ? 'AVAILABLE' : 'PENDING'} />
                </div>
                {r.comment && <p className="text-sm text-ink-800 mt-1">{r.comment}</p>}
              </div>
              <div className="flex gap-2">
                {!r.is_approved && (
                  <Button className="!px-2 !py-1 text-xs" onClick={() => moderate.mutate({ id: r.id, is_approved: true })}>
                    Approve
                  </Button>
                )}
                {r.is_approved && (
                  <Button variant="danger" className="!px-2 !py-1 text-xs" onClick={() => moderate.mutate({ id: r.id, is_approved: false })}>
                    Hide
                  </Button>
                )}
              </div>
            </Card>
          </li>
        ))}
      </ul>
    </div>
  );
}
