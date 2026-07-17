import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { Button, Card, Field, inputClass } from '../components/ui';
import { useToast } from '../components/Toast';

export default function Register() {
  const { register } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '', first_name: '', last_name: '' });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await register(form);
      showToast('Welcome to The Reading Room!', 'success');
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto">
      <h1 className="font-serif text-3xl text-center mb-6">Become a member</h1>
      <Card>
        <form onSubmit={handleSubmit} noValidate>
          <div className="grid grid-cols-2 gap-3">
            <Field label="First name">
              <input className={inputClass} value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            </Field>
            <Field label="Last name">
              <input className={inputClass} value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            </Field>
          </div>
          <Field label="Email">
            <input type="email" required autoComplete="email" className={inputClass}
              value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </Field>
          <Field label="Password">
            <input type="password" required autoComplete="new-password" className={inputClass}
              value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </Field>
          {error && <p role="alert" className="text-sm text-red-700 mb-4">{error}</p>}
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Creating account…' : 'Register'}
          </Button>
        </form>
      </Card>
      <p className="text-center text-sm text-ink-700 mt-4">
        Already a member? <Link to="/login" className="text-forest-700 font-semibold underline">Log in</Link>
      </p>
    </div>
  );
}
