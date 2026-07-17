import axios, { AxiosError } from 'axios';

export const API_BASE = 'http://localhost:8000/api/v1';

export const client = axios.create({
  baseURL: API_BASE,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export interface ApiErrorShape {
  detail: string;
  errors: Record<string, string[]> | string[] | null;
}

/** Never surface raw backend errors to users — always route through this. */
export function friendlyErrorMessage(error: unknown): string {
  const axiosError = error as AxiosError<ApiErrorShape>;
  if (axiosError?.response?.data) {
    const data = axiosError.response.data;
    if (typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string') {
      if (data.errors && typeof data.errors === 'object' && !Array.isArray(data.errors)) {
        const firstField = Object.keys(data.errors)[0];
        const firstMessage = (data.errors as Record<string, string[]>)[firstField]?.[0];
        if (firstMessage) return firstMessage;
      }
      if (Array.isArray(data.errors) && data.errors.length) {
        return String(data.errors[0]);
      }
      return data.detail;
    }
  }
  if (axiosError?.response?.status === 401) return 'Please log in to continue.';
  if (axiosError?.response?.status === 403) return 'You do not have permission to do that.';
  if (axiosError?.message === 'Network Error') return 'Cannot reach the server. Please try again.';
  return 'Something went wrong. Please try again.';
}
