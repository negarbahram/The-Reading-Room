import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { Button, Card, Field, inputClass } from '../components/ui';
import { useToast } from '../components/Toast';

export default function Login() {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const from = (location.state as { from?: Location })?.from?.pathname ?? '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(email, password);
      showToast('Welcome back!', 'success');
      navigate(from, { replace: true });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto">
      <h1 className="font-serif text-3xl text-center mb-6">Log in</h1>
      <Card>
        <form onSubmit={handleSubmit} noValidate>
          <Field label="Email">
            <input
              type="email" required autoComplete="email" className={inputClass}
              value={email} onChange={(e) => setEmail(e.target.value)}
            />
          </Field>
          <Field label="Password">
            <input
              type="password" required autoComplete="current-password" className={inputClass}
              value={password} onChange={(e) => setPassword(e.target.value)}
            />
          </Field>
          {error && <p role="alert" className="text-sm text-red-700 mb-4">{error}</p>}
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Logging in…' : 'Log in'}
          </Button>
        </form>
      </Card>
      <p className="text-center text-sm text-ink-700 mt-4">
        No account? <Link to="/register" className="text-forest-700 font-semibold underline">Register</Link>
      </p>
      <p className="text-center text-xs text-ink-700 mt-6">
        Demo admin: admin@library.com / AdminPass123<br />
        Demo member: member1@library.com / MemberPass123
      </p>
    </div>
  );
}
