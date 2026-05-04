import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/login-attempt': 'http://localhost:8000',
      '/events': 'http://localhost:8000',
      '/suspicious': 'http://localhost:8000',
      '/stats': 'http://localhost:8000',
    }
  }
})