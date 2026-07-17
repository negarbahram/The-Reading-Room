import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { client, friendlyErrorMessage } from '../../api/client';
import type { AdminUser, Paginated } from '../../api/types';
import { Button, StatusBadge, inputClass } from '../../components/ui';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../auth/AuthContext';

export default function AdminMembers() {
  const { user: me } = useAuth();
  const { showToast } = useToast();
  const qc = useQueryClient();
  const [search, setSearch] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'members', search],
    queryFn: async () => (await client.get<Paginated<AdminUser>>('/users/', { params: { search } })).data,
  });

  const updateUser = useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: Partial<AdminUser> }) =>
      client.patch(`/users/${id}/`, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'members'] }),
    onError: (err) => showToast(friendlyErrorMessage(err), 'error'),
  });

  return (
    <div>
      <h1 className="font-serif text-3xl mb-6">Members</h1>
      <input className={`${inputClass} max-w-xs mb-4`} placeholder="Search by name or email…"
        value={search} onChange={(e) => setSearch(e.target.value)} />
      {isLoading && <p className="text-ink-700">Loading…</p>}
      {data && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-parchment-300">
                <th className="py-2 pr-4">Name</th>
                <th className="py-2 pr-4">Email</th>
                <th className="py-2 pr-4">Role</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2 pr-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((u) => (
                <tr key={u.id} className="border-b border-parchment-200">
                  <td className="py-2 pr-4">{u.first_name} {u.last_name}</td>
                  <td className="py-2 pr-4">{u.email}</td>
                  <td className="py-2 pr-4">
                    <select
                      className={`${inputClass} !w-auto text-xs py-1`}
                      value={u.role} disabled={u.id === me?.id}
                      onChange={(e) => updateUser.mutate({ id: u.id, payload: { role: e.target.value as 'ADMIN' | 'MEMBER' } })}
                    >
                      <option value="MEMBER">MEMBER</option>
                      <option value="ADMIN">ADMIN</option>
                    </select>
                  </td>
                  <td className="py-2 pr-4">
                    <StatusBadge status={u.is_suspended ? 'UNPAID' : 'AVAILABLE'} />
                    {u.is_suspended ? ' Suspended' : ' Active'}
                  </td>
                  <td className="py-2 pr-4">
                    <Button
                      variant="secondary" className="!px-2 !py-1 text-xs" disabled={u.id === me?.id}
                      onClick={() => updateUser.mutate({ id: u.id, payload: { is_suspended: !u.is_suspended } })}
                    >
                      {u.is_suspended ? 'Unsuspend' : 'Suspend'}
                    </Button>
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
