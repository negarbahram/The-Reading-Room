import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Fail loudly instead of silently moving to 5174+ if 5173 is taken —
    // a silent port change breaks CORS since the backend only allows
    // http://localhost:5173 / 127.0.0.1:5173 as origins.
    port: 5173,
    strictPort: true,
  },
})
