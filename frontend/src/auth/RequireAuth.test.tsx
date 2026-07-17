import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { RequireAuth } from './RequireAuth';
import * as AuthContextModule from './AuthContext';

function renderWithAuth(user: unknown, loading = false, adminOnly = false) {
  vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
    user: user as never, loading, login: vi.fn(), register: vi.fn(), logout: vi.fn(), refreshUser: vi.fn(),
  });
  return render(
    <MemoryRouter initialEntries={['/protected']}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/dashboard" element={<div>Dashboard page</div>} />
        <Route
          path="/protected"
          element={<RequireAuth adminOnly={adminOnly}><div>Protected content</div></RequireAuth>}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe('RequireAuth', () => {
  it('redirects anonymous users to the login page', () => {
    renderWithAuth(null);
    expect(screen.getByText('Login page')).toBeInTheDocument();
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument();
  });

  it('renders protected content for an authenticated member', () => {
    renderWithAuth({ id: 1, role: 'MEMBER' });
    expect(screen.getByText('Protected content')).toBeInTheDocument();
  });

  it('redirects a non-admin member away from an admin-only route', () => {
    renderWithAuth({ id: 1, role: 'MEMBER' }, false, true);
    expect(screen.getByText('Dashboard page')).toBeInTheDocument();
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument();
  });

  it('renders protected content for an admin on an admin-only route', () => {
    renderWithAuth({ id: 1, role: 'ADMIN' }, false, true);
    expect(screen.getByText('Protected content')).toBeInTheDocument();
  });

  it('shows a loading state while auth is resolving', () => {
    renderWithAuth(null, true);
    expect(screen.getByText('Loading…')).toBeInTheDocument();
  });
});
