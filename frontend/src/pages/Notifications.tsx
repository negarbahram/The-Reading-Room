import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client } from '../api/client';
import type { AppNotification, NotificationPreference, Paginated } from '../api/types';
import { Card, EmptyState } from '../components/ui';

export default function Notifications() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => (await client.get<Paginated<AppNotification>>('/notifications/')).data,
  });
  const { data: prefs } = useQuery({
    queryKey: ['notification-preferences'],
    queryFn: async () => (await client.get<NotificationPreference>('/notifications/preferences/')).data,
  });

  const markRead = useMutation({
    mutationFn: async (id: number) => client.post(`/notifications/${id}/read/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const updatePrefs = useMutation({
    mutationFn: async (payload: Partial<NotificationPreference>) => client.patch('/notifications/preferences/', payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notification-preferences'] }),
  });

  return (
    <div className="grid md:grid-cols-[1fr_260px] gap-8">
      <div>
        <h1 className="font-serif text-3xl mb-6">Notifications</h1>
        {isLoading && <p className="text-ink-700">Loading…</p>}
        {data && data.results.length === 0 && <EmptyState title="No notifications yet" />}
        {data && data.results.length > 0 && (
          <ul className="space-y-2">
            {data.results.map((n) => (
              <li key={n.id}>
                <Card
                  className={`flex items-start justify-between gap-3 ${n.is_read ? 'opacity-60' : ''}`}
                >
                  <div>
                    <p className="text-sm">{n.message}</p>
                    <p className="text-xs text-ink-700 mt-1">{new Date(n.created_at).toLocaleString()}</p>
                  </div>
                  {!n.is_read && (
                    <button
                      onClick={() => markRead.mutate(n.id)}
                      className="text-xs font-semibold text-forest-700 underline shrink-0"
                    >
                      Mark read
                    </button>
                  )}
                </Card>
              </li>
            ))}
          </ul>
        )}
      </div>
      <aside>
        <h2 className="font-serif text-xl mb-4">Preferences</h2>
        <Card className="space-y-3">
          {prefs && (
            <>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={prefs.email_enabled}
                  onChange={(e) => updatePrefs.mutate({ email_enabled: e.target.checked })} />
                Email notifications
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={prefs.sms_enabled}
                  onChange={(e) => updatePrefs.mutate({ sms_enabled: e.target.checked })} />
                SMS notifications
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={prefs.in_app_enabled}
                  onChange={(e) => updatePrefs.mutate({ in_app_enabled: e.target.checked })} />
                In-app notifications
              </label>
            </>
          )}
        </Card>
      </aside>
    </div>
  );
}
