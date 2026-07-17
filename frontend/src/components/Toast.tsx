import { createContext, useCallback, useContext, useState, type ReactNode } from 'react';

interface Toast {
  id: number;
  message: string;
  variant: 'success' | 'error' | 'info';
}

interface ToastContextValue {
  showToast: (message: string, variant?: Toast['variant']) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, variant: Toast['variant'] = 'info') => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, variant }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div
        aria-live="polite"
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-80 max-w-[90vw]"
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`rounded-md border px-4 py-3 shadow-book text-sm font-medium animate-[fadeIn_0.2s_ease-out] ${
              t.variant === 'success'
                ? 'bg-forest-700 text-parchment-50 border-forest-800'
                : t.variant === 'error'
                  ? 'bg-red-800 text-parchment-50 border-red-900'
                  : 'bg-ink-800 text-parchment-50 border-ink-900'
            }`}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}
