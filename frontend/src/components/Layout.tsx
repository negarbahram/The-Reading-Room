import { type ReactNode } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

function NavItem({ to, children }: { to: string; children: ReactNode }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
          isActive ? 'bg-forest-800 text-parchment-50' : 'text-parchment-100 hover:bg-forest-700'
        }`
      }
    >
      {children}
    </NavLink>
  );
}

export function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-forest-800 shadow-md">
        <nav className="max-w-6xl mx-auto flex items-center justify-between px-4 py-3 flex-wrap gap-2">
          <Link to="/" className="font-serif text-xl text-parchment-50 tracking-wide">
            The Reading Room
          </Link>
          <div className="flex items-center gap-1 flex-wrap">
            <NavItem to="/catalog">Catalog</NavItem>
            {user && <NavItem to="/dashboard">Dashboard</NavItem>}
            {user && <NavItem to="/loans">My Loans</NavItem>}
            {user && <NavItem to="/reservations">Reservations</NavItem>}
            {user && <NavItem to="/fines">Fines</NavItem>}
            {user && <NavItem to="/notifications">Notifications</NavItem>}
            {user?.role === 'ADMIN' && <NavItem to="/admin">Admin</NavItem>}
            {user ? (
              <>
                <NavItem to="/profile">Profile</NavItem>
                <button
                  onClick={handleLogout}
                  className="px-3 py-2 rounded-md text-sm font-medium text-parchment-100 hover:bg-forest-700"
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <NavItem to="/login">Log in</NavItem>
                <NavItem to="/register">Register</NavItem>
              </>
            )}
          </div>
        </nav>
        <div className="shelf-divider" />
      </header>
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">{children}</main>
      <footer className="bg-walnut-800 text-parchment-200 text-center text-sm py-6 mt-8">
        The Reading Room — Online Library Management System (university project)
      </footer>
    </div>
  );
}
