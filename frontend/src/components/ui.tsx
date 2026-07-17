import type { ReactNode } from 'react';

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="text-center py-16 border border-dashed border-parchment-300 rounded-lg bg-parchment-50">
      <p className="font-serif text-lg text-ink-800">{title}</p>
      {hint && <p className="text-sm text-ink-700 mt-1">{hint}</p>}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div role="alert" className="text-center py-10 border border-red-300 bg-red-50 rounded-lg text-red-800">
      {message}
    </div>
  );
}

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`skeleton ${className}`} />;
}

export function CardSkeletonGrid({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      ))}
    </div>
  );
}

const STATUS_STYLES: Record<string, string> = {
  AVAILABLE: 'bg-forest-700 text-parchment-50',
  ACTIVE: 'bg-forest-700 text-parchment-50',
  APPROVED: 'bg-forest-700 text-parchment-50',
  READY: 'bg-forest-700 text-parchment-50',
  PAID: 'bg-forest-700 text-parchment-50',
  SUCCEEDED: 'bg-forest-700 text-parchment-50',
  PENDING: 'bg-brass-500 text-ink-900',
  WAITING: 'bg-brass-500 text-ink-900',
  PENDING_PAYMENT: 'bg-brass-500 text-ink-900',
  ON_LOAN: 'bg-brass-500 text-ink-900',
  HELD: 'bg-brass-500 text-ink-900',
  OVERDUE: 'bg-red-700 text-parchment-50',
  UNPAID: 'bg-red-700 text-parchment-50',
  FAILED: 'bg-red-700 text-parchment-50',
  REJECTED: 'bg-red-700 text-parchment-50',
  LOST: 'bg-red-700 text-parchment-50',
  DAMAGED: 'bg-red-700 text-parchment-50',
  CANCELLED: 'bg-ink-700 text-parchment-50',
  RETURNED: 'bg-ink-700 text-parchment-50',
  EXPIRED: 'bg-ink-700 text-parchment-50',
  FULFILLED: 'bg-ink-700 text-parchment-50',
  ARCHIVED: 'bg-ink-700 text-parchment-50',
  WAIVED: 'bg-ink-700 text-parchment-50',
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-semibold tracking-wide uppercase ${
        STATUS_STYLES[status] ?? 'bg-parchment-200 text-ink-800'
      }`}
    >
      {status.replace('_', ' ')}
    </span>
  );
}

export function StarRating({ rating }: { rating: number | null }) {
  if (rating === null) {
    return <span className="text-sm text-ink-700">No ratings yet</span>;
  }
  const rounded = Math.round(rating);
  return (
    <span aria-label={`${rating.toFixed(1)} out of 5 stars`} className="text-brass-600">
      {'★'.repeat(rounded)}
      <span className="text-parchment-300">{'★'.repeat(5 - rounded)}</span>
      <span className="text-ink-700 text-sm ml-1">({rating.toFixed(1)})</span>
    </span>
  );
}

export function Button({
  children,
  variant = 'primary',
  className = '',
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'danger' }) {
  const styles = {
    primary: 'bg-forest-700 text-parchment-50 hover:bg-forest-800 disabled:bg-forest-700/50',
    secondary: 'bg-parchment-200 text-ink-800 hover:bg-parchment-300 border border-parchment-300',
    danger: 'bg-red-700 text-parchment-50 hover:bg-red-800 disabled:bg-red-700/50',
  }[variant];
  return (
    <button
      className={`px-4 py-2 rounded-md text-sm font-semibold transition-colors disabled:cursor-not-allowed ${styles} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`bg-parchment-50 border border-parchment-300 rounded-lg shadow-book p-5 ${className}`}>
      {children}
    </div>
  );
}

export function Field({
  label, children, error,
}: { label: string; children: ReactNode; error?: string }) {
  return (
    <label className="block mb-4">
      <span className="block text-sm font-semibold text-ink-800 mb-1">{label}</span>
      {children}
      {error && <span className="block text-sm text-red-700 mt-1">{error}</span>}
    </label>
  );
}

export const inputClass =
  'w-full rounded-md border border-parchment-300 bg-white px-3 py-2 text-ink-900 focus:border-forest-600 focus:ring-1 focus:ring-forest-600';

export function Pagination({
  count, next, previous, onNext, onPrevious,
}: { count: number; next: string | null; previous: string | null; onNext: () => void; onPrevious: () => void }) {
  if (!next && !previous) return null;
  return (
    <div className="flex items-center justify-between mt-6">
      <Button variant="secondary" onClick={onPrevious} disabled={!previous}>
        ← Previous
      </Button>
      <span className="text-sm text-ink-700">{count} total</span>
      <Button variant="secondary" onClick={onNext} disabled={!next}>
        Next →
      </Button>
    </div>
  );
}

export function ConfirmDialog({
  open, title, message, onConfirm, onCancel, confirmLabel = 'Confirm', danger = false,
}: {
  open: boolean; title: string; message: string; onConfirm: () => void; onCancel: () => void;
  confirmLabel?: string; danger?: boolean;
}) {
  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      className="fixed inset-0 bg-ink-900/50 flex items-center justify-center z-50 p-4"
      onKeyDown={(e) => e.key === 'Escape' && onCancel()}
    >
      <div className="bg-parchment-50 rounded-lg shadow-book p-6 max-w-sm w-full">
        <h3 id="confirm-dialog-title" className="font-serif text-lg mb-2">{title}</h3>
        <p className="text-sm text-ink-700 mb-6">{message}</p>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onCancel}>Cancel</Button>
          <Button variant={danger ? 'danger' : 'primary'} onClick={onConfirm}>{confirmLabel}</Button>
        </div>
      </div>
    </div>
  );
}
