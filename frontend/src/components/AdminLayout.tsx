import { type ReactNode } from 'react';
import { NavLink } from 'react-router-dom';

const LINKS = [
  { to: '/admin', label: 'Dashboard', end: true },
  { to: '/admin/books', label: 'Books' },
  { to: '/admin/members', label: 'Members' },
  { to: '/admin/loan-requests', label: 'Loan Requests' },
  { to: '/admin/loans', label: 'Active Loans' },
  { to: '/admin/reservations', label: 'Reservations' },
  { to: '/admin/fines', label: 'Fines' },
  { to: '/admin/reviews', label: 'Review Moderation' },
  { to: '/admin/reports', label: 'Reports' },
];

export function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-6">
      <aside className="bg-parchment-50 border border-parchment-300 rounded-lg p-3 h-fit">
        <h2 className="font-serif text-lg text-walnut-800 px-2 mb-2">Librarian Console</h2>
        <nav className="flex md:flex-col gap-1 flex-wrap">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium ${
                  isActive ? 'bg-walnut-700 text-parchment-50' : 'text-ink-800 hover:bg-parchment-200'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div>{children}</div>
    </div>
  );
}
