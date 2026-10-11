import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Plotly y una dependencia transitiva referencian el global de Node.
  // En el navegador se resuelve al global estándar del runtime.
  define: { global: 'globalThis' },
  server: { host: '127.0.0.1' },
});
