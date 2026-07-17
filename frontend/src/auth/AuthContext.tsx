import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { client, friendlyErrorMessage } from '../api/client';
import type { User } from '../api/types';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; first_name?: string; last_name?: string }) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const { data } = await client.get<User>('/users/me/');
      setUser(data);
    } catch {
      localStorage.removeItem('authToken');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- bootstrapping session from a stored token on mount
    refreshUser();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const { data } = await client.post('/auth/login/', { email, password });
      localStorage.setItem('authToken', data.token);
      setUser(data.user);
    } catch (error) {
      throw new Error(friendlyErrorMessage(error), { cause: error });
    }
  };

  const register = async (payload: { email: string; password: string; first_name?: string; last_name?: string }) => {
    try {
      const { data } = await client.post('/auth/register/', payload);
      localStorage.setItem('authToken', data.token);
      setUser(data.user);
    } catch (error) {
      throw new Error(friendlyErrorMessage(error), { cause: error });
    }
  };

  const logout = async () => {
    try {
      await client.post('/auth/logout/');
    } catch {
      // token may already be invalid — proceed with local logout regardless
    }
    localStorage.removeItem('authToken');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
